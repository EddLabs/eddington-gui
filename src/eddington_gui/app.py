"""
A gui library wrapping Eddington
"""
from pathlib import Path
import xlrd
from eddington import read_data_from_excel, InvalidDataFile, plot_fitting, plot_residuals

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER, FANTASY, BOTTOM

from eddington_gui.boxes.data_box import DataBox
from eddington_gui.boxes.input_file_box import InputFileBox
from eddington_gui.consts import NO_VALUE


class EddingtonGUI(toga.App):

    file_box: InputFileBox
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

        self.file_box = InputFileBox()
        self.file_box.select_file = self.select_file
        self.file_box.select_sheet = self.select_sheet
        main_box.add(self.file_box)

        self.data_box = DataBox()
        main_box.add(self.data_box)

        spaced_box = toga.Box(style=Pack(flex=1))
        main_box.add(spaced_box)

        buttons_box = toga.Box(style=Pack(direction=ROW, padding_bottom=15, alignment=BOTTOM))
        buttons_box.add(toga.Button(label="Fit", on_press=self.fit, style=Pack(flex=1)))
        buttons_box.add(toga.Button(label="Plot", on_press=self.plot, style=Pack(flex=1)))
        buttons_box.add(toga.Button(label="Residuals", on_press=self.residuals, style=Pack(flex=1)))
        main_box.add(buttons_box)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()

    def select_file(self, widget):
        input_file_path = self.main_window.open_file_dialog(title="Choose input file",
                                                            multiselect=False)
        self.file_box.file_path = input_file_path
        if Path(input_file_path).suffix in ['.xlsx', '.xls']:
            excel_file = xlrd.open_workbook(input_file_path, on_demand=True)
            self.file_box.sheets_options = [NO_VALUE] + excel_file.sheet_names()
        else:
            self.file_box.sheets_options = None
        self.data_box.data_dict = None

    def select_sheet(self, widget):
        value = widget.value
        if value == NO_VALUE:
            self.data_box.data_dict = None
            return
        file_path_value = Path(self.file_box.file_path)
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

    def residuals(self, widget):
        if self.data_box.fit_result is None:
            self.main_window.info_dialog(title="Fit Result", message="Nothing to plot yet")
        else:
            plot_residuals(func=self.data_box.fit_function, data=self.data_box.fit_data,
                           plot_configuration=self.data_box.plot_configuration,
                           res=self.data_box.fit_result)


def main():
    return EddingtonGUI()
