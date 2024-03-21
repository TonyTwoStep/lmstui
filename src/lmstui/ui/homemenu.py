import logging

from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, Button, TextBox, Widget, MultiColumnListBox
from asciimatics.exceptions import ResizeScreenError, StopApplication, InvalidFields, NextScene
from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen

from lmstui.lms.menu import LMSMenuHandler
from lmstui.lms import menuitems
from lmstui.ui.submenu import SubMenuList
from lmstui.utils import config

_LOGGER = logging.getLogger(__name__)


class HomeMenu(Frame,):
	def __init__(self, screen, lms):
		super(HomeMenu, self).__init__(screen,
										config.APP_DIM_H_S,
										config.APP_DIM_W_S,
										has_shadow=False,
										has_border=True,
										can_scroll=False,
										is_modal=True,
										title="Home Menu",
										name="HomeMenuFrame")

		opts = []
		self._uientries = ListBox( Widget.FILL_FRAME, opts, centre=False, add_scroll_bar=True, on_select=self._process)
		layout = Layout([100], fill_frame=True)
		self.add_layout(layout)
		layout.add_widget(self._uientries, 0)
		layout.add_widget(Divider(height=1, draw_line=True), 0)

		self._player = lms.get_current_player()

		layout2 = Layout([1, 1, 1])
		self.add_layout(layout2)
		layout2.add_widget(Button("Close", self._destroy), 2)

		if self._player is not None:
			self._menu_handler = LMSMenuHandler( player=self._player)
			self._homemenu, self._homestruct = self._create_home( self._menu_handler)
			opts = []
			for i, e in enumerate( self._homestruct):
				_LOGGER.debug("LMSMenuHandler: mstruc: key:{} val:{}".format( e, str(self._homestruct[e])))
				opts.append( (e, e))

			self._uientries.options = opts

		self.set_theme( config.APP_THEME)
		self.fix()

	def _create_home( self, menu_handler):
		homemenu = menu_handler.getHomeMenu()
		mstruc = {}
		for i, entry in enumerate( homemenu):
			_LOGGER.debug("LMSMenuHandler: id: {} type: {} cmdstring:{}".format( entry._id, menuitems.menu_type( entry), entry.cmdstring))
			#_LOGGER.debug("LMSMenuHandler: id:{}  node:{} isNode:{} text:{}".format( entry._id, entry._node, str(entry._is_node), entry.text))
			node = entry._node
			if not entry._node or len( entry._node) == 0:
				node = "Unsorted"
			if node not in mstruc:
				mstruc[ node] = []
			#mstruc[ node].append( { "id": entry._id, "text": entry.text})
			mstruc[ node].append( entry)
			'''
			if entry._id == "trackstat":
				tsmenu = menu_handler.getMenu( entry.cmd)
				for i, subentry in enumerate( tsmenu):
					_LOGGER.debug("LMSMenuHandler: tsmenu: id: {} type: {} cmd:{}".format( subentry._id, menuitems.menu_type( subentry), repr(subentry.cmd)))
			'''
		return homemenu, mstruc

	def _process( self):
		_LOGGER.debug( "_process: self._uientries.val= {} ".format( self._uientries.value))
		_LOGGER.debug( "_process: entry= {} ".format( self._homestruct[ self._uientries.value]))
		self._scene.add_effect( SubMenuList( self.screen, self._menu_handler, self._homestruct[ self._uientries.value], None, title=self._uientries.value))

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
		return super(HomeMenu, self).process_event(event)
