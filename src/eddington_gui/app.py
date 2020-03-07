"""
A gui library wrapping Eddington
"""
from pathlib import Path
import xlrd

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER, FANTASY


NO_VALUE = "----------"


class EddingtonGUI(toga.App):

    input_file_path: toga.TextInput
    sheet_selection: toga.Selection

    def startup(self):
        """
        Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        main_box = toga.Box(style=Pack(direction=COLUMN))
        title_label = toga.Label(text=type(self).__name__,
                                 style=Pack(text_align=CENTER, font_family=FANTASY, font_size=23))
        main_box.add(title_label)

        file_box = toga.Box(style=Pack(direction=ROW))
        file_box.add(toga.Label(text="Input file:"))
        self.input_file_path = toga.TextInput(readonly=True, style=Pack(flex=1, padding_left=3, padding_right=3))
        file_box.add(self.input_file_path)
        file_box.add(toga.Button(label="Choose file", on_press=self.select_file))
        main_box.add(file_box)

        sheet_box = toga.Box(style=Pack(direction=ROW))
        sheet_box.add(toga.Label(text="Sheet:"))
        self.sheet_selection = toga.Selection(enabled=False)
        sheet_box.add(self.sheet_selection)
        main_box.add(sheet_box)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()

    def select_file(self, widget):
        input_file_path = self.main_window.open_file_dialog(title="Choose input file",
                                                            multiselect=False)
        self.input_file_path.value = input_file_path
        if Path(input_file_path).suffix in ['.xlsx', '.xls']:
            excel_file = xlrd.open_workbook(input_file_path, on_demand=True)
            self.sheet_selection.items = [NO_VALUE] + excel_file.sheet_names()
            self.sheet_selection.enabled = True
        else:
            self.sheet_selection.items = []
            self.sheet_selection.enabled = False


def main():
    return EddingtonGUI()
