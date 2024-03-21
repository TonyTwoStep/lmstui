'''
LMSworker
(c) 2020 R.S.U. / GPL v3 / https://www.nexus0.net/pub/sw/lmstui
'''

import threading
import queue
import logging, os, time, collections, datetime

from lmstui.lms.server import LMSServer
from lmstui.utils import config

_LOGGER = logging.getLogger(__name__)

class LMSWorker():

	def worker( self, event, q, lms, frame):
		_LOGGER.debug( "LMSWorker:worker enter")
		run_worker = True
		while run_worker:
			#_LOGGER.debug( "LMSWorker:worker enter loop")
			event.wait()
			#_LOGGER.debug( "LMSWorker:worker: run {}".format( run_worker))
			try:
				msg = q.get( block=False)
				_LOGGER.debug( "LMSWorker:worker: msg: {}".format( repr(msg)))
				if msg == "exit":
					run_worker = False
				q.task_done()
			except queue.Empty:
				pass
			if run_worker is True:
				if self._screen._scene_index >= len( self._screen._scenes):
					_LOGGER.warn( "LMSWorker:worker: _scene_index {} > _screen._scenes {}".format( self._screen._scene_index, len( self._screen._scenes)))
					continue
				scene = self._screen._scenes[ self._screen._scene_index]
				if lms.update():
					if scene.name is "Main":
						player = lms.get_current_player()
						if player:
							#frame._uistatus1.value = "{} ({}) @ {}".format( player.get_name(), player.get_player_id(), player.get_ip())
							frame.update_playerinfo( player)
							ti = player.get_track_current_info()
							if ti is not None:
								frame.update_trackinfo( ti)
							pls = player.get_playlist_current()
							if pls is not None:
								frame.update_playlist( pls, player.get_playlist_current_index())
						else:
							frame.show_error( "No player (^p to select)", lms.get_lasterror())
					else:
						pass
						#_LOGGER.debug("worker: not in main")
				else:
					_LOGGER.debug("worker: LMS update fail")
					frame.show_error( "Error: No server connection", lms.get_lasterror())
				frame.force_update()

			time.sleep( config.LMS_POLLINTERVAL)

	def __init__(self, lmsserver, screen, frame):
		self._lms = lmsserver
		self._screen = screen
		self._frame = frame
		self._queue = queue.Queue()
		self._event = threading.Event()
		self._thread = threading.Thread( target=self.worker, daemon=True, args=( self._event, self._queue, self._lms, self._frame))
		_LOGGER.debug( "LMSWorker: init done")

	def start(self):
		_LOGGER.debug( "LMSWorker: start")
		self._thread.start()

	def pause(self):
		_LOGGER.info( "LMSWorker: pause")
		self._event.clear()

	def unpause(self):
		_LOGGER.info( "LMSWorker: unpause")
		self._event.set()

	def control(self, msg):
		self._queue.put( msg)

	def join(self):
		self._thread.join()
