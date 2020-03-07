from typing import List
from collections import OrderedDict

import toga
from toga.style import Pack
from toga.style.pack import ROW, COLUMN, LEFT


class DataBox(toga.Box):

    SELECTION_WIDTH = 200

    __data_frame: OrderedDict = None
    __items: List[str] = []
    __selection_enabled: bool = False

    x_selection: toga.Selection
    xerr_selection: toga.Selection
    y_selection: toga.Selection
    yerr_selection: toga.Selection

    def __init__(self):
        super(DataBox, self).__init__(style=Pack(direction=ROW, padding_top=5))
        labels_column = toga.Box(style=Pack(direction=COLUMN, flex=1))
        labels_column.add(toga.Label(text="X column:", style=Pack()))
        labels_column.add(toga.Label(text="X error column:"))
        labels_column.add(toga.Label(text="Y column:"))
        labels_column.add(toga.Label(text="Y error column:"))
        self.add(labels_column)

        self.x_selection = toga.Selection(enabled=self.selection_enabled,
                                          style=Pack(alignment=LEFT, width=self.SELECTION_WIDTH))
        self.xerr_selection = toga.Selection(enabled=self.selection_enabled,
                                             style=Pack(alignment=LEFT, width=self.SELECTION_WIDTH))
        self.y_selection = toga.Selection(enabled=self.selection_enabled,
                                          style=Pack(alignment=LEFT, width=self.SELECTION_WIDTH))
        self.yerr_selection = toga.Selection(enabled=self.selection_enabled,
                                             style=Pack(alignment=LEFT, width=self.SELECTION_WIDTH))
        self.add(toga.Box(style=Pack(direction=COLUMN, flex=2),
                          children=[self.x_selection, self.xerr_selection, self.y_selection, self.yerr_selection]))

    @property
    def items(self):
        return self.__items

    @items.setter
    def items(self, items):
        self.__items = items
        self.x_selection.items = items
        self.xerr_selection.items = items
        self.y_selection.items = items
        self.yerr_selection.items = items

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

    @property
    def data_frame(self):
        return self.__data_frame

    @data_frame.setter
    def data_frame(self, data_frame):
        self.__data_frame = data_frame
        if data_frame is None:
            self.items = []
            self.selection_enabled = False
        else:
            self.items = list(data_frame.keys())
            self.selection_enabled = True
