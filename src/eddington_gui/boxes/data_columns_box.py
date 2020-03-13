from typing import List

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, LEFT

from eddington_gui.boxes.line_box import LineBox
from eddington_gui.consts import (
    X_COLUMN,
    Y_COLUMN,
    XERR_COLUMN,
    YERR_COLUMN,
    SELECTION_WIDTH,
)
from eddington_gui.util import value_or_none


class DataColumnsBox(toga.Box):

    __items: List[str] = []
    __selection_enabled: bool = False

    x_selection: toga.Selection
    xerr_selection: toga.Selection
    y_selection: toga.Selection
    yerr_selection: toga.Selection

    __handlers = []

    def __init__(self):
        super(DataColumnsBox, self).__init__(style=Pack(direction=COLUMN, flex=1))

        self.x_selection = self.__add_column_option(label="X column:")
        self.xerr_selection = self.__add_column_option(label="X error column:")
        self.y_selection = self.__add_column_option(label="Y column:")
        self.yerr_selection = self.__add_column_option(label="Y error column:")

    @property
    def items(self):
        return self.__items

    @items.setter
    def items(self, items):
        if items is None:
            items = []
        self.__items = items
        self.x_selection.items = items
        self.xerr_selection.items = items
        self.y_selection.items = items
        self.yerr_selection.items = items

    @property
    def x_column(self):
        return value_or_none(self.x_selection.value)

    @property
    def xerr_column(self):
        return value_or_none(self.xerr_selection.value)

    @property
    def y_column(self):
        return value_or_none(self.y_selection.value)

    @property
    def yerr_column(self):
        return value_or_none(self.yerr_selection.value)

    @property
    def columns(self):
        return {
            X_COLUMN: self.x_column,
            XERR_COLUMN: self.xerr_column,
            Y_COLUMN: self.y_column,
            YERR_COLUMN: self.yerr_column,
        }

    @property
    def selection_enabled(self):
        return self.__selection_enabled

    @selection_enabled.setter
    def selection_enabled(self, selection_enabled):
        self.__selection_enabled = selection_enabled
        self.x_selection.enabled = selection_enabled
        self.xerr_selection.enabled = selection_enabled
        self.y_selection.enabled = selection_enabled
        self.yerr_selection.enabled = selection_enabled

    def add_handler(self, handler):
        self.__handlers.append(handler)

    def on_column_change(self, widget):
        for handler in self.__handlers:
            handler(self.columns)

    def update_data_dict(self, data_dict):
        if data_dict is None:
            self.items = None
            self.selection_enabled = False
        else:
            self.items = list(data_dict.keys())
            self.selection_enabled = True

    def __add_column_option(self, label):

        selection = toga.Selection(
            enabled=self.selection_enabled,
            on_select=self.on_column_change,
            style=Pack(alignment=LEFT, width=SELECTION_WIDTH),
        )
        line = LineBox(
            children=[toga.Label(text=label), toga.Box(style=Pack(flex=1)), selection]
        )

        self.add(line)
        return selection
