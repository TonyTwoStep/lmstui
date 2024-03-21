'''
LMS server
based on https://github.com/molobrakos/lms
'''

import logging
from requests import Session
from datetime import timedelta
from sys import version_info
import json
from urllib.parse import urlparse, urlunparse, unquote, quote

from lmstui.lms.player import LMSPlayer
from lmstui.utils import config

if version_info < (3, 0):
	exit('Python 3 required')

__version__ = '0.0.1'

_LOGGER = logging.getLogger(__name__)
TIMEOUT = timedelta(seconds=config.LMS_TIMEOUT)


class LMSServer:

	def __init__(self, host=None, port=9000, username=None, password=None):
		self._host = host
		self._port = port
		self._session = Session()
		self._username = username
		self._password = password
		self._state = {}
		self._players = {}
		self._lasterror = None
		if username and password:
			self._session.auth = (username, password)

	def __str__(self):
		return '%s:%d (%s)' % (
			self._host, self._port, self.version) + '\n' + '\n'.join(
				'\t - player: ' + str(p) for p in self.players)

	def query(self, *command, player=''):
		url = 'http://{}:{}/jsonrpc.js'.format(self._host, self._port)
		data = dict(id='1',
					method='slim.request',
					params=[player, command])
		#_LOGGER.debug('URL: %s Data: %s', url, data)
		self._lasterror = None
		try:
			result = self._session.post(
				url, json=data, timeout=TIMEOUT.seconds)
			result.raise_for_status()
			result = result.json()
#			_LOGGER.debug(result)
			return result['result']
		except OSError as e:
			self._lasterror = e
			_LOGGER.warning('Could not query server: {}'.format( e))
			_LOGGER.debug('Data: {}'.format(repr( data)))
			return {}

	def get_lasterror( self):
		return self._lasterror

	def update(self):
		self._state = self.server_status
		if not self._state:
			return False
		if 'players_loop' in self._state:
			self._players = {player['playerid']: LMSPlayer(self, player) for player in self._state['players_loop']}
			self.update_players()
		else:
			self._players = None
		#_LOGGER.debug("LMSserver players: {}".format( repr(self._players)))
		return True

	def update_players(self):
		if self._players is None:
			return False
		for player in self.players:
			player.update()
		return True

	@property
	def _url(self):
		if self._username and self._password:
			return 'http://{username}:{password}@{server}:{port}/'.format(
				username=self._username,
				password=self._password,
				server=self._host,
				port=self._port)
		return 'http://{server}:{port}/'.format(
			server=self._host,
			port=self._port)

	@property
	def version(self):
		return self._state.get('version')

	@property
	def server_status(self):
		return self.query('serverstatus', '-')

	@property
	def players_status(self):
		return self.query('players', 'status')

	@property
	def players(self):
		return self._players.values() if self._players else None

	def get_player(self, player_id):
		return self._players[player_id] if ( self._players and player_id in self._players) else None

	def get_current_player(self):
		if config.LMS_CURRPLAYER is not None:
			return self.get_player( config.LMS_CURRPLAYER)
		if len( self.players) > 0:
			return self.players[0]
		return None

	def is_player_known(self, player_id):
		return player_id in self._players

	def get_playlists(self, start=0, end=config.LMS_MAXLEN):
		pls = self.query('playlists', start, end)
		if pls is not None and 'count' in pls:
			#_LOGGER.debug("LMSserver get_playlists: {}".format( repr(pls)))
			return pls['count'], pls['playlists_loop']
		return None, None

	def get_cover_url( self, coverid):
		return "{}music/{}/cover".format( self._url, coverid)

	def get_favorites( self):
		toplevel = self.query( 'favorites', 'items', 0, config.LMS_MAXLEN)
		if toplevel and 'loop_loop' in toplevel:
			topitems = []
			for i in toplevel[ 'loop_loop']:
				#_LOGGER.debug("get_favorites topitem: {}".format( repr( i)))
				item = i
				item['parent'] = None
				if item['hasitems']:
					sublevel = self.query( 'favorites', 'items', 0, config.LMS_MAXLEN, "item_id:" + item['id'])
					#_LOGGER.debug("get_favorites sublevel: {}".format( repr( sublevel)))
					if sublevel and 'loop_loop' in sublevel:
						children = []
						for subitem in sublevel[ 'loop_loop']:
							#_LOGGER.debug("get_favorites subitem: {}".format( repr( subitem)))
							self._get_subfavs( subitem, children, parent=item['id'])
						if len( children) > 0:
							item['children'] = children
						#else:
						#	item['children'] = None

				topitems.append( item)
			_LOGGER.debug("get_favorites final topitems: {}".format( json.dumps( topitems)))
			return topitems

	def _get_subfavs( self, item, toplevel, parent=None, level=0):
		child = item
		child['parent'] = parent
		if item['hasitems']:
			sub = self.query( 'favorites', 'items', 0, config.LMS_MAXLEN, "item_id:" + item['id'])
			children = []
			for subitem in sub[ 'loop_loop']:
				#_LOGGER.debug("_get_subfavs level:{} subitem: {}".format( level, repr( subitem)))
				self._get_subfavs( subitem, children, parent=item['id'], level=( level + 1))
			if len(children) > 0:
				child['children'] = children
			#else:
			#	item['children'] = None
		toplevel.append( child)

	def getSonginfoForPath(self, file, tags='ud'):
		url = urlunparse( ('file', '', quote( file), '', '', ''))
		return self.query('songinfo', 0, 1, 'url:{url} tags:{tags}'.format(url=url, tags=tags))
