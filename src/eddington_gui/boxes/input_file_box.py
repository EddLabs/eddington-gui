from collections import OrderedDict
from pathlib import Path
import xlrd
from typing import Union

import toga
from eddington import read_data_from_excel, read_data_from_csv
from eddington.exceptions import InvalidDataFile
from toga.style import Pack
from toga.style.pack import COLUMN

from eddington_gui.boxes.line_box import LineBox
from eddington_gui.consts import NO_VALUE, BIG_PADDING


class InputFileBox(toga.Box):

    __input_file_path: toga.TextInput
    __select_file: toga.Button = None
    __select_sheet: toga.Selection = None

    __data_dict: Union[OrderedDict, None] = None
    __handlers = []

    def __init__(self):
        super(InputFileBox, self).__init__(style=Pack(direction=COLUMN))
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
        return self.__input_file_path.value

    @file_path.setter
    def file_path(self, file_path):
        self.__input_file_path.value = str(file_path)

    @property
    def sheets_options(self):
        return self.__select_sheet.items

    @sheets_options.setter
    def sheets_options(self, options):
        if options is None:
            self.__select_sheet.items = []
            self.__select_sheet.enabled = False
        else:
            self.__select_sheet.items = options
            self.__select_sheet.enabled = True

    @property
    def data_dict(self):
        return self.__data_dict

    @data_dict.setter
    def data_dict(self, data_dict):
        self.__data_dict = data_dict
        for handler in self.__handlers:
            handler(data_dict)

    def add_handler(self, handler):
        self.__handlers.append(handler)

    def select_file(self, widget):
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
            self.data_dict = None
            self.sheets_options = [NO_VALUE] + excel_file.sheet_names()
            return
        self.sheets_options = None
        if suffix == ".csv":
            self.data_dict = read_data_from_csv(filepath=input_file_path)
            return
        self.data_dict = None
        self.window.error_dialog(
            title="Invalid Input Source",
            message=f"Cannot process file with suffix {suffix}",
        )

    def select_sheet(self, widget):
        value = widget.value
        if value == NO_VALUE:
            self.data_dict = None
            return
        file_path_value = Path(self.file_path)
        try:
            self.data_dict = read_data_from_excel(filepath=file_path_value, sheet=value)
        except InvalidDataFile as e:
            self.window.error_dialog(
                title="Invalid Input Source", message=str(e),
            )
            self.data_dict = None
