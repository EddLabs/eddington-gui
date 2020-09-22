"""Window for choosing record to use in fit data."""
from typing import Callable, List

import toga
from eddington import FittingData
from toga.style import Pack
from toga.style.pack import COLUMN

from eddington_gui.boxes.line_box import LineBox
from eddington_gui.consts import LINE_HEIGHT, RECORD_WINDOW_SIZE, SMALL_PADDING


class RecordsChoiceWindow(toga.Window):  # pylint: disable=too-few-public-methods
    """Window for choosing which records to consider when using fit data."""

    __save_action: Callable
    __checkboxes: List[toga.Switch]

    def __init__(self, fitting_data: FittingData, app: toga.App):
        """Initialize window."""
        super().__init__(title="Choose Records", size=RECORD_WINDOW_SIZE)
        main_box = toga.Box(style=Pack(direction=COLUMN))
        data_box = toga.Box()
        self.__checkboxes = [
            toga.Switch(
                label="",
                is_on=fitting_data.is_selected(i),
                style=Pack(height=LINE_HEIGHT),
            )
            for i in range(1, fitting_data.length + 1)
        ]
        data_box.add(
            toga.Box(
                style=Pack(
                    flex=1,
                    direction=COLUMN,
                    padding_left=SMALL_PADDING,
                    padding_right=SMALL_PADDING,
                ),
                children=[toga.Label(text="Chosen", style=Pack(height=LINE_HEIGHT))]
                + self.__checkboxes,  # noqa: W503
            )
        )
        for header, column in fitting_data.data.items():
            data_box.add(
                toga.Box(
                    style=Pack(
                        flex=1,
                        direction=COLUMN,
                        padding_left=SMALL_PADDING,
                        padding_right=SMALL_PADDING,
                    ),
                    children=[toga.Label(text=header, style=Pack(height=LINE_HEIGHT))]
                    + [  # noqa: W503
                        toga.Label(text=element, style=Pack(height=LINE_HEIGHT))
                        for element in column
                    ],
                )
            )
        main_box.add(data_box)
        main_box.add(
            LineBox(
                children=[
                    toga.Button(label="Save", on_press=self.save_action(fitting_data))
                ],
            )
        )
        scroller = toga.ScrollContainer(content=main_box)
        self.content = scroller
        self.app = app

    def save_action(self, fitting_data: FittingData):
        """Save selected records to fit data."""

        def save(widget):  # pylint: disable=unused-argument
            for i in range(fitting_data.length):
                if self.__checkboxes[i].is_on:
                    fitting_data.select_record(i + 1)
                else:
                    fitting_data.unselect_record(i + 1)
            self.close()

        return save
