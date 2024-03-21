import logging

from asciimatics.widgets import Frame, TextBox, Layout, Label, Divider, Text, CheckBox, RadioButtons, Button, PopUpDialog, TimePicker, DatePicker, Background, DropdownList, PopupMenu, VerticalDivider, MultiColumnListBox, Widget
from asciimatics.event import MouseEvent, KeyboardEvent
from asciimatics.exceptions import ResizeScreenError, StopApplication, InvalidFields, NextScene
from asciimatics.screen import Screen

from lmstui.lms.menu import LMSMenuHandler
from lmstui.ui.playlists import Playlists
from lmstui.ui.favorites import Favorites
from lmstui.ui.imagebox import ImageBox
from lmstui.ui.imageboxkitty import ImageBoxKitty
from lmstui.ui.imageboxext import ImageBoxExt
from lmstui.ui.popupmenuext import PopupMenuExt
from lmstui.ui.filterplaylist import FilterPlaylist
from lmstui.ui.homemenu import HomeMenu

from lmstui.utils import config
from lmstui.utils import tools
from lmstui.lms import menuitems

_LOGGER = logging.getLogger(__name__)

class MainFrame(Frame):
	def __init__(self, screen, lms):
		self.lms = lms
		self._trackid = None
		self._suspend_updates = False
		self._keyprefix = 0
		self._popuptheme = None
		self._popupplayers = None

		_LOGGER.debug( "server_status:" + repr( lms.server_status))
		_LOGGER.debug( "players_status:" + repr( lms.players_status))

		super(MainFrame, self).__init__(screen,
										config.APP_DIM_H_L,
										config.APP_DIM_W_L,
										#data=form_data,
										has_shadow=False,
										has_border=False,
										name="MainFrame")

		self.data['TA'] = "server status"
		self.data['LMS'] = self.lms.version
#		_LOGGER.debug( "form data:" + repr( self.data))

		layout1 = Layout([ 1, 1, 1])
		self.add_layout(layout1)
		self._uistatus1 = Text( " " + config.ICON_speaker, name="LMS", disabled=True)
		self._uistatus1.custom_colour = "edit_text"
		self._uistatus2 = Label(  label="Time", align="^")
		self._uistatus2.custom_colour = "edit_text"
		self._uistatus3 = Label(  label="Track", align=">")
		self._uistatus3.custom_colour = "edit_text"
		layout1.add_widget( self._uistatus1, 0)
		layout1.add_widget( self._uistatus2, 1)
		layout1.add_widget( self._uistatus3, 2)

		layout1d = Layout([1])
		self.add_layout( layout1d)
		layout1d.add_widget(Divider(height=1, draw_line=True), 0)

		layout2 = Layout([48, 2, 50], fill_frame=True)
		self.add_layout(layout2)

		self._uitrackinfos = {}
		for f in config.TRACKINFO_ALL:
			t = Text( " " + f[1] + " ", name="text_ti_" + f[0], disabled=True)
			t.custom_colour = "edit_text"
			t.value = f[0]
			self._uitrackinfos[ f[0]] = t
			layout2.add_widget( t, 0)

		layout2.add_widget(Divider(height=3, draw_line=True), 0)
		_LOGGER.debug( "APP_IMAGEMODE: [{}]".format( config.APP_IMAGEMODE))
		if config.APP_IMAGEMODE == "chafa":
			self._uicover = ImageBoxExt( None, None)
		elif config.APP_IMAGEMODE == "asciimatics":
			self._uicover = ImageBox( None, None)
		else:
			self._uicover = None
		if self._uicover:
			layout2.add_widget( self._uicover, 0)

		layout2.add_widget( VerticalDivider( Widget.FILL_FRAME), 1)

		#cols = [ "<50%", "<25%", "<25%"]
		cols = [ 0, "<25%", "<25%"]
		options = [(["-", "-", "-"], 1)]
		self._uiplaylist = MultiColumnListBox( Widget.FILL_FRAME, cols, options, add_scroll_bar=False)
		self._uiplaylist.disabled = True
		self._uiplaylist.custom_colour = "edit_text"
		layout2.add_widget(self._uiplaylist, 2)

		self.set_theme( config.APP_THEME)
		self.fix()

	def update_trackinfo( self, trackinfo):
		_LOGGER.debug( "update_trackinfo: trackinfo_id: {} _trackid: {}".format( trackinfo['id'], self._trackid))
		if trackinfo['id']:
			if self._trackid and self._trackid is trackinfo['id']:
				return
			self._trackid = trackinfo['id']

		for f in config.TRACKINFO_ALL:
			if f[0] in trackinfo:
				if f[0] in self._uitrackinfos:
					t = self._uitrackinfos[  f[0]]
					if f[0] is 'title':
						if 'tracknum' in trackinfo:
							t.value = trackinfo['tracknum'] + ". " + trackinfo[ f[0]]
						else:
							t.value = trackinfo[ f[0]]
						# FIXME
						if "rating" in trackinfo:
							#_LOGGER.debug( "update_trackinfo: rating = {} ".format( trackinfo['rating'] ))
							t._label = tools.rating2icon( int(trackinfo['rating']))
							t.value += " " + tools.rating2icon( int(trackinfo['rating']))
						else:
							t._label = config.ICON_music
					elif f[0] is 'duration':
						t.value = tools.seconds2str( float( trackinfo[f[0]]))
						'''
						if "rating" in trackinfo:
							t.value += ( config.ICON_sep + tools.rating2icon( int(trackinfo['rating'])))
						'''
					else:
						t.value = str( trackinfo[  f[0]])
					#_LOGGER.debug( "update_trackinfo: ti[] = {} ".format( trackinfo[  f[0]] ))
				else:
					_LOGGER.debug( "update_trackinfo: {} not in _uitrackinfos".format( f[0]))
			else:
				_LOGGER.debug( "update_trackinfo: {} not in get_track_info".format( f[0]))
				if f[0] is 'artist' and "trackartist" in trackinfo:
					self._uitrackinfos[  f[0]].value = trackinfo['trackartist']
				else:
					self._uitrackinfos[  f[0]].value = "N/A"

		if self._uicover and 'coverid' in trackinfo:
			curl = self.lms.get_cover_url( trackinfo['coverid'])
			#_LOGGER.debug( "update_trackinfo: cover url: {}".format( curl))
			self._uicover.load_image( curl)

	def update_playlist( self, playlist, idx):
		opts = []
		sl = idx
		for i, row in enumerate( playlist[idx:]):
			ti = ""
			if "tracknum" in row:
				ti = "{:02}. ".format( int(row["tracknum"]))
			ti += row[ 'title'] if 'title' in row else "-"
			if i == 0:
				ti = config.ICON_volume + " " + ti
				sl = i
				#_LOGGER.debug( "update_playlist: c=row {} id: {}".format( i, row[ 'id']))
			ar = row[ 'trackartist'] if 'trackartist' in row else ( row['artist'] if 'artist' in row else "-")
			al = row[ 'album'] if 'album' in row else "-"
			opts.append( ( [ ti, ar, al], row[ 'id']))
		self._uiplaylist.options = opts
		self._uiplaylist.start_line = sl

	def update_playerinfo( self, player):
		if player is None:
			self.show_error( "No player", "")
			return
		self._uistatus1.value = player.get_name()

		if player.get_duration() != 0:
			self._uistatus2.text = tools.progressbar( value=player.get_time(), vmax=player.get_duration(), lsep="[", rsep="]")
		elif player.get_time() != 0:
			self._uistatus2.text = "[" + tools.seconds2str( player.get_time()) + "]"
		if player.get_playlist_current():
			self._uistatus2.text += ( " [" + str( player.get_playlist_current_index() + 1) + "/" + str( player.get_playlist_len()) + "]")

		status = " ["
		if player.is_playing():
			status += config.ICON_control_play
		elif player.is_stopped():
			status += config.ICON_control_stop
		elif player.is_paused():
			status += config.ICON_control_pause
		else:
			status += config.ICON_question
		status += "] [" + config.ICON_volume + " " + str( player.get_volume()) + "]"
		status += (" [") + ( config.ICON_repeat_on if player.is_repeat() else config.ICON_repeat_off) + "]"
		status += ("[") + ( config.ICON_shuffle_on if player.is_shuffle() else config.ICON_shuffle_off) + "]"
		status += (" [") + ( config.ICON_power_on if player.is_power() else config.ICON_power_off) + ( "]" + config.ICON_dot)
		self._uistatus3.text = status

	def show_error( self, msg, error):
		self._uistatus1.value = msg
		self._uistatus2.text = "Server: [" + self.lms._url + "]"
		self._uistatus3.text = "[" + config.ICON_warn + "]"

	def process_event(self, event):
		if event is not None and isinstance(event, KeyboardEvent):
			player = self.lms.get_current_player()
			keep_keyprefix = False
			if event.key_code == 16:  # ^p
				self._select_player()
				event = None
			elif event.key_code == 20:  # ^t
				if not self._popuptheme:
					self._popuptheme = PopupMenuExt( self.screen, "Theme", [ ("Default", "default"), ("Green", "green"), ("Monochrome", "monochrome"), ("Bright", "bright"), ("Red/white", "tlj256"), 
						("Dark grey", "darkgrey"), ("Dark blue", "darkblue"), ("Dark turquoise", "darkturq"), ("Dark #1", "dark1")], ["Apply", "Close"], callback=self._theme_selected)
				self._popuptheme.set_theme( config.APP_THEME)
				self._scene.add_effect( self._popuptheme)
				event = None
			elif player and event.key_code == 32:  # space
				player.toggle()
				event = None
			elif player and event.key_code == 43:  # +
				player.set_volume( "+" + str(config.LMS_VOLADJ))
				event = None
			elif player and event.key_code == 45:  # -
				player.set_volume( "-" + str(config.LMS_VOLADJ))
				event = None
			elif player and event.key_code == Screen.KEY_UP:
				#player.previous_song()
				#_LOGGER.debug("skip_songs: {}".format( max( 1, self._keyprefix) * -1))
				player.skip_songs( max( 1, self._keyprefix) * -1)
				event = None
			elif player and event.key_code == Screen.KEY_DOWN:
				#player.next_song()
				#_LOGGER.debug("skip_songs: {}".format( max( 1, self._keyprefix)))
				player.skip_songs( max( 1, self._keyprefix))
				event = None
			elif player and event.key_code == 337:  # shift-<up>
				player.skip_songs( config.LMS_SKIPSONGS * -1)
				event = None
			elif player and event.key_code == 336:  # shift-<down>
				player.skip_songs( config.LMS_SKIPSONGS)
				event = None
			elif player and event.key_code == -200:  # pos1
				player.playlist_play_idx( 0)
				event = None
			elif player and event.key_code == Screen.KEY_PAGE_UP:
				player.skip_album( num=max( 1, self._keyprefix), forward=False)
				event = None
			elif player and event.key_code == Screen.KEY_PAGE_DOWN:
				player.skip_album( num=max( 1, self._keyprefix), forward=True)
				event = None
			elif player and event.key_code == Screen.KEY_RIGHT:
				player.seek( config.LMS_SEEKDUR)
				event = None
			elif player and event.key_code == Screen.KEY_LEFT:
				player.seek( config.LMS_SEEKDUR * -1)
				event = None
			elif player and event.key_code in range( 49, 58):  # 1-9
				self._keyprefix = event.key_code - 48
				keep_keyprefix = True
				#_LOGGER.debug("_keyprefix: {}".format( self._keyprefix))
			elif player and event.key_code == 103:  # g
				raise NextScene("PlaylistGo")
				event = None
			elif player and event.key_code == 102:  # f
				self._scene.add_effect( Favorites( self.screen, self.lms))
				event = None
			elif player and event.key_code == 112:  # p
				self._scene.add_effect( Playlists( self.screen, self.lms))
				event = None
			elif player and event.key_code == 70:  # F
				self._scene.add_effect( FilterPlaylist( self.screen, self.lms))
				event = None
			elif player and event.key_code == 109:  # m
				self._scene.add_effect( HomeMenu( self.screen, self.lms))
				event = None
			elif player and event.key_code == Screen.KEY_F1:
				raise NextScene("Help")
			elif event.key_code == 113:  # q
				raise StopApplication("User requested exit")
			# cr = -205 cl = -203 cu=-204 cd=-206 + = 43 - = 45 pgd = -208 pgup = -207 pos1 = -200 1 = 49 9 = 57
			else:
				_LOGGER.debug( "form key event: {}".format( event.key_code))

			if not keep_keyprefix:
				self._keyprefix = 0

		return super(MainFrame, self).process_event(event)

	def force_update( self):
#		self._screen.refresh()
		if not self._suspend_updates:
			#_LOGGER.debug( "force_update")
			self._screen.force_update()

	def _theme_selected( self):
		#_LOGGER.debug("_theme_selected: pop:{}".format( repr( self._popuptheme)))
		if self._popuptheme:
			_LOGGER.debug("_theme_selected: pop val:{}".format( repr( self._popuptheme.get_selected_value())))
			val, but = self._popuptheme.get_selected_value()
			if val and ( ( but and but == 0) or not but):
				config.APP_THEME = val
				self.set_theme( val)

	def _select_player( self):
		if self.lms.players:
			options = []
			for p in self.lms.players:
				o = p.get_name() + " [" + p.get_player_id() + "]"
				#o = str( p)
				options.append( ( o, p.get_player_id()))
			if not self._popupplayers:
				self._popupplayers = PopupMenuExt( self.screen, "Select Player", options, ["Select", "Close"], callback=self._player_selected)
			else:
				self._popupplayers.set_options( options)
			self._popupplayers.set_theme( config.APP_THEME)
			self._scene.add_effect( self._popupplayers)
			return True
		return False

	def _player_selected( self):
		#_LOGGER.debug("_player_selected: pop:{}".format( repr( self._popupplayers)))
		if self._popupplayers:
			_LOGGER.debug("_player_selected: pop val:{}".format( repr( self._popupplayers.get_selected_value())))
			val, but = self._popupplayers.get_selected_value()
			if val and ( ( but and but == 0) or not but):
				config.LMS_CURRPLAYER = val

	def _quit(self):
		self._scene.add_effect(
			PopUpDialog(self._screen,
						"Are you sure?",
						["Yes", "No"],
						has_shadow=True,
						on_close=self._quit_on_yes))

	@staticmethod
	def _quit_on_yes(selected):
		# Yes is the first button
		if selected == 0:
			raise StopApplication("User requested exit")
