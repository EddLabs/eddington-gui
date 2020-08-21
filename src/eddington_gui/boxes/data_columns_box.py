"""Box for choosing which columns to use in data dictionary."""
from typing import Callable, List, Union

import toga
from eddington import FitData
from toga.style import Pack
from toga.style.pack import COLUMN, LEFT

from eddington_gui.boxes.line_box import LineBox
from eddington_gui.consts import LABEL_WIDTH, SELECTION_WIDTH
from eddington_gui.util import value_or_none


class DataColumnsBox(toga.Box):  # pylint: disable=too-many-instance-attributes
    """Visual box instance for choosing columns."""

    __items: List[str] = []
    __selection_enabled: bool = False

    x_selection: toga.Selection
    xerr_selection: toga.Selection
    y_selection: toga.Selection
    yerr_selection: toga.Selection

    __fit_data: Union[FitData] = None
    __handlers: List[Callable] = []

    def __init__(self, flex):
        """Initialize box."""
        super(DataColumnsBox, self).__init__(style=Pack(direction=COLUMN, flex=flex))

        self.x_selection = self.__add_column_option(
            label="X column:", on_select=self.set_columns
        )
        self.xerr_selection = self.__add_column_option(
            label="X error column:", on_select=self.set_columns
        )
        self.y_selection = self.__add_column_option(
            label="Y column:", on_select=self.set_columns
        )
        self.yerr_selection = self.__add_column_option(
            label="Y error column:", on_select=self.set_columns
        )

    @property
    def fit_data(self):
        """Fit data getter."""
        return self.__fit_data

    @fit_data.setter
    def fit_data(self, fit_data: FitData):
        """
        Fit data setter.

        If fit data is None, reset all selections
        """
        self.__fit_data = fit_data
        if fit_data is None:
            self.clear_selections()
            return
        items = list(fit_data.data.keys())
        used_columns = self.fit_data.used_columns
        self.set_items(self.x_selection, items, used_columns.x)
        self.set_items(self.xerr_selection, items, used_columns.xerr)
        self.set_items(self.y_selection, items, used_columns.y)
        self.set_items(self.yerr_selection, items, used_columns.yerr)
        self.selection_enabled = True
        self.set_columns(None)

    @staticmethod
    def set_items(selection, items, value):
        """
        Set items and value in selection widget.

        :param selection: Selection widget
        :param items: list of options for the widget
        :param value: selected value
        """
        selection.items = items
        if value is not None:
            selection.value = value

    def clear_selections(self):
        """Clear all selections."""
        self.selection_enabled = False
        self.set_items(self.x_selection, [], None)
        self.set_items(self.xerr_selection, [], None)
        self.set_items(self.y_selection, [], None)
        self.set_items(self.yerr_selection, [], None)
        self.run_handlers()

    @property
    def x_column(self):
        """X column name value."""
        return value_or_none(self.x_selection.value)

    @property
    def xerr_column(self):
        """X error column name value."""
        return value_or_none(self.xerr_selection.value)

    @property
    def y_column(self):
        """Y column name value."""
        return value_or_none(self.y_selection.value)

    @property
    def yerr_column(self):
        """Y error column name value."""
        return value_or_none(self.yerr_selection.value)

    @property
    def selection_enabled(self):
        """Boolean. is selection enabled for columns."""
        return self.__selection_enabled

    @selection_enabled.setter
    def selection_enabled(self, selection_enabled):
        """Set selection enabled for all column selection widgets."""
        self.__selection_enabled = selection_enabled
        self.x_selection.enabled = selection_enabled
        self.xerr_selection.enabled = selection_enabled
        self.y_selection.enabled = selection_enabled
        self.yerr_selection.enabled = selection_enabled

    def add_handler(self, handler):
        """Add handler for fit data update."""
        self.__handlers.append(handler)

    def set_columns(self, widget):  # pylint: disable=unused-argument
        """Set columns of the fit data based on the selection of the user."""
        if not self.selection_enabled:
            return
        self.fit_data.x_column = self.x_selection.value
        self.fit_data.xerr_column = self.xerr_selection.value
        self.fit_data.y_column = self.y_selection.value
        self.fit_data.yerr_column = self.yerr_selection.value
        self.run_handlers()

    def run_handlers(self):
        """Whenever fit data is updated, run handlers to notify other components."""
        for handler in self.__handlers:
            handler(self.fit_data)

    def read_csv(self, filepath):
        """
        Read data from csv file.

        :param filepath: path of the csv file
        """
        self.fit_data = FitData.read_from_csv(filepath)

    def read_excel(self, filepath, sheet):
        """
        Read data from excel file.

        :param filepath: path of the excel file
        :param sheet: sheet from which to read the data.
        """
        self.fit_data = FitData.read_from_excel(filepath, sheet)

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
