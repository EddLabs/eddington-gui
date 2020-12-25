"""Window for choosing record to use in fit data."""
import itertools
from typing import Callable, Dict, List, Tuple

import toga
from eddington import FittingData, to_relevant_precision_string
from eddington.statistics import Statistics
from toga.style import Pack
from toga.style.pack import COLUMN
from travertino.constants import BOLD

from eddington_gui.boxes.line_box import LineBox
from eddington_gui.consts import (
    COLUMN_WIDTH,
    LINE_HEIGHT,
    RECORD_WINDOW_SIZE,
    SMALL_PADDING,
    TITLES_LINE_HEIGHT,
    FontSize,
)


class RecordsChoiceWindow(toga.Window):  # pylint: disable=too-few-public-methods
    """Window for choosing which records to consider when using fit data."""

    __fitting_data: FittingData
    __save_action: Callable
    __all_checkbox: toga.Switch
    __checkboxes: List[toga.Switch]
    __statistics_labels: Dict[Tuple[str, str], toga.Label]

    def __init__(self, fitting_data: FittingData, font_size: FontSize, app: toga.App):
        """Initialize window."""
        super().__init__(title="Choose Records", size=RECORD_WINDOW_SIZE)
        self.__fitting_data = fitting_data
        main_box = toga.Box(style=Pack(direction=COLUMN))
        data_box = toga.Box()
        statistics_box = toga.Box()
        font_size_value = FontSize.get_font_size(font_size)
        self.__statistics_labels = {
            (column, parameter): toga.Label(
                text=to_relevant_precision_string(
                    getattr(fitting_data.statistics(column), parameter, 0)
                ),
                style=Pack(
                    height=LINE_HEIGHT, width=COLUMN_WIDTH, font_size=font_size_value
                ),
            )
            for column, parameter in itertools.product(
                fitting_data.all_columns, Statistics.parameters()
            )
        }
        self.__checkboxes = [
            toga.Switch(
                label="",
                is_on=fitting_data.is_selected(i),
                on_toggle=self.select_records,
                style=Pack(
                    height=LINE_HEIGHT, width=COLUMN_WIDTH, font_size=font_size_value
                ),
            )
            for i in range(1, fitting_data.length + 1)
        ]
        self.__all_checkbox = toga.Switch(
            label="",
            is_on=self.are_all_selected(),
            on_toggle=self.select_all,
            style=Pack(
                height=TITLES_LINE_HEIGHT, width=COLUMN_WIDTH, font_size=font_size_value
            ),
        )
        data_box.add(
            toga.Box(
                style=Pack(
                    flex=1,
                    direction=COLUMN,
                    padding_left=SMALL_PADDING,
                    padding_right=SMALL_PADDING,
                ),
                children=[
                    toga.Box(
                        style=Pack(
                            height=LINE_HEIGHT,
                            width=COLUMN_WIDTH,
                            font_size=font_size_value,
                        ),
                        children=[self.__all_checkbox],
                    ),
                    *self.__checkboxes,
                ],
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
                    children=[
                        toga.Label(
                            text=header,
                            style=Pack(
                                height=TITLES_LINE_HEIGHT,
                                width=COLUMN_WIDTH,
                                font_size=font_size_value,
                                font_weight=BOLD,
                            ),
                        ),
                        *[
                            toga.Label(
                                text=to_relevant_precision_string(element),
                                style=Pack(
                                    height=LINE_HEIGHT,
                                    width=COLUMN_WIDTH,
                                    font_size=font_size_value,
                                ),
                            )
                            for element in column
                        ],
                    ],
                )
            )
        main_box.add(data_box)
        main_box.add(toga.Divider())
        statistics_box.add(
            toga.Box(
                style=Pack(
                    flex=1,
                    direction=COLUMN,
                    padding_left=SMALL_PADDING,
                    padding_right=SMALL_PADDING,
                ),
                children=[
                    toga.Label(
                        text=parameter.replace("_", " ").title(),
                        style=Pack(
                            height=LINE_HEIGHT,
                            width=COLUMN_WIDTH,
                            font_size=font_size_value,
                            font_weight=BOLD,
                        ),
                    )
                    for parameter in Statistics.parameters()
                ],
            )
        )
        for header, column in fitting_data.data.items():
            statistics_box.add(
                toga.Box(
                    style=Pack(
                        flex=1,
                        direction=COLUMN,
                        padding_left=SMALL_PADDING,
                        padding_right=SMALL_PADDING,
                    ),
                    children=[
                        self.__statistics_labels[(header, parameter)]
                        for parameter in Statistics.parameters()
                    ],
                )
            )
        main_box.add(statistics_box)
        main_box.add(
            LineBox(
                children=[toga.Button(label="Close", on_press=lambda _: self.close())],
            )
        )
        scroller = toga.ScrollContainer(content=main_box)
        self.content = scroller
        self.app = app

    def select_records(self, widget):  # pylint: disable=unused-argument
        """Set selected records to fitting data."""
        for i in range(self.__fitting_data.length):
            if self.__checkboxes[i].is_on:
                self.__fitting_data.select_record(i + 1)
            else:
                self.__fitting_data.unselect_record(i + 1)
        self.__all_checkbox.is_on = self.are_all_selected()
        self.update_statistics()
        self.app.reset_fitting_result()

    def select_all(self, widget):  # pylint: disable=unused-argument
        """Select/Deselect all records to fitting data."""
        if self.__all_checkbox.is_on:
            for checkbox in self.__checkboxes:
                checkbox.is_on = True
        elif self.are_all_selected():
            for checkbox in self.__checkboxes:
                checkbox.is_on = False

    def update_statistics(self):
        """Update statistics at the bottom of the window."""
        for header in self.__fitting_data.all_columns:
            for parameter in Statistics.parameters():
                text = to_relevant_precision_string(
                    getattr(self.__fitting_data.statistics(header), parameter, 0)
                )
                self.__statistics_labels[(header, parameter)].text = text

    def are_all_selected(self):
        """Informs whether all records are selected."""
        return all([checkbox.is_on for checkbox in self.__checkboxes])
