"""Main app."""
from pathlib import Path

import numpy as np
import toga
from eddington import (
    EddingtonException,
    FittingData,
    FittingDataError,
    FittingResult,
    fit,
)
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from eddington_gui.boxes.data_columns_box import DataColumnsBox
from eddington_gui.boxes.fitting_function_box import FittingFunctionBox
from eddington_gui.boxes.header_box import HeaderBox
from eddington_gui.boxes.initial_guess_box import InitialGuessBox
from eddington_gui.boxes.input_file_box import InputFileBox
from eddington_gui.boxes.line_box import LineBox
from eddington_gui.boxes.output_box import OutputBox
from eddington_gui.boxes.plot_configuration_box import PlotConfigurationBox

from eddington_gui.consts import BIG_PADDING, NO_VALUE, WINDOW_SIZE
from eddington_gui.window.figure_window import FigureWindow
from eddington_gui.window.records_choice_window import RecordsChoiceWindow

PLOT_GROUP = toga.Group("Plot", order=2)


class EddingtonGUI(toga.App):  # pylint: disable=too-many-instance-attributes
    """Main app instance."""

    input_file_box: InputFileBox
    fitting_function_box: FittingFunctionBox
    initial_guess_box: InitialGuessBox
    plot_configuration_box: PlotConfigurationBox
    data_columns_box: DataColumnsBox
    output_box: OutputBox

    main_window: toga.Window

    __a0: np.ndarray = None
    __fitting_result: FittingResult = None

    accessibility_mode = False

    def startup(self):
        """
        Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        main_box = toga.Box(style=Pack(direction=COLUMN))
        main_box.add(HeaderBox())

        self.input_file_box = InputFileBox(on_choose_record=self.choose_records)
        self.input_file_box.on_input_file_change = self.reset_fitting_data
        self.input_file_box.on_csv_read = self.read_csv
        self.input_file_box.on_excel_read = self.read_excel
        self.input_file_box.on_select_excel_file = self.select_default_sheet
        main_box.add(self.input_file_box)

        self.fitting_function_box = FittingFunctionBox(flex=1)
        self.fitting_function_box.on_fitting_function_load = (
            self.on_fitting_function_load
        )
        main_box.add(self.fitting_function_box)

        self.initial_guess_box = InitialGuessBox(
            on_initial_guess_change=self.reset_fitting_result
        )
        main_box.add(self.initial_guess_box)

        self.data_columns_box = DataColumnsBox(flex=5)
        self.data_columns_box.on_columns_change = self.on_data_columns_change

        self.plot_configuration_box = PlotConfigurationBox(flex=5)

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
        self.output_box = OutputBox(on_save_output=self.on_save_output)
        main_box.add(self.output_box)

        accessibility_group = toga.Group('Accessibility') 

        fontSize = toga.Command(
            self.change_font_size,
            label='Text Size',
            tooltip='Adds option to enlarge all text',
            shortcut=toga.Key.MOD_1 + 'a',  #a for accessibility
            group=accessibility_group,
        )

        self.main_window = toga.MainWindow(title=self.formal_name, size=WINDOW_SIZE)
        self.main_window.content = main_box
        self.main_window.toolbar.add(fontSize)
        self.main_window.show()

        self.commands.add(
            toga.Command(
                self.input_file_box.select_file,
                label="Upload data file",
                shortcut=toga.Key.MOD_1 + "u",
                group=toga.Group.FILE,
            ),
            toga.Command(
                self.output_box.choose_output_dir,
                label="Choose output directory",
                shortcut=toga.Key.MOD_1 + "o",
                group=toga.Group.FILE,
            ),
            toga.Command(
                self.on_save_output,
                label="Save plots and results",
                shortcut=toga.Key.MOD_1 + "s",
                group=toga.Group.FILE,
            ),
            toga.Command(
                self.choose_records,
                label="Choose records",
                shortcut=toga.Key.MOD_1 + "c",
                group=toga.Group.FILE,
            ),
            toga.Command(
                self.fitting_function_box.load_module,
                label="Load module",
                shortcut=toga.Key.MOD_1 + "m",
                group=toga.Group.FILE,
            ),
            toga.Command(
                self.plot_configuration_box.toggle_grid_switch,
                label="Add/remove grid lines",
                shortcut=toga.Key.MOD_1 + "g",
                section=1,
                group=PLOT_GROUP,
            ),
            toga.Command(
                self.plot_configuration_box.toggle_legend_switch,
                label="Add/remove legend",
                shortcut=toga.Key.MOD_1 + "l",
                section=1,
                group=PLOT_GROUP,
            ),
            toga.Command(
                self.plot_data,
                label="Plot data points",
                shortcut=toga.Key.MOD_1 + "d",
                section=2,
                group=PLOT_GROUP,
            ),
            toga.Command(
                self.fit,
                label="Fit result",
                shortcut=toga.Key.MOD_1 + "f",
                section=2,
                group=PLOT_GROUP,
            ),
            toga.Command(
                self.plot_initial_guess,
                label="Plot initial guess fitting",
                shortcut=toga.Key.MOD_1 + "i",
                section=2,
                group=PLOT_GROUP,
            ),
            toga.Command(
                self.plot,
                label="Plot fitting",
                shortcut=toga.Key.MOD_1 + "p",
                section=2,
                group=PLOT_GROUP,
            ),
            toga.Command(
                self.residuals,
                label="Plot residuals",
                shortcut=toga.Key.MOD_1 + "r",
                section=2,
                group=PLOT_GROUP,
            ),
        )
        
    # TODO: have fontSize call this function, 
    # and this function will call change_font_size
    # with the chosen size.
    # TODO: Get rid of the constant numbers
    #def font_size_slider(self, sender):
    #    self.main_window.content.add(
    #        toga.Slider(
    #            default=10,
    #            range=(10, 100),
    #            tick_count=10,
    #            on_slide=self.change_font_size
    #        )
    #    )

    def change_font_size(self, sender):
        self.accessibility_mode = True
        for c in self.main_window.content.children:
            try:
                c.change_font_size()
            except AttributeError:
                print(c)
                self.rec_change_font_size(c)

    def rec_change_font_size(self, container):
        for c in container.children:
            c.style.update(font_size=20, flex=1)
            c.refresh()
        try:
            container.style.update(font_size=20, flex=1)
            container.refresh()
        except AttributeError as e:
            print(e)

    @property
    def fitting_result(self):
        """Getter of the fit result."""
        if self.__fitting_result is None:
            self.__calculate_fitting_result()
        return self.__fitting_result

    @fitting_result.setter
    def fitting_result(self, fitting_result):
        """Setter of the fit result."""
        self.__fitting_result = fitting_result

    def on_data_columns_change(self, fitting_data):
        """Run those methods when data columns are changed."""
        self.reset_fitting_result()
        self.plot_configuration_box.on_fitting_data_load(fitting_data)

    def on_fitting_function_load(self, fitting_function):
        """Run those methods when fitting function is changed."""
        self.reset_fitting_result()
        self.set_parameters_number(fitting_function)
        self.plot_configuration_box.on_fitting_function_load(fitting_function)

    def on_save_output(self, widget):  # pylint: disable=unused-argument
        """Handler for the "save to output directory" button."""
        try:
            if self.fitting_result is None:
                self.show_nothing_to_plot()
                return
        except EddingtonException:
            return
        if self.output_box.output_directory is None:
            self.main_window.error_dialog(
                title="Results output save error",
                message="No output directory was chosen",
            )
            return
        output_dir = Path(self.output_box.output_directory)
        if not output_dir.exists():
            output_dir.mkdir()
        func_name = self.fitting_function_box.fitting_function.name
        if self.output_box.export_data_plot:
            self.plot_configuration_box.plot_data(
                data=self.data_columns_box.fitting_data
            ).savefig(output_dir / f"{func_name}_data.png")
        if self.output_box.export_fitting_plot:
            self.plot_configuration_box.plot_fitting(
                func=self.fitting_function_box.fitting_function,
                data=self.data_columns_box.fitting_data,
                a=self.fitting_result.a,
            ).savefig(output_dir / f"{func_name}_fitting.png")
        if self.output_box.export_residuals_plot:
            self.plot_configuration_box.plot_residuals(
                func=self.fitting_function_box.fitting_function,
                data=self.data_columns_box.fitting_data,
                a=self.fitting_result.a,
            ).savefig(output_dir / f"{func_name}_residuals.png")
        if self.output_box.export_result_as_text:
            self.fitting_result.save_txt(output_dir / f"{func_name}_result.txt")
        if self.output_box.export_result_as_json:
            self.fitting_result.save_json(output_dir / f"{func_name}_result.json")
        self.main_window.info_dialog(
            title="Save output", message="All plots have been saved successfully!"
        )

    def read_csv(self, filepath):
        """
        Read data from csv file.

        If failing to read the file, reset the input file path and fit data.

        :param filepath: path of the csv file
        """
        try:
            self.data_columns_box.read_csv(filepath)
        except FittingDataError as error:
            self.main_window.error_dialog(title="Input data error", message=str(error))
            self.data_columns_box.fitting_data = None
            self.input_file_box.file_path = None

    def read_excel(self, filepath, sheet):
        """
        Read data from excel file.

        If failing to read the file, reset the selected sheet and fit data.

        :param filepath: path of the excel file
        :param sheet: sheet from which to read the data.
        """
        try:
            self.data_columns_box.read_excel(filepath, sheet)
        except FittingDataError as error:
            self.main_window.error_dialog(title="Input data error", message=str(error))
            self.data_columns_box.fitting_data = None
            self.input_file_box.selected_sheet = None

    def choose_records(self, widget):  # pylint: disable=unused-argument
        """Open the choose records window."""
        if self.data_columns_box.fitting_data is None:
            self.main_window.info_dialog(
                title="Choose Records", message="No data been given yet"
            )
            return
        window = RecordsChoiceWindow(
            fitting_data=self.data_columns_box.fitting_data, app=self
        )
        window.show()
        self.reset_fitting_result()

    def fit(self, widget):  # pylint: disable=unused-argument
        """Handler for the "fit" button."""
        try:
            if self.fitting_result is None:
                self.main_window.info_dialog(
                    title="Fit Result", message="Nothing to fit yet"
                )
                return
        except EddingtonException:
            return
        self.main_window.info_dialog(
            title="Fit Result", message=str(self.fitting_result)
        )

    def plot_data(self, widget):  # pylint: disable=unused-argument
        """Handler for the "plot data" button."""
        if self.data_columns_box.fitting_data is None:
            self.show_nothing_to_plot()
        else:
            self.show_figure_window(
                fig=self.plot_configuration_box.plot_data(
                    data=self.data_columns_box.fitting_data
                ),
                title="Data Plot",
            )

    def plot_initial_guess(self, widget):  # pylint: disable=unused-argument
        """Handler for the "plot initial guess" button."""
        try:
            if (
                self.data_columns_box.fitting_data is None
                or self.initial_guess_box.a0 is None  # noqa: W503
            ):
                self.show_nothing_to_plot()
                return
            self.show_figure_window(
                fig=self.plot_configuration_box.plot_fitting(
                    func=self.fitting_function_box.fitting_function,
                    data=self.data_columns_box.fitting_data,
                    a=self.initial_guess_box.a0,
                ),
                title="Initial Guess Fitting",
            )
        except EddingtonException as error:
            self.main_window.error_dialog(
                title="Plot initial guess error", message=str(error)
            )

    def plot(self, widget):  # pylint: disable=unused-argument
        """Handler for the "plot fitting" button."""
        try:
            if self.fitting_result is None:
                self.show_nothing_to_plot()
                return
            self.show_figure_window(
                fig=self.plot_configuration_box.plot_fitting(
                    func=self.fitting_function_box.fitting_function,
                    data=self.data_columns_box.fitting_data,
                    a=self.fitting_result.a,
                ),
                title="Fitting Plot",
            )
        except EddingtonException as error:
            self.main_window.error_dialog(
                title="Plot fitting error", message=str(error)
            )

    def residuals(self, widget):  # pylint: disable=unused-argument
        """Handler for the "residuals" button."""
        try:
            if self.fitting_result is None:
                self.show_nothing_to_plot()
                return
            self.show_figure_window(
                fig=self.plot_configuration_box.plot_residuals(
                    func=self.fitting_function_box.fitting_function,
                    data=self.data_columns_box.fitting_data,
                    a=self.fitting_result.a,
                ),
                title="Residuals Plot",
            )
        except EddingtonException as error:
            self.main_window.error_dialog(
                title="Plot residuals error", message=str(error)
            )

    def show_nothing_to_plot(self):
        """Show dialog indicating that there is nothing to plot yet."""
        self.main_window.info_dialog(title="Fit Result", message="Nothing to plot yet")

    def show_figure_window(self, fig, title):
        """Open a window with matplotlib window."""
        figure_window = FigureWindow(figure=fig, title=title, app=self)
        figure_window.show()

    def reset_fitting_data(self):
        """Set fit data to None."""
        self.data_columns_box.fitting_data = None

    def reset_fitting_result(self):
        """Set fit result to None."""
        self.fitting_result = None

    def set_parameters_number(self, func):
        """Set number of parameters."""
        self.initial_guess_box.n = 0 if func is None else func.n

    def __calculate_fitting_result(self):
        if (
            self.data_columns_box.fitting_data is None
            or self.fitting_function_box.fitting_function is None  # noqa: W503
        ):
            self.fitting_result = None
            return
        try:
            self.fitting_result = fit(
                data=self.data_columns_box.fitting_data,
                func=self.fitting_function_box.fitting_function,
                a0=self.initial_guess_box.a0,
            )
        except EddingtonException as error:
            self.fitting_result = None
            self.main_window.error_dialog(title="Fit result error", message=str(error))
            raise error

    def select_default_sheet(self):
        """
        Automatically choose the first valid sheet.

        If it fails to find a valid sheet, resets the input file.
        """
        for sheet in self.input_file_box.sheets_options:
            if sheet != NO_VALUE:
                try:
                    self.data_columns_box.fitting_data = FittingData.read_from_excel(
                        Path(self.input_file_box.file_path), sheet
                    )
                    self.input_file_box.selected_sheet = sheet
                    return
                except FittingDataError:
                    pass

        if self.data_columns_box.fitting_data is None:
            self.main_window.error_dialog(
                title="Input data error",
                message=(
                    "No sheet available with valid data.\n"
                    "Please fix the file or load another one."
                ),
            )
            self.input_file_box.file_path = None


def main():
    """Main function."""
    return EddingtonGUI()
