"""Header box of the app."""

import toga
from toga.style import Pack
from toga.style.pack import TOP

from eddington_gui import __author__, __year__
from eddington_gui.boxes.line_box import LineBox
from eddington_gui.consts import FOOTER_FONT_FAMILY, SMALL_FONT_SIZE


class FooterBox(LineBox):  # pylint: disable=too-few-public-methods
    """
    Header box of the app.

    This box containing the logo of Eddington, version number and the author name.
    """

    def __init__(self):
        """Initialize box."""
        super().__init__(
            alignment=TOP,
        )
        footer_text = f"Copyright \u00a9 {__year__} {__author__}. All rights reserved"
        self.add(
            toga.Box(style=Pack(flex=1)),
            toga.Label(
                text=footer_text,
                style=Pack(font_size=SMALL_FONT_SIZE, font_family=FOOTER_FONT_FAMILY),
            ),
        )
