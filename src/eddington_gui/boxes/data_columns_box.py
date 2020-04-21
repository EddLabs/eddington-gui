from typing import List, Union

import toga
from eddington_core import FitData
from toga.style import Pack
from toga.style.pack import COLUMN, LEFT

from eddington_gui.boxes.line_box import LineBox
from eddington_gui.consts import SELECTION_WIDTH, LABEL_WIDTH
from eddington_gui.util import value_or_none


class DataColumnsBox(toga.Box):

    __items: List[str] = []
    __selection_enabled: bool = False

    x_selection: toga.Selection
    xerr_selection: toga.Selection
    y_selection: toga.Selection
    yerr_selection: toga.Selection

    __fit_data: Union[FitData] = None
    __handlers = []

    def __init__(self, flex):
        super(DataColumnsBox, self).__init__(style=Pack(direction=COLUMN, flex=flex))

        self.x_selection = self.__add_column_option(
            label="X column:", on_select=self.select_x
        )
        self.xerr_selection = self.__add_column_option(
            label="X error column:", on_select=self.select_xerr
        )
        self.y_selection = self.__add_column_option(
            label="Y column:", on_select=self.select_y
        )
        self.yerr_selection = self.__add_column_option(
            label="Y error column:", on_select=self.select_yerr
        )

    @property
    def fit_data(self):
        return self.__fit_data

    @fit_data.setter
    def fit_data(self, fit_data: FitData):
        self.__fit_data = fit_data
        if fit_data is None:
            self.items = []
            self.selection_enabled = False
            return
        self.items = list(fit_data.data.keys())
        self.selection_enabled = True
        self.x_selection.value = self.fit_data.x_column
        self.xerr_selection.value = self.fit_data.xerr_column
        self.y_selection.value = self.fit_data.y_column
        self.yerr_selection.value = self.fit_data.yerr_column

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

    def select_x(self, widget):
        self.fit_data.x_column = self.x_selection.value
        self.run_handlers()

    def select_xerr(self, widget):
        self.fit_data.xerr_column = self.xerr_selection.value
        self.run_handlers()

    def select_y(self, widget):
        self.fit_data.y_column = self.y_selection.value
        self.run_handlers()

    def select_yerr(self, widget):
        self.fit_data.yerr_column = self.yerr_selection.value
        self.run_handlers()

    def run_handlers(self):
        for handler in self.__handlers:
            handler(self.fit_data)

    def read_csv(self, filename):
        self.fit_data = FitData.read_from_csv(filename)

    def read_excel(self, filename, sheet):
        self.fit_data = FitData.read_from_excel(filename, sheet)

    def __add_column_option(self, label, on_select):

        selection = toga.Selection(
            enabled=self.selection_enabled,
            on_select=on_select,
            style=Pack(alignment=LEFT, width=SELECTION_WIDTH),
        )
        line = LineBox(
            alignment=LEFT,
            children=[
                toga.Label(text=label, style=Pack(width=LABEL_WIDTH)),
                selection,
            ],
        )

        self.add(line)
        return selection
