from lmstui.ui.popupmenuext import PopupMenuExt
from lmstui.utils import config

class Players( PopupMenuExt):

	def set_players( self, opts):
		self._uilistbox.options = opts
