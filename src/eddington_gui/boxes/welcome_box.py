"""The first box that opens when opening the application."""
from pathlib import Path
from tkinter.constants import CENTER
from typing import Callable

import toga
from toga.style import Pack
from travertino.constants import COLUMN, ROW

from eddington_gui.boxes.eddington_box import EddingtonBox
from eddington_gui.boxes.footer_box import FooterBox
from eddington_gui.consts import LOGO_SIZE, FontSize


class WelcomeBox(EddingtonBox):
    """Box for welcoming users."""

    def __init__(self, on_start: Callable[[], None]):
        """Constructor."""
        super().__init__(style=Pack(direction=ROW, alignment=CENTER))
        left_side = self.build_left_side(on_start=on_start)
        right_side = self.build_right_side()
        self.add(left_side, right_side)

    @classmethod
    def build_left_side(cls, on_start: Callable[[], None]):
        """Build the left side of the welcome box."""
        return EddingtonBox(
            style=Pack(flex=1, direction=COLUMN),
            children=[
                EddingtonBox(style=Pack(flex=1)),
                EddingtonBox(
                    style=Pack(direction=ROW, alignment=CENTER),
                    children=[
                        EddingtonBox(style=Pack(flex=1)),
                        toga.Button("Start", on_press=lambda _: on_start()),
                        EddingtonBox(style=Pack(flex=1)),
                    ],
                ),
                EddingtonBox(style=Pack(flex=1)),
            ],
        )

    @classmethod
    def build_right_side(cls):
        """Build the right side of the welcome box."""
        logo_path = Path(__file__).parent.parent / "resources" / "eddington_gui.png"
        logo = toga.Image(str(logo_path))
        return EddingtonBox(
            style=Pack(direction=COLUMN, alignment=CENTER, flex=1),
            children=[
                EddingtonBox(style=Pack(flex=1)),
                toga.ImageView(
                    image=logo,
                    style=Pack(height=LOGO_SIZE, width=LOGO_SIZE, alignment=CENTER),
                ),
                EddingtonBox(
                    style=Pack(direction=ROW, alignment=CENTER),
                    children=[
                        toga.Label(
                            "Welcome to Eddington!"
                        ),
                    ],
                ),
                EddingtonBox(style=Pack(flex=1)),
                FooterBox(),
            ],
            fix_font_size=True
        )
