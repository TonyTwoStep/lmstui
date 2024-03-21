'''
LMS player
based on https://github.com/molobrakos/lms
'''

from urllib.parse import urlparse, urlunparse, unquote, quote
import logging
#from lms.server import LMSServer
from lmstui.utils import config

__version__ = '0.0.1'

_LOGGER = logging.getLogger(__name__)

class LMSPlayer:

	def __init__(self, server, player):
		self._server = server
		self._state = player
		self._oldstate = None
		self._oldstatus = None

	def __str__(self):

		return '%s [%s] @ %s' % ( self.get_name(), self.get_player_id(), self.get_ip())

	def get_player_id(self):
		return self._state['playerid']

	def get_name(self):
		return self._state['name']

	def get_ip(self):
		return self._state.get('player_ip')

	def get_mode(self):
		return self._state.get('mode')

	def is_playing(self):
		return self.get_mode() == 'play'

	def is_stopped(self):
		return self.get_mode() == 'stop'

	def is_paused(self):
		return self.get_mode() == 'pause'

	def is_shuffle(self):
		return self._state.get('playlist_shuffle') == 1

	def is_power( self):
		return self._state['power'] == 1

	def is_connected( self):
		return self._state['player_connected'] == 1

	def is_repeat( self):
		return self._state['playlist repeat'] == 1

	def is_statechanged(self):
		pass

	def is_player_status_changed( self):
		if (( self._state is None or self._oldstate is None)
				or (self._state['power'] and (self._state['power'] is not self._oldstate['power']))
				or (self._state['mode'] and self._state['mode'] is not self._oldstate['mode'])  # play/paus mode
				or (self._state['playlist_timestamp'] and self._state['playlist_timestamp'] > self._oldstate['playlist_timestamp'])  # playlist: time of last change
				or (self._state['playlist_cur_index'] and self._state['playlist_cur_index'] is not self._oldstate['playlist_cur_index'])   # the currently playing song's position in the playlist
				or (self._state['current_title'] and self._state['current_title'] is not self._oldstate['current_title'])   # title (eg. radio stream)
				or (self._state['playlist_tracks'] > 0 and self._state['playlist_loop'][0].title is not self._oldstate['title'])   # songtitle?
				or (self._state['playlist_tracks'] > 0 and self._state['playlist_loop'][0].url is not self._oldstate['url'])   # track url
				or (self._state['playlist_tracks'] < 1 and self._oldstate['track'])   # there's a player, but no song in the playlist
				or (self._state['playlist_tracks'] > 0 and not self._oldstate['track'])   # track in playlist changed
				or (self._state['rate'] and self._state['rate'] is not self._oldstate['rate'])):  # song is scanning (ffwd/frwd)
			return True
		return False

	def is_playlist_changed( self):
		if ( (self._state['playlist_timestamp'] is None and self._oldstate['playlist_timestamp'] is not None)
				or (self._state['playlist_timestamp'] is not None and self._oldstate['playlist_timestamp'] is None)
				or (self._state['playlist_timestamp'] is not None and self._state['playlist_timestamp'] > self._oldstate['playlist_timestamp'])):
			return True
		return False

	"""
	def _update_state(self, newstate):
		self._oldstate = self._state
		self._oldstus = self._status
		self._status = []
		has_tracks = True if newstate['playlist_tracks'] > 0 and newstate['playlist_loop'] not None else False

		self._status['power'] = None if newstate['power'] is None else newstate['power']
		self._status['mode'] = newstate['mode']
		self._status['rate'] = newstate['rate']
		self._status['current_title'] = newstate['current_title'] if newstate['current_title'] else None
		self._status['playlist_tracks'] = newstate['playlist_tracks']

		self._status['isPlaying'] = True if newstate['mode'] is "play" else False
		self._status['canSeek'] = True if newstate['can_seek'] else False

		self._status['title'] = newstate['playlist_loop'][0]['title'] if hasTracks else None
		self._status['albumName'] = newstate['playlist_loop'][0]['album'] if hasTracks else None
		self._status['artistName'] = hasTracks ? newstate['playlist_loop'][0]['artist'] : undefined,
		self._status['genreName'] = hasTracks ? newstate['playlist_loop'][0]['genre'] : undefined,
		self._status['year'] = hasTracks ? parseInt(newstate['playlist_loop'][0]['year']) : undefined,
		self._status['bitrate'] = hasTracks ? newstate['playlist_loop'][0]['bitrate'] : undefined,
		self._status['url'] = hasTracks ? newstate['playlist_loop'][0]['url'] : undefined,
		self._status['trackId'] = hasTracks ? newstate['playlist_loop'][0]['id'] : undefined,
		self._status['coverId'] = hasTracks ? newstate['playlist_loop'][0]['coverid'] : undefined,
		self._status['artistId'] = hasTracks ? parseInt(newstate['playlist_loop'][0]['artist_id']) : undefined,
		self._status['rating'] = hasTracks ? parseInt(newstate['playlist_loop'][0]['rating']) : undefined,

		self._status['index'] = parseInt(newstate['playlist_cur_index']),
		self._status['duration'] = parseInt(newstate['duration']) || 0,
		self._status['playtime'] = parseInt(newstate['time']),
		self._status['mixerVolume'] = newstate["mixer volume"],

		self._status['playlist_timestamp'] = newstate['playlist_timestamp'],
		self._status['lastCheck'] = Date.now()
	"""

	def query(self, *params):
		return self._server.query(*params, player=self.get_player_id())

	def update(self):
		tags = "cgAsRbehldrtyrSuKN"
		#tags = 'alu'  # artist, album, url
		response = self.query(
			#'status', '-', '1', 'tags:{tags}'
			'status', 0, config.LMS_MAXLEN, 'tags:{tags}'
			.format(tags=tags))

		if response is False:
			return

		'''
		try:
			self._state.update(response['playlist_loop'][0])
		except KeyError:
			pass

		try:
			self._state.update(response['remoteMeta'])
		except KeyError:
			pass
		'''
		self._state.update(response)

	def get_value( self, key):
		return self._state[ key] if key in self._state else None

	def get_track_id(self):
		return self._state['id']

	def get_track_current_info(self):
		#_LOGGER.debug( "get_track_info: playlist_loop= {}".format( repr(self._state['playlist_loop'][0])))
		if self._state and self._state['playlist_tracks'] > 0 and self._state['playlist_loop']:
			return self._state['playlist_loop'][ self.get_playlist_current_index()]

	def get_playlist_len(self):
		return int( self._state['playlist_tracks'])

	def get_playlist_current(self):
		if "playlist_loop" in self._state:
			return self._state['playlist_loop']
		return None

	def get_playlist_current_index(self):
		if "playlist_cur_index" in self._state:
			return int( self._state['playlist_cur_index'])
		return None

	def get_track(self, idx):
		return self._state['playlist_loop'][idx]

	def get_track_fileurl(self, idx):
#		_LOGGER.debug( "get_track_fileurl: idx= {} plslen={}".format( idx, len(self._state['playlist_loop'])))
		if len(self._state['playlist_loop']) - 1 < idx:
			return None
		return unquote( urlparse( self._state['playlist_loop'][idx]['url']).path)

	def get_volume( self):
		return self._state['mixer volume']

	def get_time( self):
		return int( self._state['time']) if 'time' in self._state else 0

	def get_duration( self):
		return int(self._state['duration']) if 'duration' in self._state else 0

	def display(self, line2, line1="LMSmusly:", duration=3):
		if config.LMS_NOTIFICATIONS:
			response = self.query('display', line1, line2, duration)
			#_LOGGER.debug( "show: response= {}".format( repr(response)))

	def playlist_add( self, file):
		url = urlunparse( ('file', '', quote( file), '', '', ''))
		_LOGGER.debug( "playlist_add: url= {}".format( url))
		response = self.query('playlist', 'add', url)

	def playlist_play_idx( self, idx):
		response = self.query('playlist', 'index', idx)

	def playlist_control( self, cmd, parm):
		response = self.query('playlistcontrol', cmd, parm)

	def playlist_delete_idx( self, idx):
		response = self.query('playlist', 'delete', idx)
#		_LOGGER.debug( "playlist_delete_idx: response= {}".format( repr(response)))

	def play(self):
		return self.query("play")

	def pause(self):
		return self.query('pause 1')

	def unpause(self):
		return self.query('pause 0')

	def toggle(self):
		return self.query('pause')

	def stop(self):
		return self.query("stop")

	def seek_to(self, seconds):
		return self.query("time {}".format(seconds))

	def seek(self, seconds):
		dir = "+" if seconds > 0 else "-"
		return self.query("time", "{}{}".format( dir, abs( seconds)))

	def skip_songs(self, amount):
		if amount > 0:
			amount = "+" + str(amount)
		else:
			amount = str(amount)
		return self.query("playlist", "index", amount)

	def previous_song(self):
		return self.skip_songs( -1)

	def next_song(self):
		return self.skip_songs( 1)

	def skip_album( self, num=1, forward=True):
		if not self.get_playlist_current() and not self.get_playlist_current_index():
			_LOGGER.debug("skip_album: get_playlist_current or get_playlist_current_index failed")
			return False
		pls = self.get_playlist_current()
		albums = 0
		curr_album = pls[ self.get_playlist_current_index()][ 'album'] if 'album' in pls[ self.get_playlist_current_index()] else "-"
		for i, row in ( enumerate( pls[ self.get_playlist_current_index():]) if forward is True else enumerate( pls[ self.get_playlist_current_index(): 0: -1])):
			al = row[ 'album'] if 'album' in row else "-"
			#_LOGGER.debug( "skip_album: album={} index={}".format( al, i))
			if al != curr_album:
				#_LOGGER.debug( "skip_album: old album={} new album={} index={} row={}".format( curr_album, al, i, repr( row)))
				albums += 1
				if albums == num:
					if forward:
						self.playlist_play_idx( row[ 'playlist index'])
					else:
						for j, sr in enumerate( pls[ self.get_playlist_current_index() - i: 0: -1]):
							sal = sr[ 'album'] if 'album' in row else "-"
							#_LOGGER.debug( "skip_album: subalbum={} j={}".format( sal, j))
							if sal != al:
								pos = self.get_playlist_current_index() - i - j + 1
								#_LOGGER.debug( "skip_album: skip idx={} al={}".format( pos, pls[pos]['album']))
								self.playlist_play_idx( pls[ pos][ 'playlist index'])
								break
					break
				curr_album = al
			pass

	def set_volume(self, volume):
		self.query("mixer", "volume", volume)
