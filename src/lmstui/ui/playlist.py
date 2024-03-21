import logging

from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, Button, TextBox, Widget, MultiColumnListBox
from asciimatics.exceptions import ResizeScreenError, StopApplication, InvalidFields, NextScene
from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen

from lmstui.utils import config
from lmstui.utils import tools

_LOGGER = logging.getLogger(__name__)

class Playlist(Frame,):
	def __init__(self, screen, lms):
		super(Playlist, self).__init__(screen,
										config.APP_DIM_H_L,
										config.APP_DIM_W_L,
										has_shadow=False,
										has_border=True,
										can_scroll=False,
										title="Playlist",
										name="PlaylistFrame")

		cols = [ 0, "<25%", "<25%"]
		options = [(["-", "-", "-"], 1)]
		self._uiplaylist = MultiColumnListBox( Widget.FILL_FRAME, cols, options, add_scroll_bar=True, on_select=self._go)
		layout = Layout([100], fill_frame=True)
		self.add_layout(layout)
		layout.add_widget(self._uiplaylist, 0)
		layout.add_widget(Divider(height=1, draw_line=True), 0)
		self._uifilter = Text("Filter:", "filter", on_change=self.filter_pls)
		layout.add_widget( self._uifilter, 0)
		layout.add_widget(Divider(height=1, draw_line=True), 0)

		layout2 = Layout([1, 1, 1, 1])
		self.add_layout(layout2)
		layout2.add_widget(Button("Back", self._ok), 0)

		lms.update()
		self._lms = lms
		if self.fetch_playlist():
			self.update_playlist( )

		self.set_theme( config.APP_THEME)
		self.fix()

	def update(self, frame_no):
		self.set_theme( config.APP_THEME)
		super(Playlist, self).update( frame_no)

	def filter_pls( self):
		if self._uifilter.value is not None and self._uifilter.value is not "":
			#_LOGGER.debug( "filter_pls: self._uifilter.value= {} ".format( self._uifilter.value))
			self.update_playlist( filter=self._uifilter.value)
#			self._uiplaylist.blur()
#			self._uifilter.focus()

	def update_playlist( self, filter=None):
		opts = []
		curridx = self._player.get_playlist_current_index()
		#_LOGGER.debug( "update_playlist: curridx= {}".format( curridx))
		for i, row in enumerate( self._pls):
			ti = ( config.ICON_volume + " ") if ( i == curridx) else ""
			if "tracknum" in row:
				ti += "{:02}. ".format( int(row["tracknum"]))
			ti += row[ 'title'] if 'title' in row else "-"
			if "year" in row:
				ti += " ({:04})".format( int(row["year"]))
			if "rating" in row:
				ti += " " + tools.rating2icon( int( row['rating']))
			ar = row[ 'trackartist'] if 'trackartist' in row else ( row['artist'] if 'artist' in row else "-")
			al = row[ 'album'] if 'album' in row else "-"
			if filter is None:
				opts.append( ( [ ti, ar, al], i))
			else:
				g = row[ 'genre'] if 'genre' in row else ""
				matchstr = " ".join( (ti, ar, al, g))
				if filter.lower() in matchstr.lower():
					opts.append( ( [ ti, ar, al], i))
		self._uiplaylist.options = opts
		if filter is None:
			self._uiplaylist.start_line = curridx
		#self.fix()

	def reset(self):
		super(Playlist, self).reset()
		self._uifilter.value = None
		if self.fetch_playlist():
			self.update_playlist()

	def fetch_playlist( self):
		self._player = self._lms.get_current_player()
		if self._player:
			self._pls = self._player.get_playlist_current()
			if self._pls is not None:
				return True
		return False

	def _go( self):
		#_LOGGER.debug( "_go: self._uiplaylist.val= {} ".format( self._uiplaylist.value))
		self._player.playlist_play_idx( self._uiplaylist.value)
		raise NextScene("Main")

	def _ok(self):
		raise NextScene("Main")

	def process_event(self, event):
		if event is not None and isinstance(event, KeyboardEvent):
			if event.key_code == 47 or event.key_code == 6:  # / or ^f
				self._uifilter.focus()
				self._uiplaylist.blur()
				event = None
			elif event.key_code == Screen.KEY_ESCAPE:
				self._ok()
		return super(Playlist, self).process_event(event)
