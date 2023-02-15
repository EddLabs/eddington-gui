"""Box for choosing which columns to use in data dictionary."""
from pathlib import Path
from typing import Callable, List, Optional, Union

import toga
from eddington import FittingData
from toga.style import Pack
from toga.style.pack import LEFT

from eddington_gui.boxes.line_box import LineBox
from eddington_gui.util import value_or_none


class DataColumnsBox(LineBox):  # pylint: disable=too-many-instance-attributes
    """Visual box instance for choosing columns."""

    __items: List[str] = []
    __selection_enabled: bool = False

    x_selection: toga.Selection
    xerr_selection: toga.Selection
    y_selection: toga.Selection
    yerr_selection: toga.Selection

    __fitting_data: Optional[FittingData]
    __on_columns_change: Optional[Callable[[FittingData], None]]

    def __init__(self, on_columns_change):
        """Initialize box."""
        super().__init__()
        self.__fitting_data = None
        self.on_columns_change = None

        self.x_selection = self.__add_column_option(
            text="X column:", on_select=lambda widget: self.set_columns()
        )
        self.xerr_selection = self.__add_column_option(
            text="X error column:", on_select=lambda widget: self.set_columns()
        )
        self.y_selection = self.__add_column_option(
            text="Y column:", on_select=lambda widget: self.set_columns()
        )
        self.yerr_selection = self.__add_column_option(
            text="Y error column:", on_select=lambda widget: self.set_columns()
        )
        self.on_columns_change = on_columns_change

    @property
    def fitting_data(self):
        """Fit data getter."""
        return self.__fitting_data

    @fitting_data.setter
    def fitting_data(self, fitting_data: FittingData):
        """
        Fit data setter.

        If fit data is None, reset all selections
        """
        self.__fitting_data = fitting_data
        if fitting_data is None:
            self.clear_selections()
            return
        items = list(fitting_data.data.keys())
        used_columns = self.fitting_data.used_columns
        self.set_items(self.x_selection, items, used_columns.x)
        self.set_items(self.xerr_selection, items, used_columns.xerr)
        self.set_items(self.y_selection, items, used_columns.y)
        self.set_items(self.yerr_selection, items, used_columns.yerr)
        self.selection_enabled = True
        self.set_columns()

    @property
    def on_columns_change(self) -> Optional[Callable]:
        """on_columns_change getter."""
        return self.__on_columns_change

    @on_columns_change.setter
    def on_columns_change(self, on_columns_change):
        """on_columns_change setter."""
        self.__on_columns_change = on_columns_change

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

    @staticmethod
    def set_items(selection: toga.Selection, items: List[str], value: Optional[str]):
        """
        Set items and value in selection widget.

        :param selection: Selection widget
        :type selection: toga.Selection
        :param items: list of options for the widget
        :type items: List[str]
        :param value: selected value
        :type value: Optional[str]
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
        self.run_on_columns_change()

    def set_columns(self):
        """Set columns of the fit data based on the selection of the user."""
        if not self.selection_enabled:
            return
        self.fitting_data.x_column = self.x_selection.value
        self.fitting_data.xerr_column = self.xerr_selection.value
        self.fitting_data.y_column = self.y_selection.value
        self.fitting_data.yerr_column = self.yerr_selection.value
        self.run_on_columns_change()

    def run_on_columns_change(self):
        """If on_columns_change is not None, runs it."""
        if self.on_columns_change is not None:
            self.on_columns_change(self.fitting_data)

    def read_csv(self, filepath: Union[str, Path]):
        """
        Read data from csv file.

        :param filepath: path of the csv file
        :type filepath: Union[str, Path]
        """
        self.fitting_data = FittingData.read_from_csv(filepath)

    def read_excel(self, filepath: Union[str, Path], sheet: str):
        """
        Read data from excel file.

        :param filepath: path of the excel file
        :type filepath: Union[str, Path]
        :param sheet: sheet from which to read the data.
        :type sheet: str
        """
        self.fitting_data = FittingData.read_from_excel(filepath, sheet)

    def __add_column_option(self, text, on_select):
        self.add(toga.Label(text=text))
        selection = toga.Selection(
            enabled=self.selection_enabled,
            on_select=on_select,
            style=Pack(alignment=LEFT, flex=1),
        )
        self.add(selection)
        return selection
