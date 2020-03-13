"""
A gui library wrapping Eddington
"""
from eddington import (
    plot_fitting,
    plot_residuals,
    fit_to_data,
    FitData,
    FitResult,
    reduce_data,
)

import toga
from eddington.input.util import get_a0
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER, FANTASY, BOTTOM

from eddington_gui.boxes.data_columns_box import DataColumnsBox
from eddington_gui.boxes.fitting_function_box import FittingFunctionBox
from eddington_gui.boxes.input_file_box import InputFileBox
from eddington_gui.boxes.plot_configuration_box import PlotConfigurationBox
from eddington_gui.consts import SIZE


class EddingtonGUI(toga.App):

    input_file_box: InputFileBox
    fitting_function_box: FittingFunctionBox
    plot_configuration_box: PlotConfigurationBox
    data_columns_box: DataColumnsBox

    __fit_data: FitData = None
    __fit_result: FitResult = None

    def startup(self):
        """
        Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        main_box = toga.Box(style=Pack(direction=COLUMN))
        title_label = toga.Label(
            text=type(self).__name__,
            style=Pack(text_align=CENTER, font_family=FANTASY, font_size=23),
        )
        main_box.add(title_label)

        self.input_file_box = InputFileBox()
        main_box.add(self.input_file_box)

        self.fitting_function_box = FittingFunctionBox()
        self.fitting_function_box.add_handler(lambda fit_func: self.reset_all())
        main_box.add(self.fitting_function_box)

        self.data_columns_box = DataColumnsBox()
        self.data_columns_box.add_handler(lambda columns: self.reset_all())
        self.input_file_box.add_handler(self.data_columns_box.update_data_dict)

        self.plot_configuration_box = PlotConfigurationBox()
        self.fitting_function_box.add_handler(
            self.plot_configuration_box.load_fit_function
        )
        self.data_columns_box.add_handler(self.plot_configuration_box.load_columns)

        main_box.add(
            toga.Box(
                style=Pack(direction=ROW, padding_top=5),
                children=[self.data_columns_box, self.plot_configuration_box],
            )
        )

        spaced_box = toga.Box(style=Pack(flex=1))
        main_box.add(spaced_box)

        buttons_box = toga.Box(
            style=Pack(direction=ROW, padding_bottom=15, alignment=BOTTOM)
        )
        buttons_box.add(toga.Button(label="Fit", on_press=self.fit, style=Pack(flex=1)))
        buttons_box.add(
            toga.Button(label="Plot", on_press=self.plot, style=Pack(flex=1))
        )
        buttons_box.add(
            toga.Button(label="Residuals", on_press=self.residuals, style=Pack(flex=1))
        )
        main_box.add(buttons_box)

        self.main_window = toga.MainWindow(title=self.formal_name, size=SIZE)
        self.input_file_box.set_main_window(self.main_window)
        self.main_window.content = main_box
        self.main_window.show()

    @property
    def fit_data(self):
        if self.__fit_data is None:
            self.__calculate_fit_data()
        return self.__fit_data

    @fit_data.setter
    def fit_data(self, fit_data):
        self.__fit_data = fit_data

    @property
    def fit_result(self):
        if self.__fit_result is None:
            self.__calculate_fit_result()
        return self.__fit_result

    @fit_result.setter
    def fit_result(self, fit_result):
        self.__fit_result = fit_result

    def fit(self, widget):
        if self.fit_result is None:
            self.main_window.info_dialog(
                title="Fit Result", message="Nothing to fit yet"
            )
        else:
            self.main_window.info_dialog(
                title="Fit Result", message=str(self.fit_result)
            )

    def plot(self, widget):
        if self.fit_result is None:
            self.main_window.info_dialog(
                title="Fit Result", message="Nothing to plot yet"
            )
        else:
            plot_fitting(
                func=self.fitting_function_box.fit_function,
                data=self.fit_data,
                plot_configuration=self.plot_configuration_box.plot_configuration,
                a=self.fit_result.a,
            )

    def residuals(self, widget):
        if self.fit_result is None:
            self.main_window.info_dialog(
                title="Fit Result", message="Nothing to plot yet"
            )
        else:
            plot_residuals(
                func=self.fitting_function_box.fit_function,
                data=self.fit_data,
                plot_configuration=self.plot_configuration_box.plot_configuration,
                res=self.fit_result,
            )

    def reset_fit_data(self):
        self.fit_data = None

    def reset_fit_result(self):
        self.fit_result = None

    def reset_all(self):
        self.reset_fit_data()
        self.reset_fit_result()
        self.plot_configuration_box.reset_plot_configuration()

    def __calculate_fit_data(self):
        if (
            self.input_file_box.data_dict is None
            or self.fitting_function_box.fit_function is None
        ):
            self.fit_data = None
            return
        reduced_data = reduce_data(
            data_dict=self.input_file_box.data_dict,
            x_column=self.data_columns_box.x_column,
            xerr_column=self.data_columns_box.xerr_column,
            y_column=self.data_columns_box.y_column,
            yerr_column=self.data_columns_box.yerr_column,
        )
        self.fit_data = FitData.build_from_data_dict(
            data_dict=reduced_data, a0=get_a0(self.fitting_function_box.fit_function.n)
        )
        self.plot_configuration_box.set_xmin_xmax(self.fit_data.x)

    def __calculate_fit_result(self):
        if self.fit_data is None or self.fitting_function_box.fit_function is None:
            self.fit_result = None
        else:
            self.fit_result = fit_to_data(
                self.fit_data, self.fitting_function_box.fit_function
            )


def main():
    return EddingtonGUI()
