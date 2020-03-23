import toga
from toga.style import Pack

from eddington_gui import __version__, __author__
from eddington_gui.boxes.line_box import LineBox
from eddington_gui.consts import SMALL_FONT_SIZE, HEADER_FONT_FAMILY


class HeaderBox(LineBox):
    def __init__(self):
        super(HeaderBox, self).__init__(
            children=[
                toga.Label(
                    text=f"Version: {__version__}",
                    style=Pack(
                        font_size=SMALL_FONT_SIZE, font_family=HEADER_FONT_FAMILY
                    ),
                ),
                toga.Box(style=Pack(flex=1)),
                toga.Label(
                    text=f"Author: {__author__}",
                    style=Pack(
                        font_size=SMALL_FONT_SIZE, font_family=HEADER_FONT_FAMILY
                    ),
                ),
            ]
        )
