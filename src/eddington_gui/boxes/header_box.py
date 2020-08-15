"""Header box of the app."""
from pathlib import Path

import toga
from toga.style import Pack
from toga.style.pack import TOP

from eddington_gui import __version__, __author__
from eddington_gui.boxes.line_box import LineBox
from eddington_gui.consts import SMALL_FONT_SIZE, HEADER_FONT_FAMILY, LOGO_SIZE


class HeaderBox(LineBox):  # pylint: disable=too-few-public-methods
    """
    Header box of the app.

    This box containing the logo of Eddington, version number and the author name.
    """

    def __init__(self):
        """Initialize box."""
        logo_path = Path(__file__).parent.parent / "resources" / "eddington_gui.png"
        logo = toga.Image(str(logo_path))
        super(HeaderBox, self).__init__(
            alignment=TOP,
            children=[
                toga.Label(
                    text=f"Version: {__version__}",
                    style=Pack(
                        font_size=SMALL_FONT_SIZE, font_family=HEADER_FONT_FAMILY
                    ),
                ),
                toga.Box(style=Pack(flex=1)),
                toga.ImageView(
                    image=logo, style=Pack(height=LOGO_SIZE, width=LOGO_SIZE)
                ),
                toga.Box(style=Pack(flex=1)),
                toga.Label(
                    text=f"Author: {__author__}",
                    style=Pack(
                        font_size=SMALL_FONT_SIZE, font_family=HEADER_FONT_FAMILY
                    ),
                ),
            ],
        )
