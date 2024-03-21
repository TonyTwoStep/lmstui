import logging
import sys
from base64 import standard_b64encode

from PIL import Image
import requests

from asciimatics.renderers import ColourImageFile
from asciimatics.widgets import Widget

from lmstui.ui.colourimage import ColourImage

_LOGGER = logging.getLogger(__name__)

class ImageBoxKitty( Widget):

	def __init__(self, image, id, height=1):
		super(ImageBoxKitty, self).__init__(None, tab_stop=False)
#		self._required_height = height  # Widget.FILL_FRAME
		self._required_height = Widget.FILL_COLUMN
		self._image = image
		self._id = id
		self._currid = None

	def process_event(self, event):
		return event

	def update(self, frame_no):
		if self._image is None:
			return

		is_new_image = True
		if self._currid is not None and ( self._currid == self._id):
			is_new_image = False
		_LOGGER.debug("is_new_image: {} id: {} cid: {}".format( is_new_image, self._id, self._currid))

		'''
		if is_new_image:
			_LOGGER.debug("pix: w:{} h:{} ".format( self._image.size[0], self._image.size[1]))
			_LOGGER.debug("calc: pw/ww:{:.02f} ph/wh:{} ".format( self._image.size[0] / self._w, self._image.size[1] / self._h))
			#rw = pimg.size[0] / self._w
			#rh = pimg.size[1] / self._h
			rw = self._w / self._image.size[0]
			rh = self._h / self._image.size[1]
			_LOGGER.debug("calc: rw:{:.02f} rh:{} ".format( rw, rh))
			#new_height = new_width * height / width 
			pw = (self._w // 2) -2
			cif = ColourImage( self.frame.canvas._screen, self._image, height=pw, uni=True)
			self._timg, self._cmap = cif.rendered_text
			self._currid = self._id

		if self._timg is not None:
			img_w = len( self._timg[1:])
			off_x = 2  # ( (self._w - img_w) // 4)
			_LOGGER.debug("x:{} y:{} w:{} h:{} imgw:{} off_x:{}".format( self._x, self._y, self._w, self._h, img_w, off_x))

			for i, t in enumerate( self._timg[1:]):
				self.frame.canvas.paint( t[:-1], self._x + off_x, self._y + i, colour_map=self._cmap[i])
		'''

		ir = self._image.height / self._image.width
		tr = self._h
		tc = 20  # (tr * ir)

		if self._image.mode is "L":
			self._image = self._image.convert( mode="RGB")
		iform = None
		if self._image.mode is "RGB":
			iform = 24
		elif self._image.mode is "RGBA":
			iform = 32

		self._frame.canvas._screen.move( self._x, self._y)
		sys.stdout.buffer.write( self.serialize_gr_command( {'a': 'd'}))
		self.write_chunked({'a': 'T', 'f': iform, 'X': self._x, 'Y': self._y, 'c': tc, 'r': tr, 's': self._image.width, 'v': self._image.height}, self._image.tobytes())
		#self.write_chunked({'a': 'T', 'f': iform, 'x': 10, 'y': 10, 'c': 20, 'r': 10, 's': self._image.width, 'v': self._image.height}, self._image.tobytes())

	def reset(self):
		pass

	def required_height(self, offset, width):
		return self._required_height

	def set_image( self, image, id):
		self._image = image
		self._id = id

	def load_image( self, url):
		response = requests.get( url, stream=True)
		self._image = Image.open( response.raw)
		self._id = url

	def serialize_gr_command( self, cmd, payload=None):
		cmd = ','.join('{}={}'.format(k, v) for k, v in cmd.items())
		ans = []
		w = ans.append
		w(b'\033_G'), w(cmd.encode('ascii'))
		if payload:
			w(b';')
			w(payload)
		w(b'\033\\')
		return b''.join(ans)

	def write_chunked( self, cmd, data):
		data = standard_b64encode(data)
		while data:
			chunk, data = data[:4096], data[4096:]
			m = 1 if data else 0
			cmd['m'] = m
			sys.stdout.buffer.write( self.serialize_gr_command(cmd, chunk))
			#sys.stdout.flush()
			cmd.clear()

	@property
	def value(self):
		return self._value
