from PIL import Image

from asciimatics.screen import Screen
from asciimatics.renderers import StaticRenderer, _ImageSequence

class ColourImage(StaticRenderer):
	"""
	Renderer to convert an image file (as supported by the Python Imaging
	Library) into an block image of available colours.

	.. warning::

		This is only compatible with 256-colour terminals.  Results in other
		terminals with reduced colour capabilities are severely restricted.
		Since Windows only has 8 base colours, it is recommended that you
		avoid this renderer on that platform.
	"""

	def __init__(self, screen, image, height=30, bg=Screen.COLOUR_BLACK,
					fill_background=False, uni=False, dither=False):
		"""
		:param screen: The screen to use when displaying the image.
		:param filename: The name of the file to render.
		:param height: The height of the text rendered image.
		:param bg: The default background colour for this image.
		:param fill_background: Whether to set background colours too.
		:param uni: Whether to use unicode box characters or not.
		:param dither: Whether to dither the rendered image or not.
		"""
		super(ColourImage, self).__init__()
		# Find any PNG or GIF background colour.
		background = None
		if 'background' in image.info:
				background = image.info['background']
		elif 'transparency' in image.info:
				background = image.info['transparency']

		# Convert each frame in the image.
		for frame in _ImageSequence(image):
				ascii_image = ""
				frame = frame.resize(
					(int(frame.size[0] * height * 2.0 / frame.size[1]),
					height * 2 if uni else height),
					Image.BICUBIC)
				tmp_img = Image.new("P", (1, 1))
				tmp_img.putpalette(screen.palette)

				# Avoid dithering - this requires a little hack to get directly
				# at the underlying library in PIL.
				new_frame = frame.convert('RGB')
				tmp_img.load()
				new_frame.load()
				new_frame = new_frame._new(
					new_frame.im.convert("P", 3 if dither else 0, tmp_img.im))

				# Blank out any transparent sections of the image for complex
				# images with alpha blending.
				if background is None and frame.mode == 'RGBA':
					mask = Image.eval(
						frame.split()[-1], lambda a: 255 if a <= 64 else 0)
					new_frame.paste(16, mask)

				# Decide what "brush" we're going to use for the rendering.
				brush = "▄" if uni else "#"

				# Convert the resulting image to coloured ASCII codes.
				for py in range(0, new_frame.size[1], 2 if uni else 1):
					# Looks like some terminals need a character printed before
					# they really reset the colours - so insert a dummy char
					# to reset the background if needed.
					if uni:
						ascii_image += "${%d,2,%d}." % (bg, bg)
					ascii_image += "\n"
					for px in range(0, new_frame.size[0]):
						real_col = frame.getpixel((px, py))
						real_col2 = (frame.getpixel((px, py + 1)) if uni else
											real_col)
						col = new_frame.getpixel((px, py))
						col2 = new_frame.getpixel((px, py + 1)) if uni else col
						if ((real_col == real_col2 == background) or
									(col == col2 == 16)):
								if fill_background or uni:
									ascii_image += "${%d,2,%d}." % (bg, bg)
								else:
									ascii_image += "${%d} " % bg
						else:
								if fill_background or uni:
									ascii_image += "${%d,2,%d}%s" % (col2, col,
																				brush)
								else:
									ascii_image += "${%d}#" % col
				if uni:
					ascii_image += "${%d,2,%d}." % (bg, bg)
				self._images.append(ascii_image)
