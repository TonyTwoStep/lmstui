import logging

from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, Button, TextBox, Widget, MultiColumnListBox
from asciimatics.exceptions import ResizeScreenError, StopApplication, InvalidFields, NextScene
from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen

from lmstui.utils import config

_LOGGER = logging.getLogger(__name__)

class Playlists(Frame,):
	def __init__(self, screen, lms):
		super(Playlists, self).__init__(screen,
										config.APP_DIM_H_L,
										config.APP_DIM_W_M,
										has_shadow=False,
										has_border=True,
										can_scroll=False,
										is_modal=True,
										title="Playlists",
										name="PlaylistFrame")

		opts = []
		self._uiplaylists = ListBox( Widget.FILL_FRAME, opts, centre=False, add_scroll_bar=True, on_select=self._play)
		layout = Layout([100], fill_frame=True)
		self.add_layout(layout)
		layout.add_widget(self._uiplaylists, 0)
		layout.add_widget(Divider(height=1, draw_line=True), 0)

		self._player = lms.get_current_player()

		layout2 = Layout([1, 1, 1, 1])
		self.add_layout(layout2)
		if self._player:
			layout2.add_widget(Button("Load", self._play), 0)
			layout2.add_widget(Button("Add", self._add_end), 1)
			layout2.add_widget(Button("Insert", self._insert), 2)
		layout2.add_widget(Button("Back", self._destroy), 3)

		_, self._pls = lms.get_playlists()
		if self._pls is not None:
			opts = []
			for p in self._pls:
				opts.append( (p['playlist'], p['id']))
			self._uiplaylists.options = opts

		self.set_theme( config.APP_THEME)
		self.fix()

	def _add_end( self):
		self._player.playlist_control( "cmd:add", "playlist_id:" + str(self._uiplaylists.value))
		self._destroy()

	def _insert( self):
		self._player.playlist_control( "cmd:insert", "playlist_id:" + str(self._uiplaylists.value))
		self._destroy()

	def _play( self):
		#_LOGGER.debug( "_play: self._uiplaylists.val= {} ".format( self._uiplaylists.value))
		self._player.playlist_control( "cmd:load", "playlist_id:" + str(self._uiplaylists.value))
		self._destroy()

	def _destroy( self, callback=None):
		self._scene.remove_effect(self)
		if callback is not None:
			callback()

	def process_event(self, event):
		# Look for events that will close the pop-up - e.g. clicking outside the Frame or ESC key.
		if event is not None:
			if isinstance(event, KeyboardEvent):
					if event.key_code == Screen.KEY_ESCAPE:
						event = None
			elif isinstance(event, MouseEvent) and event.buttons != 0:
					origin = self._canvas.origin
					if event.y < origin[1] or event.y >= origin[1] + self._canvas.height:
						event = None
					elif event.x < origin[0] or event.x >= origin[0] + self._canvas.width:
						event = None
		if event is None:
			self._destroy()
		return super(Playlists, self).process_event(event)
