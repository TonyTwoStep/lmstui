import logging

from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, Button, TextBox, Widget, MultiColumnListBox, PopUpDialog, PopupMenu
from asciimatics.exceptions import ResizeScreenError, StopApplication, InvalidFields, NextScene
from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen

from lmstui.ui.popupmenuext import PopupMenuExt
from lmstui.lms.menu import LMSMenuHandler
from lmstui.lms import menuitems
from lmstui.utils import config

_LOGGER = logging.getLogger(__name__)

class SubMenu( Frame):
	def __init__(self, screen, menu_handler, entries, parent_entries, title="Sub Menu", h=None, w=None):
		if h is None:
			h = config.APP_DIM_H_M
		if w is None:
			w = config.APP_DIM_W_S

		super(SubMenu, self).__init__(screen,
										h,
										w,
										has_shadow=False,
										has_border=True,
										can_scroll=False,
										is_modal=True,
										title=title.replace("\n", " | "))
		# name="SubMenuFrame")

		if parent_entries is None:
			self._parent_entries = []
		else:
			self._parent_entries = parent_entries

		#_LOGGER.debug("SubMenu: _parent_entries: {}".format( repr( self._parent_entries)))
		self._menu_handler = menu_handler
		self._entries = entries

		self._create_ui( entries)
		self.set_theme( config.APP_THEME)
		self.fix()

	def _switch_to_parent( self):
		parent_menu = self._parent_entries[-1]
		parents = self._parent_entries[:-2] if len( self._parent_entries) != 1 else None
		self._scene.add_effect( SubMenuList( self.screen, self._menu_handler, parent_menu, parents, title="Menu"))
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
		return super(SubMenu, self).process_event(event)

class SubMenuList( SubMenu):
	def _create_ui( self, entries):
		opts = []
		self._uientries = ListBox( Widget.FILL_FRAME, opts, centre=False, add_scroll_bar=True, on_select=self._process)
		layout = Layout([100], fill_frame=True)
		self.add_layout(layout)
		layout.add_widget(self._uientries, 0)
		layout.add_widget(Divider(height=1, draw_line=True), 0)

		layout2 = Layout([1, 1, 1, 1])
		self.add_layout(layout2)
		layout2.add_widget(Button("Back", self._destroy), 3)

		opts = [ ("<<", -1)]
		for i, e in enumerate( entries):
			_LOGGER.debug("SubMenu: entry: {} actions:{}".format( e, e.has_actions))
			ot = ""
			if e.itemtype == menuitems.TYPE_MENU:
				if e.has_actions:
					ot = config.ICON_arrow_right + " "
				else:
					ot = config.ICON_dot + " "
			elif e.itemtype == menuitems.TYPE_PLAYLIST:
				ot = config.ICON_list + " "
			elif e.itemtype == menuitems.TYPE_AUDIO:
				ot = config.ICON_music + " "
			elif e.itemtype == menuitems.TYPE_SEARCH:
				ot = config.ICON_search + " "
			elif e.itemtype == menuitems.TYPE_TEXT:
				ot = config.ICON_info + " "
			else:
				_LOGGER.debug("SubMenu: unknown type: {}".format( e.itemtype))
			if len( ot) > 0:
				opts.append( ( ot + e.text.replace("\n", " | "), i))
		self._uientries.options = opts

	def _process( self):
		_LOGGER.debug( "_process: self._uientries.val= {} ".format( self._uientries.value))
		if int( self._uientries.value) == -1:
			if len( self._parent_entries) > 0:
				_LOGGER.debug( "_process: self._parent_entries= {} ".format( repr(self._parent_entries)))
				_LOGGER.debug( "_process: self._parent_entries[-1]= {} ".format( repr(self._parent_entries[-1])))
				self._switch_to_parent()
			else:
				self._destroy()
			return
		entry = self._entries[ int(self._uientries.value)]
		#_LOGGER.debug( "_process: entry= {}".format( entry))
		_LOGGER.debug( "_process: menu entry= {}".format( repr(entry.menuitem)))
		if menuitems.menu_type( entry) == "menu" and entry.has_actions_go and entry.cmd and not entry.has_actions_play:
			_LOGGER.debug( "_process: menu cmd= {}".format( entry.cmd))
			submenu = self._menu_handler.getMenu( entry.cmd + ["direct:1"])
			#for i, e in enumerate( submenu):
			#	_LOGGER.debug("SubMenuList: entry: {}".format( e))
			if submenu:
				self._parent_entries.append( self._entries)
				self._scene.add_effect( SubMenuList( self.screen, self._menu_handler, submenu, self._parent_entries, title=entry.text))
				self._destroy()
			else:
				if entry.has_actions_go_next:
					_LOGGER.debug( "_process: has_actions_go: has_actions_go_next")
					self._destroy()
				else:
					self._scene.add_effect(
						PopUpDialog(self._screen,
									"Error getting menu (cmd: {})".format( entry.cmd),
									["OK"],
									has_shadow=True))
		elif menuitems.menu_type( entry) == "menu" and entry.has_actions_play:
			_LOGGER.debug( "_process: has_actions_play actions= {}".format( repr(entry.actions)))
			options = []
			for i, act in enumerate( entry.actions):
				if entry.actions[ act] is not None:
					_LOGGER.debug( "_process: has_actions_play: checking action {}".format( act))
					if "params" in entry.actions[ act]:
						parms = entry.format_dict_cmd( entry.actions[ act]["params"])
					_LOGGER.debug( "_process: has_actions_play action= {} cmd={} parm={}".format( act, entry.actions[ act]["cmd"], parms))
					options.append( ( act, entry.actions[ act]["cmd"] + parms))
				elif entry.base is not None and entry.base['actions'][ act] is not None:
					_LOGGER.debug( "_process: has_actions_play: checking action {} base={}".format( act, repr( entry.base)))
					if entry.params:
						parms = entry.format_dict_cmd( entry.params)
					_LOGGER.debug( "_process: has_actions_play base action= {} cmd={} parm={}".format( act, entry.base['actions'][ act]["cmd"], parms))
					options.append( ( act + " (base)", entry.base['actions'][ act]["cmd"] + parms))

			self._doentry = entry
			self._popup_dochoice = PopupMenuExt( self.screen, "Action for " + entry.text, options, ["Select", "Cancel"], callback=self._choose_do_action)
			self._popup_dochoice.set_theme( config.APP_THEME)
			self._scene.add_effect( self._popup_dochoice)
		elif menuitems.menu_type( entry) == "menu" and entry.has_actions_do:
			#_LOGGER.debug( "_process: has_actions_do")
			if entry.actions_do_choices:
				#_LOGGER.debug( "_process: has_actions_do actions_do_choices= {}".format( entry.actions_do_choices))
				#_LOGGER.debug( "_process: has_actions_do actions_do_choiceStrings= {}".format( entry.actions_do_choiceStrings))
				self._doentry = entry
				options = []
				for i, choice in enumerate( entry.actions_do_choices):
					options.append( ( entry.actions_do_choiceStrings[i], choice['cmd']))
				_LOGGER.debug( "_process: has_actions_do opts= {}".format( repr( options)))
				self._popup_dochoice = PopupMenuExt( self.screen, "Setting for " + entry.text, options, ["Select", "Cancel"], callback=self._choose_do_action)
				self._popup_dochoice.set_theme( config.APP_THEME)
				self._scene.add_effect( self._popup_dochoice)
			elif entry.actions_do_input:
				_LOGGER.debug( "_process: has_actions_do cmd={} params={}".format( entry.actions_do_cmd, entry.actions_do_params))
				self._scene.add_effect(
					PopUpDialog(self._screen,
								"Not implemented (cmd: actions_do_input)",
								["Cancel"],
								has_shadow=True))
				self._destroy()
			else:
				_LOGGER.debug( "_process: has_actions_do: unhandled")
		elif ( menuitems.menu_type( entry) == "audio" or menuitems.menu_type( entry) == "playlist"):
			_LOGGER.debug( "_process: audio cmd= {}".format( entry.show_items_cmd))
			self._audioentry = entry
			options = [ ("Add", "_choose_audio_add"), ("Play", "_choose_audio_play"), ("Play next", "_choose_audio_play_next"), ("Go", "_choose_audio_go")]
			self._popup_audiochoice = PopupMenuExt( self.screen, "Action for " + entry.text.replace("\n", " | "), options, ["Select", "Cancel"], callback=self._choose_audio_action)
			self._popup_audiochoice.set_theme( config.APP_THEME)
			self._scene.add_effect( self._popup_audiochoice)
		elif menuitems.menu_type( entry) == "search":
			self._parent_entries.append( self._entries)
			self._scene.add_effect( SubMenuSearch( self.screen, self._menu_handler, [ entry], self._parent_entries, title=entry.text, h=5, w=min( 80, self._screen.width)))
			self._destroy()
		elif menuitems.menu_type( entry) == "text":
			pass
		else:
			_LOGGER.debug( "_process: unhandled")

	def _choose_audio_action( self):
		val, but = self._popup_audiochoice.get_selected_value()
		_LOGGER.debug("_choose_audio_action: pop val:{} but:{}".format( val, but))
		if val and ( ( but and but == 0) or not but):
			if self._audioentry is not None:
#				_LOGGER.debug("_choose_audio_action: entry:{}".format( repr( self._audioentry.menuitem)))
				if val == "_choose_audio_go":
					_LOGGER.debug("_choose_audio_action: _choose_audio_go: go: {}".format( self._audioentry.go()))
					submenu = self._menu_handler.getMenu( self._audioentry.go() + ["direct:1"])
					if submenu:
						self._parent_entries.append( self._entries)
						self._scene.add_effect( SubMenuList( self.screen, self._menu_handler, submenu, self._parent_entries, title=self._audioentry.text))
						self._destroy()
					else:
						_LOGGER.warn("_choose_audio_action: _choose_audio_go: no submenu")
				elif val == "_choose_audio_add":
					#_LOGGER.debug("_choose_audio_action: _choose_audio_add: cmd: {}".format( self._audioentry.cmd_add))
					self._audioentry.add()
				elif val == "_choose_audio_play":
					#_LOGGER.debug("_choose_audio_action: _choose_audio_play: cmd: {}".format( self._audioentry.cmd_play))
					self._audioentry.play()
				elif val == "_choose_audio_play_next":
					#_LOGGER.debug("_choose_audio_action: _choose_audio_play_next: cmd: {}".format( self._audioentry.cmd_play_next))
					self._audioentry.play_next()
			else:
				_LOGGER.error( "_choose_audio_action: no audio entry")

	def _choose_do_action( self):
		val, but = self._popup_dochoice.get_selected_value()
		_LOGGER.debug("_choose_do_action: pop val:{} but:{}".format( val, but))
		if val and ( ( but and but == 0) or not but):
			_LOGGER.debug("_choose_do_action: entry:{}".format( repr( self._doentry.menuitem)))
			res = self._menu_handler.player.query( *val)
			_LOGGER.debug("_choose_do_action: res:{}".format( repr( res)))
			if res:
				submenu = self._menu_handler._process_menu( res)
				self._parent_entries.append( self._entries)
				self._scene.add_effect( SubMenuList( self.screen, self._menu_handler, submenu, self._parent_entries, title=self._doentry.text))
				self._destroy()


class SubMenuInput( SubMenu):
	def process_event(self, event):
		if event is not None:
			if isinstance(event, KeyboardEvent):
					#_LOGGER.debug( "SubMenuSearch: event.key_code: {}".format( event.key_code))
					if event.key_code == 10:
						self._on_input()
						event = None
		if event is not None:
			return super(SubMenuInput, self).process_event(event)


class SubMenuSearch( SubMenuInput):
	def _create_ui( self, entries):
		self._uisearchterm = Text("Term:", "term")  # , on_change=self.filter_pls)
		layout = Layout([100], fill_frame=True)
		self.add_layout(layout)
		layout.add_widget(self._uisearchterm, 0)

		layout2 = Layout([1, 1, 1])
		self.add_layout(layout2)
		layout2.add_widget(Button("Search", self._on_input), 0)
		layout2.add_widget(Button("Back", self._switch_to_parent), 2)

	def _on_input( self):
		_LOGGER.debug( "SubMenuSearch: _uisearchterm: {}".format( self._uisearchterm.value))
		submenu = self._menu_handler.getMenu( self._entries[0].search( self._uisearchterm.value) + ["direct:1"])
		if submenu:
			self._scene.add_effect( SubMenuList( self.screen, self._menu_handler, submenu, self._parent_entries, title="Result for " + self._uisearchterm.value))
			self._destroy()
