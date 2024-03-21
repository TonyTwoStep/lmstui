import logging

from PIL import Image
import requests

from asciimatics.renderers import ColourImageFile
from asciimatics.widgets import Widget

from lmstui.ui.colourimage import ColourImage

_LOGGER = logging.getLogger(__name__)

class ImageBox( Widget):

	def __init__(self, image, id, height=1):
		super(ImageBox, self).__init__(None, tab_stop=False)
#		self._required_height = height  # Widget.FILL_FRAME
		self._required_height = Widget.FILL_COLUMN
		self._image = image
		self._id = id
		self._currid = None

	def process_event(self, event):
		return event

	def update(self, frame_no):
		super(ImageBox, self).update( frame_no)
		if self._image is None:
			return

		is_new_image = True
		if self._currid is not None and ( self._currid == self._id):
			is_new_image = False
		#_LOGGER.debug("is_new_image: {} id: {} cid: {}".format( is_new_image, self._id, self._currid))

		if is_new_image:
			#_LOGGER.debug("pix: w:{} h:{} ".format( self._image.size[0], self._image.size[1]))

			target_w = self._w - 1
			ratio_orig = self._image.size[0] / self._image.size[1]
			target_h = target_w / ( self._image.size[0] / self._image.size[1])
			#target_w = int( (self._image.size[0] / self._image.size[1]) * target_h)
			_LOGGER.debug("new pix: w:{} h:{} calc: target_w:{:.02f} target_h:{:.02f}".format( self._image.size[0], self._image.size[1], target_w, target_h))

			ph = min( int( ( target_h // 2) - 1), self._h)
			cif = ColourImage( self.frame.canvas._screen, self._image, height=ph, uni=True)
			self._timg, self._cmap = cif.rendered_text
			self._currid = self._id

		if self._timg is not None:
			img_h = len( self._timg[1:])
			img_w = len( self._timg[1])
			off_x = 2  # ( (self._w - img_w) // 4)
			_LOGGER.debug("x:{} y:{} w:{} h:{} imgw:{} imgh:{} off_x:{}".format( self._x, self._y, self._w, self._h, img_w, img_h, off_x))

			for i, t in enumerate( self._timg[ 1:]):
				self.frame.canvas.paint( t[:-1], self._x + off_x, self._y + i, colour_map=self._cmap[ i])

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

	@property
	def value(self):
		return self._value
