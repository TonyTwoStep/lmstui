from collections import defaultdict
import logging

_LOGGER = logging.getLogger(__name__)

LMS_SERVERNAME = None
LMS_SERVERPORT = 9000
LMS_CURRPLAYER = ""
LMS_TIMEOUT = 30
LMS_POLLINTERVAL = 3
LMS_MAXLEN = 999
LMS_VOLADJ = 2
LMS_SKIPSONGS = 5
LMS_SEEKDUR = 20

APP_THEME = "default"
APP_IMAGEMODE = "asciimatics"
APP_HELPTEXT = '''
key bindings
------------

<space>      play / pause
<up>         previous song
<down>       next song
<s><down>    back {num_skipsong} songs
<s><up>      forward {num_skipsong} songs
<pgup>       skip forward n albums
<pgdown>     skip back n albums
<left>       back {num_seek} seconds
<right>      forward {num_seek} seconds
<home>       go to first track
[1-9]        prefix for <up> / <down> / <pgup> / <pgdown>
+/-          volume +/- {num_voladj} step(s)

p        playlists
f        favorites
g        go to track
m        LMS menu
F        filter playlist
q        quit

^p       select player
^t       select theme

<ESC>    close form
<TAB>    focus next element
'''.format( num_skipsong=LMS_SKIPSONGS, num_voladj=LMS_VOLADJ, num_seek=LMS_SEEKDUR)
APP_DIM_H_L = None
APP_DIM_W_L = None
APP_DIM_H_PCT = 1
APP_DIM_W_PCT = 1

def calc_app_dims( screen):
	global APP_DIM_H_L, APP_DIM_W_L, APP_DIM_H_M, APP_DIM_W_M, APP_DIM_H_S, APP_DIM_W_S
	APP_DIM_H_L = int( screen.height * APP_DIM_H_PCT) if APP_DIM_H_L is None else APP_DIM_H_L
	APP_DIM_W_L = int( screen.width * APP_DIM_W_PCT) if APP_DIM_W_L is None else APP_DIM_W_L
	_LOGGER.debug("calc_app_dims APP_DIM_H_L: {} APP_DIM_W_L: {}".format( APP_DIM_H_L, APP_DIM_W_L))
	APP_DIM_H_M = int(APP_DIM_H_L * 2 // 3)
	APP_DIM_W_M = int(APP_DIM_W_L * 2 // 3)
	APP_DIM_H_S = int(APP_DIM_H_L * 2 // 4)
	APP_DIM_W_S = int(APP_DIM_W_L * 2 // 4)

def clear_app_dims( ):
	global APP_DIM_H_L, APP_DIM_W_L
	APP_DIM_H_L = None
	APP_DIM_W_L = None


# https://en.wikibooks.org/wiki/Unicode/List_of_useful_symbols

#ICON_sep = "\u2595"
ICON_sep = "\u2502"  # 2503 2506 250A

ICON_speaker = "\uf9c2"
ICON_artist = "\uf007"
ICON_artists = "\uf0c0"
# uni: 266B 266C
#ICON_music = "\uf001"
#ICON_music = "\uf883"
#ICON_music2 = "\uf888"
ICON_music = "\ufc58"
ICON_disc = "\ue271"
ICON_thermometer_0 = "\uf2cb"
ICON_thermometer_1 = "\uf2ca"
ICON_thermometer_2 = "\uf2c9"
ICON_thermometer_3 = "\uf2c8"
ICON_thermometer_4 = "\uf2c7"
ICON_thumbs_o_up = "\uf087"
ICON_thumbs_o_down = "\uf088"
ICON_info = "\uf05a"  # f449 f129
ICON_volume = "\uf028"  # f027
ICON_eye = "\uf06e"
ICON_calendar = "\uf073"  # f133
ICON_clock = "\uf017"  # f64f f017
ICON_dot = "\uf444"
ICON_square = "\uf445"
ICON_control_play = "\uf04b"  # f144
ICON_control_play_pause = "\uf90d"
ICON_control_pause = "\uf04c"  # f28b
ICON_control_stop = "\uf04d"  # f28d
ICON_repeat_on = "\uf955"
ICON_repeat_once = "\uf957"
ICON_repeat_off = "\uf956"
ICON_shuffle_on = "\uf99c"
ICON_shuffle_off = "\uf99d"
ICON_power_on = "\uf011"
ICON_power_off = "\u2b58"
ICON_question = "\uf128"
ICON_warn = "\uf071"
ICON_folder = "\ue5ff"  # e5fe f07c
ICON_arrow_right = "\uf061"  # f178 f432
ICON_list = "\uf03a"  # f778 f910 f451
ICON_search = "\uf002"  # f422

#ICON_artist = "\ufd01"
ICON_user = "\uf007"
ICON_user_circle = "\uf2bd"
ICON_user_plus = "\uf234"
ICON_audiofile = "\uf1c7"
ICON_circle = "\uf10c"
ICON_bullseye = "\uf140"
ICON_details = "\uf1f8"
ICON_control_prev = "\uf04a"
ICON_control_next = "\uf04e"
ICON_check_square_o = "\uf046"
ICON_check_square = "\uf14a"
ICON_check = "\uf00c"
ICON_plus = "\uf067"
ICON_plus_circle = "\uf055"
ICON_database = "\uf1c0"
ICON_filter = "\uf0b0"
ICON_bolt = "\uf0e7"

TRACKINFO_ALL = [ ('title', ICON_music), ('artist', ICON_artist), ('album', ICON_disc), ('year', ICON_calendar), ('genre', ICON_info), ('duration', ICON_clock), ('bitrate', ICON_info)]  # 'rating' 'tracknum'


# https://github.com/altercation/solarized/tree/master/mutt-colors-solarized

# 33 / 75 blue
# 37 / 117 turqois
# 88 / 124 / 196  red
# 244 / 245 grey

THEME_focuscol = 159

THEME_DARK1 = defaultdict(
	lambda: (69, 0, 234),
	{
		"invalid": (160, 0, 234),
		"label": (244, 0, 234),
		"title": (255, 0, 234),
		"selected_focus_field": ( THEME_focuscol, 0, 234),
		"focus_edit_text": ( THEME_focuscol, 0, 234),
		"focus_button": ( THEME_focuscol, 0, 234),
		"selected_focus_control": ( THEME_focuscol, 0, 234),
		"disabled": (33, 0, 234),
	}
)
THEME_DARKTURQ = defaultdict(
	lambda: (80, 0, 234),
	{
		"invalid": (160, 0, 234),
		"label": (244, 0, 234),
		"title": (255, 0, 234),
		"selected_focus_field": ( 159, 0, 234),
		"focus_edit_text": ( 159, 0, 234),
		"focus_button": ( 159, 0, 234),
		"selected_focus_control": ( 159, 0, 234),
		"disabled": (33, 0, 234),
	}
)
THEME_DARKGREY = defaultdict(
	lambda: (246, 0, 234),
	{
		"invalid": (160, 0, 234),
		"label": (250, 0, 234),
		"title": (255, 0, 234),
		"selected_focus_field": ( 124, 0, 234),
		"focus_edit_text": ( 124, 0, 234),
		"focus_button": ( 124, 0, 234),
		"selected_focus_control": ( 124, 0, 234),
		"disabled": (33, 0, 234),
	}
)
THEME_DARKBLUE = defaultdict(
	lambda: (33, 0, 234),
	{
		"invalid": (160, 0, 234),
		"label": (111, 0, 234),
		"title": (111, 0, 234),
		"selected_focus_field": ( 75, 0, 234),
		"focus_edit_text": ( 75, 0, 234),
		"focus_button": ( 75, 0, 234),
		"selected_focus_control": ( 75, 0, 234),
		"disabled": (33, 0, 234),
	}
)
'''
THEME_DARK1 = defaultdict(
	lambda: (37, 0, 234),
	{
		"invalid": (160, 0, 234),
		"label": (244, 0, 234),
		"title": (245, 0, 234),
		"selected_focus_field": (33, 0, 234),
		"focus_edit_text": (33, 0, 234),
		"focus_button": (33, 0, 234),
		"selected_focus_control": (33, 0, 234),
		"disabled": (33, 0, 234),
	}
)
'''
