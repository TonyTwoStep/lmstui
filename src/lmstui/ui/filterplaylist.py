import logging

from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, Button, TextBox, Widget, MultiColumnListBox, CheckBox
from asciimatics.exceptions import ResizeScreenError, StopApplication, InvalidFields, NextScene
from asciimatics.event import KeyboardEvent, MouseEvent
from asciimatics.screen import Screen

from lmstui.utils import config
from lmstui.utils import tools

_LOGGER = logging.getLogger(__name__)

form_data = { "rate_from": "0"}

class FilterPlaylist(Frame,):
	def __init__(self, screen, lms):
		super(FilterPlaylist, self).__init__(screen,
										min( screen.height, 10),
										min( screen.width, 50),
										data=form_data,
										has_shadow=False,
										has_border=True,
										can_scroll=False if (screen.height > 9) else True,
										is_modal=True,
										title="Filter Playlist",
										name="FilterPlaylistFrame")

		layout = Layout([ 1, 1], fill_frame=False)
		self.add_layout(layout)
		self._uiratefrom = Text( label="Rating >", name="rate_from", max_length=3, validator="^[0-9]*$", on_change=self._on_change)
		self._uirateto = Text( label="Rating <", name="rate_to", max_length=3, validator="^[0-9]*$", on_change=self._on_change)
		layout.add_widget(self._uiratefrom, 0)
		layout.add_widget(self._uirateto, 0)
		self._uiyearfrom = Text( label="Year >", name="year_from", max_length=4, validator="^[0-9]*$", on_change=self._on_change)
		self._uiyearto = Text( label="Year <", name="year_to", max_length=4, validator="^[0-9]*$", on_change=self._on_change)
		layout.add_widget(self._uiyearfrom, 1)
		layout.add_widget(self._uiyearto, 1)

		self._uiremovenull_r = CheckBox( label="unrated", text="", name="remove_null_r", on_change=self._on_change)
		self._uiremovenull_r.value = True
		layout.add_widget( self._uiremovenull_r, 0)
		self._uiremovenull_y = CheckBox( label="no year", text="", name="remove_null_y", on_change=self._on_change)
		self._uiremovenull_y.value = True
		layout.add_widget( self._uiremovenull_y, 1)

		layout2 = Layout([ 1], fill_frame=False)
		self.add_layout(layout2)
		layout2.add_widget(Divider(height=1, draw_line=True), 0)
		self._uifilter = Text(label="Text filter:", name="textfilter", on_change=self._on_change)
		layout2.add_widget( self._uifilter, 0)
		layout2.add_widget(Divider(height=1, draw_line=True), 0)

		layout3 = Layout([1, 1])
		self.add_layout(layout3)
		self._uibtnfilter = Button("Filter", self._filter_pls)
		layout3.add_widget( self._uibtnfilter, 0)
		layout3.add_widget(Button("Close", self._close), 1)

		lms.update()
		self._lms = lms
		if self.fetch_playlist():
			self.pls_to_form()

		self.set_theme( config.APP_THEME)
		self.fix()

	def update(self, frame_no):
		self.set_theme( config.APP_THEME)
		super(FilterPlaylist, self).update( frame_no)

	def pls_to_form( self):
		#_LOGGER.debug( "pls_to_form: pls: {}".format( repr( self._pls)))
		#self.data['rate_to'] = max( [int( i['rating']) if 'rating' in i else 0 for i in self._pls])
		ratemin = 100
		ratemax = 0
		yearmin = 2050
		yearmax = 1000
		for track in self._pls:
			if 'rating' in track:
				ratemin = min( ratemin, int( track['rating']))
				ratemax = max( ratemax, int( track['rating']))
			if 'year' in track:
				yearmin = min( yearmin, int( track['year']))
				yearmax = max( yearmax, int( track['year']))

		form_data['rate_to'] = str(ratemax)
		form_data['rate_from'] = str(ratemin)
		form_data['year_to'] = str(yearmax)
		form_data['year_from'] = str(yearmin)
		'''
		form_data['rate_to'] = str( max( [int( i['rating']) if 'rating' in i else 0 for i in self._pls]))
		form_data['rate_from'] = str( min( [int( i['rating']) if 'rating' in i else 0 for i in self._pls]))
		form_data['year_to'] = str( max( [int( i['year']) if 'year' in i else 0 for i in self._pls]))
		form_data['year_from'] = str( min( [int( i['year']) if 'year' in i else 0 for i in self._pls]))
		'''

	def reset(self):
		_LOGGER.debug( "reset")
		self._uifilter.value = None
		if self.fetch_playlist():
			self._uibtnfilter.disabled = False
			self.pls_to_form()
		else:
			self._uibtnfilter.disabled = True
		super(FilterPlaylist, self).reset()

	def fetch_playlist( self):
		self._player = self._lms.get_current_player()
		#_LOGGER.debug( "fetch_playlist")
		if self._player:
			#_LOGGER.debug( "fetch_playlist: _player")
			self._pls = self._player.get_playlist_current()
			if self._pls is not None:
				#_LOGGER.debug( "fetch_playlist: _pls")
				return True
		return False

	def _filter_pls( self):
		has_textfilter = True if (self._uifilter.value is not None and self._uifilter.value is not "") else False
		tids = []
		for row in self._pls:
			select_row = False
			if has_textfilter:
				ti = row[ 'title'] if 'title' in row else ""
				ar = row[ 'trackartist'] if 'trackartist' in row else ( row['artist'] if 'artist' in row else "")
				al = row[ 'album'] if 'album' in row else ""
				g = row[ 'genre'] if 'genre' in row else ""
				matchstr = " ".join( (ti, ar, al, g))
				if self._uifilter.value.lower() in matchstr.lower():
					select_row = True
					_LOGGER.debug( "filter_pls: _uifilter {} match".format( matchstr.lower()))
			if 'rating' in row:
				if int(row['rating']) not in range( int(self._uiratefrom.value), int( self._uirateto.value) + 1):
					_LOGGER.debug( "filter_pls: _uirate {} match".format( row['rating']))
					select_row = True
			elif not self._uiremovenull_r.value:
					select_row = True
			if 'year' in row:
				if int(row['year']) not in range( int(self._uiyearfrom.value), int( self._uiyearto.value) + 1):
					_LOGGER.debug( "filter_pls: _uiyear {} match".format( row['year']))
					select_row = True
			elif not self._uiremovenull_y.value:
					select_row = True
			if select_row:
				tids.append( str(row['id']))

			#_LOGGER.debug( "filter_pls: self._uifilter.value= {} ".format( self._uifilter.value))
		if len( tids) > 0:
			t = ",".join( tids)
			# ['playlistcontrol', 'cmd:delete', 'track_id:'+delTrackIds.join()])
			self._player.playlist_control( "cmd:delete", "track_id:" + ",".join( tids))
			_LOGGER.debug( "filter_pls: tids {}".format( t))
		self._close()

	def _close(self):
		self._scene.remove_effect(self)

	def _on_change(self):
		self.save()

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
			self._close()
		return super(FilterPlaylist, self).process_event(event)
