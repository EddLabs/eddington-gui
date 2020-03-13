from tkinter import CENTER

import toga
from toga.style import Pack
from toga.style.pack import ROW

from eddington_gui.consts import LINE_HEIGHT


class LineBox(toga.Box):
    def __init__(self,):
        super(LineBox, self).__init__(
            style=Pack(
                direction=ROW,
                height=LINE_HEIGHT,
                alignment=CENTER,
                padding_top=2,
                padding_bottom=2,
            )
        )
