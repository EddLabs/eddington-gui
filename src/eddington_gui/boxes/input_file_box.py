from collections import OrderedDict
from pathlib import Path
import xlrd
from typing import Union

import toga
from eddington import read_data_from_excel, InvalidDataFile
from toga.style import Pack
from toga.style.pack import ROW, COLUMN

from eddington_gui.consts import NO_VALUE


class InputFileBox(toga.Box):

    __input_file_path: toga.TextInput
    __select_file: toga.Button = None
    __select_sheet: toga.Selection = None

    __data_dict: Union[OrderedDict, None] = None
    __main_window = None
    __handlers = []

    def __init__(self):
        super(InputFileBox, self).__init__(style=Pack(direction=COLUMN))
        file_path_box = toga.Box(style=Pack(direction=ROW))
        file_path_box.add(toga.Label(text="Input file:"))
        self.__input_file_path = toga.TextInput(readonly=True, style=Pack(flex=1, padding_left=3, padding_right=3))
        file_path_box.add(self.__input_file_path)
        self.__select_file = toga.Button(label="Choose file", on_press=self.select_file)
        file_path_box.add(self.__select_file)
        self.add(file_path_box)

        sheet_box = toga.Box(style=Pack(direction=ROW))
        sheet_box.add(toga.Label(text="Sheet:"))
        self.__select_sheet = toga.Selection(enabled=False, on_select=self.select_sheet)
        sheet_box.add(self.__select_sheet)
        self.add(sheet_box)

    @property
    def file_path(self):
        return self.__input_file_path.value

    @file_path.setter
    def file_path(self, file_path):
        self.__input_file_path.value = file_path

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

    def set_main_window(self, main_window):
        self.__main_window = main_window

    def add_handler(self, handler):
        self.__handlers.append(handler)

    def select_file(self, widget):
        input_file_path = self.__main_window.open_file_dialog(title="Choose input file",
                                                              multiselect=False)
        self.file_path = input_file_path
        if Path(input_file_path).suffix in ['.xlsx', '.xls']:
            excel_file = xlrd.open_workbook(input_file_path, on_demand=True)
            self.sheets_options = [NO_VALUE] + excel_file.sheet_names()
        else:
            self.sheets_options = None
        self.data_dict = None

    def select_sheet(self, widget):
        value = widget.value
        if value == NO_VALUE:
            self.data_dict = None
            return
        file_path_value = Path(self.file_path)
        try:
            self.data_dict = read_data_from_excel(filepath=file_path_value, sheet=value)
        except InvalidDataFile:
            self.__main_window.error_dialog(
                title="Invalid Input Source",
                message=f"\"{value}\" sheet in \"{file_path_value.name}\" has invalid syntax"
            )
            self.data_dict = None
