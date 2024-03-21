import logging

from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, Button, TextBox, Widget, MultiColumnListBox
from asciimatics.exceptions import ResizeScreenError, StopApplication, InvalidFields, NextScene
from asciimatics.event import KeyboardEvent, MouseEvent
from asciimatics.screen import Screen

from lmstui.utils import config

_LOGGER = logging.getLogger(__name__)

class PopupMenuExt( Frame):
	def __init__(self, screen, title, opts, buttons, callback=None, w=None, h=None, fullscreen=False):
		w, h = self.calc_dims( screen, opts, buttons, w, h)
		super(PopupMenuExt, self).__init__(screen,
										h,
										w,
										has_shadow=False,
										has_border=True,
										can_scroll=False,
										is_modal=True,
										title=title,
										name=title.replace(" ", "_"))

		self._fullscreen = fullscreen
		self._selval = None
		self._selbut = None
		self._callback = callback
		self._uilistbox = ListBox( Widget.FILL_FRAME, opts, centre=False, add_scroll_bar=True, on_select=self._select, on_change=self._change)
		layout = Layout([100], fill_frame=True)
		self.add_layout(layout)
		layout.add_widget(self._uilistbox, 0)
		layout.add_widget( Divider(height=1, draw_line=True), 0)

		numbut = len( buttons)
		layout2 = Layout([1] * (numbut))
		self.add_layout( layout2)
		for i, b in enumerate( buttons):
			mn = "func_" + b.replace(" ", "_")
			_method = self.make_method( b, i)
			setattr( self, mn, _method)
			#_LOGGER.debug( "init: i={} mn={} ".format( i, mn))
			layout2.add_widget(Button( b, _method), i)
		#layout2.add_widget(Button("Close", self._destroy), numbut)

		self._uilistbox.options = opts

		self.set_theme( config.APP_THEME)
		self.fix()

	def make_method( self, name, value):
		def _method():
			#_LOGGER.debug("method {0} in {1}".format(name, self))
			self._destroy( value=value)
		return _method

	def calc_dims( self, screen, opts, buttons, w=None, h=None):
		if h is None:
			h = min( config.APP_DIM_H_L, len( opts) + 4)
		if w is None:
			maxopt = max( [len( i[0]) for i in opts])
			butlen = sum( [len( i) for i in buttons])
			maxbut = butlen + len(buttons) * 20
			w = min( config.APP_DIM_W_L, max( maxopt, maxbut))
		return w, h

	def set_options( self, opts):
		self._uilistbox.options = opts

	def _change( self):
		self._selval = self._uilistbox.value

	def _select( self):
		_LOGGER.debug( "_select: self._uilistbox.val= {} ".format( self._uilistbox.value))
		self._selval = self._uilistbox.value
		self._destroy( value=None)

	def _destroy( self, value=None):
		self._selbut = value
		_LOGGER.debug("_destroy _selbut: {0} _selval: {1}".format( self._selbut, self._selval))
		if self._fullscreen:
			raise NextScene("Main")
		else:
			self._scene.remove_effect(self)
		if self._callback is not None:
			self._callback()

	def get_selected_value( self):
		return self._selval, self._selbut

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
			self._destroy( value=-1)
		return super( PopupMenuExt, self).process_event(event)
