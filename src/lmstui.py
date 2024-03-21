#!/usr/bin/env python3
# encoding: utf-8
'''
LMS TUI Remote

@author:     R.S.U.
@copyright:  2020 R.S.U. All rights reserved.
@license:    GPL v3
@contact:    https://www.nexus0.net/pub/sw/lmstui
'''

import sys, os, logging, time, configparser, textwrap, tempfile, re, pathlib

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

from asciimatics.widgets import Frame, TextBox, Layout, Label, Divider, Text, CheckBox, RadioButtons, Button, PopUpDialog, TimePicker, DatePicker, Background, DropdownList, PopupMenu
from asciimatics.event import MouseEvent
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError, NextScene, StopApplication, InvalidFields
from asciimatics.renderers import ColourImageFile
from asciimatics.widgets import THEMES

from lmstui.utils import config
from lmstui.lms.server import LMSServer
from lmstui.lms.worker import LMSWorker
from lmstui.ui.mainframe import MainFrame
from lmstui.ui.playlist import Playlist
from lmstui.ui.helpdialog import HelpDialog

__all__ = []
__version__ = '0.0.1'
__date__ = '2020-01-21'
__updated__ = '2020-02-03'

DEBUG = 1
TESTRUN = 0
PROFILE = 0

_LOGGER = logging.getLogger(__name__)

def startMain(screen, scene):
	lms = LMSServer( config.LMS_SERVERNAME, config.LMS_SERVERPORT)
	if not lms.update():
		screen.print_at( config.ICON_warn + " Failed to query server [{}:{}]".format( config.LMS_SERVERNAME, config.LMS_SERVERPORT), 1, 1, colour=Screen.COLOUR_RED)
		err = lms.get_lasterror()
		if err:
			for y, line in enumerate( textwrap.wrap( "Error message: " + str( err), width=screen.width - 2)):
				screen.print_at( line, 1, 3 + y)
		screen.refresh()
		screen.wait_for_input( 60)
		screen.get_event()
		return False

	THEMES['dark1'] = config.THEME_DARK1
	THEMES['darkblue'] = config.THEME_DARKBLUE
	THEMES['darkgrey'] = config.THEME_DARKGREY
	THEMES['darkturq'] = config.THEME_DARKTURQ

	config.calc_app_dims( screen)
	_LOGGER.debug( "APP_DIM_H_M {} APP_DIM_W_M {}".format( config.APP_DIM_H_M, config.APP_DIM_W_M))
	_LOGGER.debug( "APP_DIM_H_S {} APP_DIM_W_S {}".format( config.APP_DIM_H_S, config.APP_DIM_W_S))

	mf = MainFrame(screen, lms)
	pgf = Playlist( screen, lms)
	hf = HelpDialog( screen)

	lsmworker = LMSWorker( lms, screen, mf)
	lsmworker.start()
	lsmworker.unpause()

	scenes = [
		Scene([ Background( screen), mf], -1, name="Main"),
		Scene([ Background( screen), pgf], -1, name="PlaylistGo"),
		Scene([ Background( screen), hf], -1, name="Help")
	]
	try:
		screen.play( scenes, stop_on_resize=True, start_scene=scene, allow_int=True)
	finally:
		_LOGGER.debug("cleaning up LMS worker")
		lsmworker.unpause()
		lsmworker.control("exit")
		lsmworker.join()


class CLIError(Exception):
	'''Generic exception to raise and log different fatal errors.'''
	def __init__(self, msg):
		super(CLIError).__init__(type(self))
		self.msg = "E: %s" % msg

	def __str__(self):
		return self.msg

	def __unicode__(self):
		return self.msg

def main(argv=None):  # IGNORE:C0111
	'''Command line options.'''

	if argv is None:
		argv = sys.argv
	else:
		sys.argv.extend(argv)

	program_name = os.path.basename(sys.argv[0])
	program_version = "v%s" % __version__
	program_build_date = str(__updated__)
	program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
	program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
	program_license = '''%s

	LMStui v%s.
	Copyright 2020 R.S.U. GPL v3. All rights reserved.
	https://www.nexus0.net/pub/sw/lmstui

	<F1> to show key bindings

USAGE
''' % (program_shortdesc, str(__version__))

	try:
		# Setup argument parser
		parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
		parser.add_argument('-V', '--version', action='version', version=program_version_message)
		parser.add_argument('--log-level', action='store', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'], default='INFO', help="set log level (default: %(default)s)")
		parser.add_argument('--log-file', action='store', required=False, help='log file')

		parser.add_argument('--config', action='store', required=False, default=str( pathlib.Path.home()) + "/.config/lmstui.conf", help='config file location (default: %(default)s)')
		parser.add_argument('--lms', action='store', required=False, help='LMS server name')
		parser.add_argument('--lms-port', action='store', type=int, default=9000, help='LMS server port (default: %(default)s)')
		parser.add_argument('--player', action='store', required=False, help='LMS player ID. Format: 00:00:00:00:00:00')

		parser.add_argument('--geometry', action='store', required=False, help='screen size (format: <columns>x<rows> or <0.nx0.n> for percentage of screen)')

		cfgparser = configparser.ConfigParser()
		# Process arguments
		args = parser.parse_args()
		#logging.basicConfig(level=args.log_level)
		if args.log_file:
			logging.basicConfig( level=args.log_level, filename=args.log_file)
		else:
			logging.basicConfig( level=args.log_level, filename=tempfile.gettempdir() + "/lmstui.log")

		if os.path.isfile( args.config):
			_LOGGER.info("reading config file: {}".format( args.config))
			cfgparser.read( args.config)
			if "lms" in cfgparser.sections():
				#_LOGGER.info("reading config lms: {}".format( repr( cfgparser["lms"]["server"])))
				config.LMS_SERVERNAME = cfgparser["lms"]["server"] if "server" in cfgparser["lms"] else None
				config.LMS_SERVERPORT = cfgparser.getint("lms", "port") if "port" in cfgparser["lms"] else None
				config.LMS_CURRPLAYER = cfgparser["lms"]["player"] if "player" in cfgparser["lms"] else None
			if "app" in cfgparser.sections():
				cf_app = cfgparser['app']
				config.LMS_POLLINTERVAL = cfgparser.getint( "app", 'pollinterval') if "pollinterval" in cf_app else config.LMS_POLLINTERVAL
				config.LMS_VOLADJ = cfgparser.getint( "app", 'voladjust') if "voladjust" in cf_app else config.LMS_VOLADJ
				config.APP_THEME = cf_app['theme'] if "theme" in cf_app else config.APP_THEME
				config.LMS_SKIPSONGS = cfgparser.getint( "app", 'skipsongs') if "skipsongs" in cf_app else config.LMS_SKIPSONGS
				config.APP_IMAGEMODE = cf_app['imagemode'] if "imagemode" in cf_app else config.APP_IMAGEMODE

		if args.lms_port:
			config.LMS_SERVERPORT = args.lms_port
		if args.lms:
			config.LMS_SERVERNAME = args.lms
		if args.player:
			config.LMS_CURRPLAYER = args.player
		if args.geometry:
			dim_w, dim_h = args.geometry.split( "x")
			r = re.compile(r"^0\.\d*$")
			if r.match( dim_h) and r.match( dim_w):
				config.APP_DIM_W_PCT, config.APP_DIM_H_PCT = float( dim_w), float( dim_h)
			elif dim_w.isdigit() and dim_w.isdigit():
				config.APP_DIM_W_L, config.APP_DIM_H_L = int( dim_w), int( dim_h)
			else:
				_LOGGER.warn("cannot parse geometry {}".format( args.geometry))

		if config.LMS_SERVERPORT is None or config.LMS_SERVERNAME is None:
			print("Error: server name must set (either with the --lms option, or in the config file ({})".format( args.config))
			return 1

		os.environ.setdefault("ESCDELAY", "10")
		last_scene = None
		while True:
			try:
				Screen.wrapper(startMain, catch_interrupt=False, arguments=[last_scene])
				return 0
			except ResizeScreenError as e:
				_LOGGER.debug("ResizeScreen")
				config.clear_app_dims()
				last_scene = e.scene

		return 0

	except Exception as e:
		if DEBUG or TESTRUN:
			raise(e)
		indent = len(program_name) * " "
		sys.stderr.write(program_name + ": " + repr(e) + "\n")
		sys.stderr.write(indent + "  for help use --help")
		return 2


if __name__ == "__main__":
	sys.exit(main())
