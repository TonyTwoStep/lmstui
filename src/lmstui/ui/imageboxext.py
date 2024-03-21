import logging, subprocess

from PIL import Image
import requests
from wcwidth import wcwidth, wcswidth

from asciimatics.renderers import ColourImageFile
from asciimatics.widgets import Widget
from asciimatics.screen import Screen, _DoubleBuffer

from lmstui.ui.colourimage import ColourImage

_LOGGER = logging.getLogger(__name__)

class ImageBoxExt( Widget):

	def __init__(self, image, id, height=1):
		super(ImageBoxExt, self).__init__(None, tab_stop=False)
#		self._required_height = height  # Widget.FILL_FRAME
		self._required_height = Widget.FILL_COLUMN
		self._image = image
		self._id = id
		self._currid = None
		self._origbuf = None

	def process_event(self, event):
		return event

	def update(self, frame_no):
		if self._image is None:
			return

		if self._origbuf is None:
			self._origbuf = _DoubleBuffer( self._h, self._w)

			'''
			i = 0
			for y in range( self._y, self._h):
				slice = self.frame.canvas._buffer.slice( self._x, y, self._w)
				self._origbuf.block_transfer( slice, 0, i)
				i += 1
			'''

		is_new_image = True
		if self._currid is not None and ( self._currid == self._id):
			is_new_image = False
		_LOGGER.debug("is_new_image: {} id: {} cid: {}".format( is_new_image, self._id, self._currid))

		if is_new_image or self._timg is None:
			self._timg = None
			cmd = ["chafa", "--colors=full", "--work=9", "--size={}x{}".format( self._w - 2, self._h - 2), "-"]
			with subprocess.Popen( cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE) as proc:
				(stdout_data, stderr_data) = proc.communicate( input=self._image, timeout=5)
				if stderr_data:
					_LOGGER.error("stderr_data: {} ".format( stderr_data))
			self._timg = stdout_data.decode( "utf-8")
			#_LOGGER.debug("stdout_data: {} timg: {}".format( len( stdout_data), len(self._timg)))
			self._currid = self._id
			#self.frame.canvas.

		if self._timg is not None:
			colour = self.frame.canvas._screen._colour
			attr = self.frame.canvas._screen._attr
			bg = self.frame.canvas._screen._bg
			#img_w = len( self._timg[1:])
			#off_x = 2  # ( (self._w - img_w) // 4)
			#_LOGGER.debug("x:{} y:{} w:{} h:{} imgw:{} off_x:{}".format( self._x, self._y, self._w, self._h, img_w, off_x))
			_LOGGER.debug("x:{} y:{} w:{} h:{} dx:{} dy:{}".format( self._x, self._y, self._w, self._h, self.frame.canvas._dx, self.frame.canvas._dy))
			#_LOGGER.debug("dx:{} dy:{}".format( self.frame.canvas._dx, self.frame.canvas._dy))

			fx = self.frame.canvas._dx + self._x + 1
			fy = self.frame.canvas._dy + self._y
			tl = self._timg.splitlines()

			'''
			if len( tl) < self._h:
				_LOGGER.debug(" h:{} > imgh:{}".format( self._h, len( tl)))
				_LOGGER.debug("hx:{} hy:{} hw:{} hh:{}".format( self._x + 1, len( tl), self._w - 2, self._h - 2 - len( tl)))
				text = "█" * (self._w - 1)
				#for y in range( len( tl), self._h):
				for y in range( self._y, self._h + 1):
					self.frame.canvas.print_at(text, self._x + 1, y, colour=Screen.COLOUR_RED, attr=attr, bg=Screen.COLOUR_GREEN, transparent=False)
				#self.frame.canvas._screen.fill_polygon( [ (fx, fy), (fx + self._w, fy), (fx + self._w, fy + self._h), (fx, fy + self._h)], colour=Screen.COLOUR_RED, bg=Screen.COLOUR_GREEN)
				#self.frame.canvas.highlight( self._x + 1, len( tl), self._w - 2, self._h - 2 - len( tl), fg=Screen.COLOUR_RED, bg=Screen.COLOUR_GREEN)
				#self.frame.canvas.highlight( self._x + 1, self._y, self._w - 2, self._h - 2, fg=Screen.COLOUR_RED, bg=Screen.COLOUR_GREEN)
				#self.frame.canvas.refresh( )

			if len( tl) < self._h:
				blank = "X" * (self._w - 1)
				for y in range( 0,  self._h - len( tl)):
					self.frame.canvas._screen.print_at( blank, fx, fy + len(tl) + y, colour=Screen.COLOUR_RED, bg=Screen.COLOUR_GREEN)
			'''

			#self.frame.canvas._buffer.block_transfer( self._origbuf[0][self._x:self._y - len( tl)], self._x, self._y + len( tl))

			for y, t in enumerate( tl):
				self.frame.canvas._screen._print_at( t, fx, fy + y, 1)

			#self._h = len( tl)
			#self._required_height = len( tl)

			self.frame.canvas._screen._change_colours( 0, 0, 0)
			self.frame.canvas._screen._change_colours( colour, attr, bg)

	def reset(self):
		pass

	def required_height(self, offset, width):
		return self._required_height

	def set_image( self, image, id):
		self._image = image
		self._id = id

	def load_image( self, url):
		response = requests.get( url, stream=True)
		self._image = response.raw.read()
		self._id = url

	@property
	def value(self):
		return self._value
