import toga
from toga.style import Pack
from toga.style.pack import ROW, COLUMN


class InputFileBox(toga.Box):

    __input_file_path: toga.TextInput

    __select_file: toga.Button = None
    __select_sheet: toga.Selection = None

    def __init__(self):
        super(InputFileBox, self).__init__(style=Pack(direction=COLUMN))
        file_path_box = toga.Box(style=Pack(direction=ROW))
        file_path_box.add(toga.Label(text="Input file:"))
        self.__input_file_path = toga.TextInput(readonly=True, style=Pack(flex=1, padding_left=3, padding_right=3))
        file_path_box.add(self.__input_file_path)
        self.__select_file = toga.Button(label="Choose file")
        file_path_box.add(self.__select_file)
        self.add(file_path_box)

        sheet_box = toga.Box(style=Pack(direction=ROW))
        sheet_box.add(toga.Label(text="Sheet:"))
        self.__select_sheet = toga.Selection(enabled=False)
        sheet_box.add(self.__select_sheet)
        self.add(sheet_box)

    @property
    def select_file(self):
        return self.__select_file.on_press

    @select_file.setter
    def select_file(self, select_file):
        self.__select_file.on_press = select_file

    @property
    def select_sheet(self):
        return self.__select_sheet.on_select

    @select_sheet.setter
    def select_sheet(self, select_sheet):
        self.__select_sheet.on_select = select_sheet

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
