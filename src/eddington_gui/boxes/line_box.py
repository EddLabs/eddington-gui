from tkinter import CENTER

import toga
from toga.style import Pack
from toga.style.pack import ROW

from eddington_gui.consts import LINE_HEIGHT, SMALL_PADDING


class LineBox(toga.Box):
    def __init__(self, children=None):
        super(LineBox, self).__init__(
            style=Pack(
                direction=ROW,
                height=LINE_HEIGHT,
                alignment=CENTER,
                padding_left=SMALL_PADDING,
                padding_right=SMALL_PADDING,
                padding_top=SMALL_PADDING,
                padding_bottom=SMALL_PADDING,
            ),
            children=children,
        )
