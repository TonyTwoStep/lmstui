import json, logging

_LOGGER = logging.getLogger(__name__)

TYPE_MENU = 1
TYPE_AUDIO = 2
TYPE_PLAYLIST = 3
TYPE_SEARCH = 4
TYPE_TEXT = 5

def menu_type(menu):

	if isinstance(menu, AudioMenuItem):
		return "audio"
	elif isinstance(menu, PlaylistMenuItem):
		return "playlist"
	elif isinstance(menu, SearchMenuItem):
		return "search"
	elif isinstance(menu, TextMenuItem):
		return "text"
	else:
		return "menu"

class LMSMenuItemBase(object):

	def __init__(self, player=None, menuitem=None, base=None):

		self.player = player
		self.text = None
		self._cmd = None
		self.icon = None
		self.action = None
		self.base = base
		self.menuitem = menuitem
		self.params = []
		self._process_item(menuitem)

	def __str__( self):
		return self.text

	def _process_item(self, menuitem):

		self.text = menuitem.get("text", "")
		self.icon = self._get_icon(menuitem)
		self._is_node = True if menuitem.get("isANode") else False
		self.has_actions = True if menuitem.get("actions") else False
		self.actions = None if not self.has_actions else menuitem.get("actions")
		self.params = menuitem.get("params", None)

	def _get_icon(self, menuitem):

		icon = menuitem.get("icon", None)

		if icon is None:
			icon = menuitem.get("icon-id", None)

		if icon is None:
			icon = menuitem.get("window", dict()).get("icon-id", None)

		if icon is None:
			icon = menuitem.get("commonParams", dict()).get("track_id", None)
			if icon:
				icon = "music/{}/cover".format(icon)

		if icon and not icon.startswith("http"):
			icon = self.player._server._url + str(icon)
		return icon

	def format_dict_cmd(self, item):
		return ["{}:{}".format( x, item[x]) for x in item]

	def build_cmd(self, menuitem):

		act = menuitem.get("actions", dict()).get("go", False)

		if act:
			#_LOGGER.debug("build_cmd: action: {}".format( repr( act)))
			cmd = act["cmd"] + self.format_dict_cmd(act.get("params", dict()))
			try:
				idx = cmd.index("items")
				cmd.insert( idx + 1, 1000)
				cmd.insert( idx + 1, 0)
			except ValueError:
				pass
			#_LOGGER.debug("build_cmd: cmd: {}".format( repr( cmd)))
			return cmd
		else:
			return []

	def _list_to_str(self, cmdlist):
		return " ".join(str(x) for x in cmdlist)

	@property
	def cmdstring(self):
		if type(self._cmd) == list:
			return " ".join(str(x) for x in self._cmd)
		else:
			return None

class NextMenuItem(LMSMenuItemBase):
	"""Menu item which has no other purpose than to create a new submenu."""
	itemtype = TYPE_MENU

	def __init__(self, player=None, menuitem=None, base=None):
		super(NextMenuItem, self).__init__(player=player,
											menuitem=menuitem,
											base=base)
		self._cmd = self.build_cmd(menuitem)
		self._node = menuitem.get("node", None)
		self._id = menuitem.get("id", None)
		self.has_actions_go = True if ( self.has_actions and "go" in menuitem.get("actions")) else False
		self.has_actions_go_next = True if ( self.has_actions_go and "nextWindow" in menuitem) else False
		self.has_actions_do = True if ( self.has_actions and "do" in menuitem.get("actions")) else False
		self.has_actions_play = True if ( self.has_actions and "play" in menuitem.get("actions")) else False
		self.actions_do_choices = None if ( not self.has_actions_do or "choices" not in menuitem["actions"]["do"]) else menuitem["actions"]["do"]["choices"]
		self.actions_do_choiceStrings = None if not self.has_actions_do else menuitem.get( "choiceStrings", None)
		self.actions_do_cmd = None if ( not self.has_actions_do or "cmd" not in menuitem["actions"]["do"]) else menuitem["actions"]["do"]["cmd"]
		self.actions_do_params = None if ( not self.has_actions_do or "params" not in menuitem["actions"]["do"]) else menuitem["actions"]["do"]["params"]
		self.actions_do_input = None if ( not self.has_actions_do or "input" not in menuitem) else menuitem["input"]

	def __str__( self):
		return self.text + "[" + ( self._id if self._id else "NoID") + " @ " + ( self._node if self._node else "NoNode") + "]"

	def __repr__( self):
		return ( self._id if self._id else "NoID") + " @ " + ( self._node if self._node else "NoNode")

	@property
	def cmd(self):
		"""
		:rtype: str
		:returns: command string for next menu

		Get command string for submenu.
		"""
		return self._cmd


class SearchMenuItem(LMSMenuItemBase):
	"""Menu item where a search term is required."""
	itemtype = TYPE_SEARCH

	def __init__(self, player=None, menuitem=None, base=None):
		super(SearchMenuItem, self).__init__(player=player,
												menuitem=menuitem,
												base=base)
		self.search_text = None

	def search(self, query):
		"""
		:type query: str
		:param query: search terms
		:rtype: list
		:returns: command to generate search results
		"""
		cmd = self.build_cmd(self.menuitem)
		cmd = [u"{}".format(x).replace("__TAGGEDINPUT__", query)
				if "__TAGGEDINPUT__" in u"{}".format(x) else x for x in cmd]
		return cmd

	@property
	def cmd_search(self):
		"""
		:rtype: str
		:returns: raw command string

		You will need to replace __TAGGEDINPUT__ with your search term before \
		building a menu with this command.
		"""
		return self._list_to_str(self.build_cmd(self.menuitem))

class PlaylistMenuItem(LMSMenuItemBase):
	"""
	A playlist menu item is one that can be played directly from this link \
	but can also provide a submenu of all the tracks in the playlist.
	"""
	itemtype = TYPE_PLAYLIST

	def __init__(self, player=None, menuitem=None, base=None):
		super(PlaylistMenuItem, self).__init__(player=player,
												menuitem=menuitem,
												base=base)
		self.play_control_params = menuitem.get("playControlParams") if ( "goAction" in menuitem and "playControl" == menuitem.get("goAction")) else None

	def cmd_from_action(self, mode):
		cmd = []

		act = self.menuitem.get("actions", dict()).get(mode)

		if not act:
			act = self.base.get("actions", dict()).get(mode)

		if act:
			cmd += act.get("cmd", list())
			cmd += self.format_dict_cmd(act.get("params", dict()))
			key = act.get("itemsParams")
			if key:
				try:
					cmd += self.format_dict_cmd(self.menuitem[key])
				except KeyError:
					pass

		return cmd

	def play(self):
		"""Play the selected item."""
		cmd = self.cmd_play
		self.player.query( *cmd)

	def play_next(self):
		"""Play the selected item after the currently playing item."""
		cmd = self.cmd_play_next
		self.player.query( *cmd)

	def add(self):
		"""Add the selected item to your playlist."""
		cmd = self.cmd_add
		self.player.query( *cmd)

	def go(self):
		"""
		:rtype: list
		:returns: command list for submenu

		Go to submenu i.e. list of tracks in playlist.
		"""
		return self.cmd_from_action("go")

	@property
	def cmd_play(self):
		"""
		:rtype: str
		:returns: command string to play selected item
		"""
		# return self._list_to_str(self.cmd_from_action("play"))
		return self.cmd_from_action("play")

	@property
	def cmd_play_next(self):
		"""
		:rtype: str
		:returns: command string to play selected item after currently \
		playing item
		"""
		# return self._list_to_str(self.cmd_from_action("add-hold"))
		return self.cmd_from_action("add-hold")

	@property
	def cmd_add(self):
		"""
		:rtype: str
		:returns: command string to add selected item to playlist
		"""
		#cmd = self.cmd_from_action("add")
		#return self._list_to_str(cmd)
		return self.cmd_from_action("add")

	@property
	def show_items_cmd(self):
		"""
		:rtype: str
		:returns: command string to show submenu items
		"""
		cmd = self.go()
		return " ".join(str(x) for x in cmd)


class AudioMenuItem(PlaylistMenuItem):
	"""Audio menu item. Basically the same as a playlist."""
	itemtype = TYPE_AUDIO

	pass

class TextMenuItem( LMSMenuItemBase):
	itemtype = TYPE_TEXT

	def build_cmd(self, menuitem):
		return []

	def _get_icon(self, menuitem):
		return None
