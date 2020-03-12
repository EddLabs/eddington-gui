from typing import List

import toga
from toga.style import Pack
from toga.style.pack import ROW, COLUMN, LEFT


class DataBox(toga.Box):

    SELECTION_WIDTH = 200

    __items: List[str] = []
    __selection_enabled: bool = False

    x_selection: toga.Selection
    xerr_selection: toga.Selection
    y_selection: toga.Selection
    yerr_selection: toga.Selection

    __handlers = []

    def __init__(self):
        super(DataBox, self).__init__(style=Pack(direction=COLUMN))

        columns_box = toga.Box(style=Pack(direction=ROW, padding_top=5))
        labels_column = toga.Box(style=Pack(direction=COLUMN, flex=1))
        labels_column.add(toga.Label(text="X column:", style=Pack()))
        labels_column.add(toga.Label(text="X error column:"))
        labels_column.add(toga.Label(text="Y column:"))
        labels_column.add(toga.Label(text="Y error column:"))
        columns_box.add(labels_column)

        self.x_selection = toga.Selection(enabled=self.selection_enabled, on_select=self.on_column_change,
                                          style=Pack(alignment=LEFT, width=self.SELECTION_WIDTH))
        self.xerr_selection = toga.Selection(enabled=self.selection_enabled, on_select=self.on_column_change,
                                             style=Pack(alignment=LEFT, width=self.SELECTION_WIDTH))
        self.y_selection = toga.Selection(enabled=self.selection_enabled, on_select=self.on_column_change,
                                          style=Pack(alignment=LEFT, width=self.SELECTION_WIDTH))
        self.yerr_selection = toga.Selection(enabled=self.selection_enabled, on_select=self.on_column_change,
                                             style=Pack(alignment=LEFT, width=self.SELECTION_WIDTH))
        columns_box.add(toga.Box(style=Pack(direction=COLUMN, flex=2),
                                 children=[self.x_selection, self.xerr_selection,
                                           self.y_selection, self.yerr_selection]))
        self.add(columns_box)

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
        return self.x_selection.value

    @property
    def xerr_column(self):
        return self.xerr_selection.value

    @property
    def y_column(self):
        return self.y_selection.value

    @property
    def yerr_column(self):
        return self.yerr_selection.value

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
            handler()

    def update_data_dict(self, data_dict):
        if data_dict is None:
            self.items = None
            self.selection_enabled = False
        else:
            self.items = list(data_dict.keys())
            self.selection_enabled = True
