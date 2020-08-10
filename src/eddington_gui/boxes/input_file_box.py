"""Box for choosing from which file to load the input data."""
from collections import Callable
from pathlib import Path
from typing import List, Optional

import xlrd

import toga
from toga.style import Pack
from toga.style.pack import COLUMN

from eddington_gui.boxes.line_box import LineBox
from eddington_gui.consts import NO_VALUE, BIG_PADDING


class InputFileBox(toga.Box):
    """Visual box instance for choosing input file."""

    __input_file_path: toga.TextInput
    __select_file: toga.Button = None
    __select_sheet: toga.Selection = None
    __handlers: List[Callable] = []

    on_csv_read: Optional[Callable] = None
    on_excel_read: Optional[Callable] = None

    def __init__(self, flex):
        """Initialize box."""
        super(InputFileBox, self).__init__(style=Pack(direction=COLUMN, flex=flex))
        self.__input_file_path = toga.TextInput(
            readonly=True,
            style=Pack(flex=1, padding_left=BIG_PADDING, padding_right=BIG_PADDING),
        )
        self.__select_file = toga.Button(label="Choose file", on_press=self.select_file)
        self.add(
            LineBox(
                children=[
                    toga.Label(text="Input file:"),
                    self.__input_file_path,
                    self.__select_file,
                ]
            )
        )

        self.__select_sheet = toga.Selection(enabled=False, on_select=self.select_sheet)
        self.add(LineBox(children=[toga.Label(text="Sheet:"), self.__select_sheet]))

    @property
    def file_path(self):
        """Getter for the chosen file path."""
        return self.__input_file_path.value

    @file_path.setter
    def file_path(self, file_path):
        """
        Setter for the chosen file path.

        Once a path has been chosen, run handlers to notify other components of the
        change.
        """
        self.__input_file_path.value = str(file_path)
        self.data_dict = None
        for handler in self.__handlers:
            handler()

    @property
    def sheets_options(self):
        """Sheets options getter. Relevant for excel files."""
        return self.__select_sheet.items

    @sheets_options.setter
    def sheets_options(self, options):
        """Sheets options setter. Relevant for excel files."""
        if options is None:
            self.__select_sheet.items = []
            self.__select_sheet.enabled = False
        else:
            self.__select_sheet.items = options
            self.__select_sheet.enabled = True

    def add_handler(self, handler):
        """
        Add handler to run whenever the input file is changed.

        :param handler: Callable
        """
        self.__handlers.append(handler)

    def select_file(self, widget):  # pylint: disable=unused-argument
        """Open file selection dialog."""
        try:
            input_file_path = Path(
                self.window.open_file_dialog(
                    title="Choose input file", multiselect=False
                )
            )
        except ValueError:
            return
        self.file_path = input_file_path
        suffix = input_file_path.suffix
        if suffix in [".xlsx", ".xls"]:
            excel_file = xlrd.open_workbook(input_file_path, on_demand=True)
            self.sheets_options = [NO_VALUE] + excel_file.sheet_names()
            return
        self.sheets_options = None
        if suffix == ".csv":
            if self.on_csv_read is not None:
                self.on_csv_read(input_file_path)  # pylint: disable=not-callable
            return
        self.window.error_dialog(
            title="Invalid Input Source",
            message=f"Cannot process file with suffix {suffix}",
        )

    def select_sheet(self, widget):  # pylint: disable=unused-argument
        """Select sheet to read data from. Relevant for excel files."""
        value = widget.value
        if value == NO_VALUE:
            self.data_dict = None
            return
        file_path_value = Path(self.file_path)
        if self.on_excel_read is not None:
            self.on_excel_read(file_path_value, value)  # pylint: disable=not-callable
