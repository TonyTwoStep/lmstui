import logging

from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, Button, TextBox, Widget, MultiColumnListBox
from asciimatics.exceptions import ResizeScreenError, StopApplication, InvalidFields, NextScene
from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen

from lmstui.utils import config

_LOGGER = logging.getLogger(__name__)

# https://stackoverflow.com/questions/41760856/most-simple-tree-data-structure-in-python-that-can-be-easily-traversed-in-both

class Favorites(Frame,):
	def __init__(self, screen, lms):
		super(Favorites, self).__init__(screen,
										config.APP_DIM_H_L,
										config.APP_DIM_W_M,
										has_shadow=False,
										has_border=True,
										can_scroll=False,
										is_modal=True,
										title="Favorites",
										name="FavoritesFrame")

		opts = []
		self._uifavs = ListBox( Widget.FILL_FRAME, opts, centre=False, add_scroll_bar=True, on_select=self._play)
		layout = Layout([100], fill_frame=True)
		self.add_layout(layout)
		layout.add_widget(self._uifavs, 0)
		layout.add_widget(Divider(height=1, draw_line=True), 0)

		self._player = lms.get_current_player()

		layout2 = Layout([1, 1, 1, 1])
		self.add_layout(layout2)
		layout2.add_widget(Button("Back", self._destroy), 3)

		self._favs = lms.get_favorites()
		if self._favs is not None:
			opts = []
			for f in self._favs:
				'''
				txt = ""
				if f['isaudio']:
					txt += ( config.ICON_music + " ")
				elif f['hasitems']:
					txt += ( config.ICON_circle + " ")
				txt += f['name']
				opts.append( ( txt, f['id']))
				'''
				#if f['hasitems']:
				self._proc_sub( opts, f)
			self._uifavs.options = opts

		self.set_theme( config.APP_THEME)
		self.fix()

	def _proc_sub( self, opts, item, level=0):
		txt = level * " "
#		if level > 0:
#			txt = level * " "  # + "├─" + " "
		if item['isaudio']:
			txt += ( config.ICON_music + " ")
		elif item['hasitems']:
			txt += ( config.ICON_folder + " ")
		txt += item['name']
		_LOGGER.debug( "_proc_sub:  level: {} txt:{}".format( level, txt))
		opts.append( ( txt, item['id'] if item['isaudio'] else ("NOAUDIO_" + item['id'])))
		if 'children' in item:
			for subitem in item['children']:
				self._proc_sub( opts, subitem, level=(level + 1))

	def _play( self):
		_LOGGER.debug( "_play: self._uifavs.val= {} ".format( self._uifavs.value))
		if self._uifavs.value and not self._uifavs.value.startswith( "NOAUDIO_"):
			self._player.query( 'favorites', 'playlist', 'play', 'item_id:' + str(self._uifavs.value))
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
		return super(Favorites, self).process_event(event)
