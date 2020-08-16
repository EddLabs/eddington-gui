"""Main app."""
from pathlib import Path

from eddington_matplotlib import (
    plot_fitting,
    plot_residuals,
    plot_data,
    OutputConfiguration,
    plot_all,
)
from eddington import FitResult, EddingtonException, fit_to_data, FitData

import numpy as np
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from eddington_gui.boxes.data_columns_box import DataColumnsBox
from eddington_gui.boxes.fitting_function_box import FittingFunctionBox
from eddington_gui.boxes.header_box import HeaderBox
from eddington_gui.boxes.initial_guess_box import InitialGuessBox
from eddington_gui.boxes.input_file_box import InputFileBox
from eddington_gui.boxes.line_box import LineBox
from eddington_gui.boxes.plot_configuration_box import PlotConfigurationBox
from eddington_gui.consts import (
    WINDOW_SIZE,
    BIG_PADDING,
    MAIN_BOTTOM_PADDING,
    SMALL_PADDING,
)
from eddington_gui.window.figure_window import FigureWindow
from eddington_gui.window.records_choice_window import RecordsChoiceWindow


class EddingtonGUI(toga.App):  # pylint: disable=too-many-instance-attributes
    """Main app instance."""

    input_file_box: InputFileBox
    fitting_function_box: FittingFunctionBox
    initial_guess_box: InitialGuessBox
    plot_configuration_box: PlotConfigurationBox
    data_columns_box: DataColumnsBox
    output_directory_input: toga.TextInput
    main_window: toga.Window

    __a0: np.ndarray = None
    __fit_result: FitResult = None

    def startup(self):
        """
        Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        main_box = toga.Box(style=Pack(direction=COLUMN))
        main_box.add(HeaderBox())

        self.input_file_box = InputFileBox(flex=1)
        self.input_file_box.add_handler(self.reset_fit_data)
        main_box.add(self.input_file_box)

        self.fitting_function_box = FittingFunctionBox(flex=1)
        self.fitting_function_box.add_handler(lambda fit_func: self.reset_fit_result())
        main_box.add(self.fitting_function_box)

        self.initial_guess_box = InitialGuessBox()
        self.initial_guess_box.add_handler(lambda a0: self.reset_fit_result())
        self.fitting_function_box.add_handler(self.set_parameters_number)
        main_box.add(self.initial_guess_box)

        self.data_columns_box = DataColumnsBox(flex=5)
        self.data_columns_box.add_handler(lambda fit_data: self.reset_fit_result())
        self.input_file_box.on_csv_read = self.data_columns_box.read_csv
        self.input_file_box.on_excel_read = self.data_columns_box.read_excel
        self.input_file_box.on_select_file = self.choose_sheet

        self.plot_configuration_box = PlotConfigurationBox(flex=5)
        self.fitting_function_box.add_handler(
            self.plot_configuration_box.on_fit_function_load
        )
        self.data_columns_box.add_handler(self.plot_configuration_box.on_fit_data_load)

        main_box.add(
            toga.Box(
                style=Pack(direction=ROW, padding_top=BIG_PADDING, flex=1),
                children=[
                    self.data_columns_box,
                    toga.Box(style=Pack(flex=2)),
                    self.plot_configuration_box,
                ],
            )
        )
        main_box.add(
            LineBox(
                children=[
                    toga.Button(label="Choose Records", on_press=self.choose_records)
                ]
            )
        )
        main_box.add(toga.Box(style=Pack(flex=1)))
        main_box.add(
            LineBox(
                children=[
                    toga.Button(label="Fit", on_press=self.fit, style=Pack(flex=1))
                ],
            )
        )
        main_box.add(
            LineBox(
                children=[
                    toga.Button(
                        label="Plot data", on_press=self.plot_data, style=Pack(flex=1)
                    ),
                    toga.Button(
                        label="Plot Initial Guess",
                        on_press=self.plot_initial_guess,
                        style=Pack(flex=1),
                    ),
                ]
            )
        )
        main_box.add(
            LineBox(
                children=[
                    toga.Button(
                        label="Plot Fitting", on_press=self.plot, style=Pack(flex=1)
                    ),
                    toga.Button(
                        label="Residuals", on_press=self.residuals, style=Pack(flex=1)
                    ),
                ],
            )
        )
        self.output_directory_input = toga.TextInput(style=Pack(flex=1))
        main_box.add(
            LineBox(
                padding_bottom=MAIN_BOTTOM_PADDING,
                children=[
                    toga.Label(text="Output directory:"),
                    self.output_directory_input,
                    toga.Button(
                        label="Choose directory",
                        on_press=self.choose_output_dir,
                        style=Pack(padding_left=SMALL_PADDING),
                    ),
                    toga.Button(
                        label="Save",
                        on_press=self.save_to_output_dir,
                        style=Pack(
                            padding_left=SMALL_PADDING, padding_right=SMALL_PADDING
                        ),
                    ),
                ],
            )
        )

        self.main_window = toga.MainWindow(title=self.formal_name, size=WINDOW_SIZE)
        self.main_window.content = main_box
        self.main_window.show()

    @property
    def fit_result(self):
        """Getter of the fit result."""
        if self.__fit_result is None:
            self.__calculate_fit_result()
        return self.__fit_result

    @fit_result.setter
    def fit_result(self, fit_result):
        """Setter of the fit result."""
        self.__fit_result = fit_result

    def choose_records(self, widget):  # pylint: disable=unused-argument
        """Open the choose records window."""
        if self.data_columns_box.fit_data is None:
            self.main_window.info_dialog(
                title="Choose Records", message="No data been given yet"
            )
            return
        window = RecordsChoiceWindow(fit_data=self.data_columns_box.fit_data)
        window.show()
        self.reset_fit_result()
        self.initial_guess_box.reset_initial_guess()
        self.plot_configuration_box.reset_plot_configuration()

    def fit(self, widget):  # pylint: disable=unused-argument
        """Handler for the "fit" button."""
        try:
            if self.fit_result is None:
                self.main_window.info_dialog(
                    title="Fit Result", message="Nothing to fit yet"
                )
                return
        except EddingtonException:
            return
        self.main_window.info_dialog(title="Fit Result", message=str(self.fit_result))

    def plot_data(self, widget):  # pylint: disable=unused-argument
        """Handler for the "plot data" button."""
        if self.data_columns_box.fit_data is None:
            self.show_nothing_to_plot()
        else:
            self.show_figure_window(
                plot_data(
                    data=self.data_columns_box.fit_data,
                    plot_configuration=self.plot_configuration_box.plot_configuration,
                )
            )

    def plot_initial_guess(self, widget):  # pylint: disable=unused-argument
        """Handler for the "plot initial guess" button."""
        try:
            if (
                self.data_columns_box.fit_data is None
                or self.initial_guess_box.a0 is None  # noqa: W503
            ):
                self.show_nothing_to_plot()
                return
        except EddingtonException as error:
            self.main_window.error_dialog(
                title="Plot initial guess error", message=str(error),
            )
            return
        self.show_figure_window(
            plot_fitting(
                func=self.fitting_function_box.fit_function,
                data=self.data_columns_box.fit_data,
                plot_configuration=self.plot_configuration_box.plot_configuration,
                a=self.initial_guess_box.a0,
            )
        )

    def plot(self, widget):  # pylint: disable=unused-argument
        """Handler for the "plot fitting" button."""
        try:
            if self.fit_result is None:
                self.show_nothing_to_plot()
                return
        except EddingtonException:
            return
        self.show_figure_window(
            plot_fitting(
                func=self.fitting_function_box.fit_function,
                data=self.data_columns_box.fit_data,
                plot_configuration=self.plot_configuration_box.plot_configuration,
                a=self.fit_result.a,
            )
        )

    def residuals(self, widget):  # pylint: disable=unused-argument
        """Handler for the "residuals" button."""
        try:
            if self.fit_result is None:
                self.show_nothing_to_plot()
                return
        except EddingtonException:
            return
        self.show_figure_window(
            plot_residuals(
                func=self.fitting_function_box.fit_function,
                data=self.data_columns_box.fit_data,
                plot_configuration=self.plot_configuration_box.plot_configuration,
                a=self.fit_result.a,
            )
        )

    def choose_output_dir(self, widget):  # pylint: disable=unused-argument
        """Open output directory choice dialog."""
        try:
            folder_path = self.main_window.select_folder_dialog(
                title="Output directory"
            )
        except ValueError:
            return
        self.output_directory_input.value = folder_path[0]

    def save_to_output_dir(self, widget):  # pylint: disable=unused-argument
        """Handler for the "save to output directory" button."""
        try:
            if self.fit_result is None:
                self.show_nothing_to_plot()
                return
        except EddingtonException:
            return
        output_dir = Path(self.output_directory_input.value)
        if not output_dir.exists():
            output_dir.mkdir()
        func_name = self.fitting_function_box.fit_function.name
        output_configuration = OutputConfiguration.build(
            base_name=func_name, output_dir=output_dir,
        )
        plot_all(
            func=self.fitting_function_box.fit_function,
            data=self.data_columns_box.fit_data,
            plot_configuration=self.plot_configuration_box.plot_configuration,
            output_configuration=output_configuration,
            result=self.fit_result,
        )
        self.main_window.info_dialog(
            title="Save output", message="All plots have been saved successfully!"
        )

    def show_nothing_to_plot(self):
        """Show dialog indicating that there is nothing to plot yet."""
        self.main_window.info_dialog(title="Fit Result", message="Nothing to plot yet")

    @staticmethod
    def show_figure_window(fig):
        """Open a window with matplotlib window."""
        figure_window = FigureWindow(fig)
        figure_window.show()

    def reset_fit_data(self):
        """Set fit data to None."""
        self.data_columns_box.fit_data = None

    def reset_fit_result(self):
        """Set fit result to None."""
        self.fit_result = None

    def set_parameters_number(self, func):
        """Set number of parameters."""
        if func is None:
            self.initial_guess_box.n = None
        else:
            self.initial_guess_box.n = func.n

    def __calculate_fit_result(self):
        if (
            self.data_columns_box.fit_data is None
            or self.fitting_function_box.fit_function is None  # noqa: W503
        ):
            self.fit_result = None
            return
        try:
            self.fit_result = fit_to_data(
                data=self.data_columns_box.fit_data,
                func=self.fitting_function_box.fit_function,
                a0=self.initial_guess_box.a0,
            )
        except EddingtonException as error:
            self.fit_result = None
            self.main_window.error_dialog(
                title="Fit result error", message=str(error),
            )
            raise error
   
    def choose_sheet(self):
        """Automatically choose the first valid sheet"""
        for sheet in self.input_file_box.sheets_options:
            try:
                self.data_columns_box.fit_data = FitData.read_from_excel(
                    Path(self.input_file_box.file_path),
                    sheet)
                self.input_file_box.selected_sheet.value = sheet
                return
            except Exception as error:
                pass
        if self.data_columns_box.fit_data == None:
            self.main_window.error_dialog(
                title="Input data error",
                message="No sheet available with valid data.\nPlease fix the file or load another one.")
            self.fit_data = None



def main():
    """Main function."""
    return EddingtonGUI()
