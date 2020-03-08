"""
A gui library wrapping Eddington
"""
from pathlib import Path
import xlrd
from eddington import read_data_from_excel, InvalidDataFile, plot_fitting

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER, FANTASY, BOTTOM

from eddington_gui.data_box import DataBox
from eddington_gui.consts import NO_VALUE


class EddingtonGUI(toga.App):

    input_file_path: toga.TextInput
    sheet_selection: toga.Selection
    data_box: DataBox

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
        self.sheet_selection = toga.Selection(enabled=False, on_select=self.select_sheet)
        sheet_box.add(self.sheet_selection)
        main_box.add(sheet_box)

        self.data_box = DataBox()
        main_box.add(self.data_box)

        spaced_box = toga.Box(style=Pack(flex=1))
        main_box.add(spaced_box)

        buttons_box = toga.Box(style=Pack(direction=ROW, padding_bottom=15, alignment=BOTTOM))
        buttons_box.add(toga.Button(label="Fit", on_press=self.fit, style=Pack(flex=1)))
        buttons_box.add(toga.Button(label="Plot", on_press=self.plot, style=Pack(flex=1)))
        main_box.add(buttons_box)

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
        self.data_box.data_dict = None

    def select_sheet(self, widget):
        value = widget.value
        if value == NO_VALUE:
            self.data_box.data_dict = None
            return
        file_path_value = Path(self.input_file_path.value)
        try:
            self.data_box.data_dict = read_data_from_excel(filepath=file_path_value, sheet=value)
        except InvalidDataFile:
            self.main_window.error_dialog(title="Invalid Input Source",
                                          message=f"\"{value}\" sheet in \"{file_path_value.name}\" has invalid syntax")
            self.data_box.data_dict = None

    def fit(self, widget):
        if self.data_box.fit_result is None:
            self.main_window.info_dialog(title="Fit Result", message="Nothing to fit yet")
        else:
            self.main_window.info_dialog(title="Fit Result", message=str(self.data_box.fit_result))

    def plot(self, widget):
        if self.data_box.fit_result is None:
            self.main_window.info_dialog(title="Fit Result", message="Nothing to plot yet")
        else:
            plot_fitting(func=self.data_box.fit_function, data=self.data_box.fit_data,
                         plot_configuration=self.data_box.plot_configuration,
                         a=self.data_box.fit_result.a)


def main():
    return EddingtonGUI()
