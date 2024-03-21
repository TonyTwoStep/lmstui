import logging

from asciimatics.widgets import Frame, TextBox, Layout, Divider, Button, Widget
from asciimatics.screen import Screen
from asciimatics.event import KeyboardEvent
from asciimatics.exceptions import NextScene

from lmstui.utils import config

class HelpDialog( Frame):
	def __init__(self, screen, title="Help", w=None, h=None, fullscreen=True):
		self._fullscreen = fullscreen
		if h is None:
			h = config.APP_DIM_H_L
		if w is None:
			w = config.APP_DIM_W_M
		super(HelpDialog, self).__init__(screen,
										h,
										w,
										has_shadow=False,
										has_border=True,
										can_scroll=True,
										is_modal=True,
										title=title,
										name=title.replace(" ", "_"))

		layout = Layout([100], fill_frame=True)
		self.add_layout(layout)
		tb = TextBox( Widget.FILL_FRAME, line_wrap=True, as_string=True)
		tb.value = config.APP_HELPTEXT
		tb.disabled = True
		tb.custom_colour = "edit_text"
		layout.add_widget( tb, 0)
		layout.add_widget(Divider(height=1, draw_line=True), 0)

		layout2 = Layout( [1, 1, 1])
		self.add_layout(layout2)
		layout2.add_widget(Button("Close", self._destroy), 2)
		self.set_theme( config.APP_THEME)
		self.fix()

	def update(self, frame_no):
		self.set_theme( config.APP_THEME)
		super(HelpDialog, self).update( frame_no)

	def _destroy( self, callback=None):
		if self._fullscreen:
			raise NextScene("Main")
		else:
			self._scene.remove_effect(self)
			if callback is not None:
				callback()

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
			self._destroy()
		return super( HelpDialog, self).process_event(event)
