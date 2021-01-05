"""Main app."""
import importlib
import webbrowser
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import requests
import toga
from eddington import (
    EddingtonException,
    FittingData,
    FittingDataError,
    FittingResult,
    fit,
    plot_data,
    plot_fitting,
    plot_residuals,
    show_or_export,
)
from lastversion.lastversion import latest
from packaging.version import parse as parse_version
from toga.style import Pack
from toga.style.pack import COLUMN

from eddington_gui import __version__, has_matplotlib
from eddington_gui.boxes.data_columns_box import DataColumnsBox
from eddington_gui.boxes.eddington_box import EddingtonBox
from eddington_gui.boxes.figure_box import FigureBox
from eddington_gui.boxes.fitting_function_box import FittingFunctionBox
from eddington_gui.boxes.footer_box import FooterBox
from eddington_gui.boxes.header_box import HeaderBox
from eddington_gui.boxes.input_file_box import InputFileBox
from eddington_gui.boxes.output_box import OutputBox
from eddington_gui.boxes.parameters_box import ParametersBox
from eddington_gui.boxes.plot_configuration_box import PlotConfigurationBox
from eddington_gui.boxes.save_figure_button import SaveFigureButton
from eddington_gui.consts import (
    FIGURE_WINDOW_SIZE,
    GITHUB_USER_NAME,
    MAIN_WINDOW_SIZE,
    NO_VALUE,
    SMALL_PADDING,
    FontSize,
)
from eddington_gui.window.explore_window import ExploreWindow
from eddington_gui.window.records_choice_window import RecordsChoiceWindow

PLOT_GROUP = toga.Group("Plot", order=2)


class EddingtonGUI(toga.App):  # pylint: disable=R0902,R0904
    """Main app instance."""

    input_file_box: InputFileBox
    fitting_function_box: FittingFunctionBox
    initial_guess_box: ParametersBox
    data_columns_box: DataColumnsBox
    plot_options_container: toga.OptionContainer
    output_box: OutputBox

    main_window: toga.Window
    plot_boxes: Dict[str, PlotConfigurationBox]

    __a0: Optional[np.ndarray] = None
    __fitting_result: Optional[FittingResult] = None
    __font_size: Optional[FontSize] = None
    __has_newer_version: bool = False

    def startup(self):
        """
        Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        main_box = EddingtonBox(style=Pack(direction=COLUMN))
        main_box.add(HeaderBox())

        self.input_file_box = InputFileBox(on_choose_record=self.choose_records)
        self.input_file_box.on_input_file_change = self.reset_fitting_data
        self.input_file_box.on_csv_read = self.read_csv
        self.input_file_box.on_excel_read = self.read_excel
        self.input_file_box.on_select_excel_file = self.select_default_sheet
        main_box.add(self.input_file_box)

        self.data_columns_box = DataColumnsBox(
            on_columns_change=self.on_data_columns_change
        )
        self.data_columns_box.add(
            toga.Button(
                "Explore", on_press=self.explore, style=Pack(padding_left=SMALL_PADDING)
            )
        )
        main_box.add(self.data_columns_box)

        self.fitting_function_box = FittingFunctionBox(
            on_fitting_function_load=self.on_fitting_function_load
        )
        self.fitting_function_box.add(
            toga.Button(label="Fit", on_press=self.fit),
            toga.Button(label="Load module", on_press=self.load_module),
        )
        main_box.add(self.fitting_function_box)

        self.initial_guess_box = ParametersBox(
            on_parameters_change=self.reset_fitting_result
        )
        self.initial_guess_box.add(toga.Label(text="Initial Guess:"))
        main_box.add(self.initial_guess_box)

        self.plot_boxes = {
            "Data": PlotConfigurationBox(
                "Plot data",
                plot_method=lambda **kwargs: plot_data(
                    data=self.data_columns_box.fitting_data, **kwargs
                ),
                suffix="Data",
                can_plot=self.can_plot_data,
                has_legend=False,
            ),
            "Initial guess": PlotConfigurationBox(
                "Plot initial guess",
                plot_method=lambda **kwargs: plot_fitting(
                    func=self.fitting_function_box.fitting_function,
                    data=self.data_columns_box.fitting_data,
                    a=self.initial_guess_box.a0,
                    **kwargs,
                ),
                suffix="Initial Guess",
                can_plot=self.can_plot_initial_guess,
            ),
            "Fit": PlotConfigurationBox(
                "Plot fit",
                plot_method=lambda **kwargs: plot_fitting(
                    func=self.fitting_function_box.fitting_function,
                    data=self.data_columns_box.fitting_data,
                    a=self.fitting_result.a,
                    **kwargs,
                ),
                suffix="Fitting",
                can_plot=self.can_plot_fit,
            ),
            "Residuals": PlotConfigurationBox(
                "Plot residuals",
                plot_method=lambda **kwargs: plot_residuals(
                    func=self.fitting_function_box.fitting_function,
                    data=self.data_columns_box.fitting_data,
                    a=self.fitting_result.a,
                    **kwargs,
                ),
                suffix="Residuals",
                can_plot=self.can_plot_fit,
                has_legend=False,
            ),
        }
        self.plot_options_container = toga.OptionContainer(style=Pack(flex=5))
        self.plot_options_container.app = self
        for label, box in self.plot_boxes.items():
            self.plot_options_container.add(label, box)

        main_box.add(self.plot_options_container)

        self.output_box = OutputBox(on_save_output=self.on_save_output)
        main_box.add(self.output_box)

        main_box.add(FooterBox())

        self.main_window = toga.MainWindow(
            title=self.formal_name, size=MAIN_WINDOW_SIZE
        )
        self.main_window.content = main_box

        self.check_latest_version()
        self.commands.add(
            # File group
            toga.Command(
                self.input_file_box.select_file,
                label="Upload data file",
                shortcut=toga.Key.MOD_1 + "o",
                group=toga.Group.FILE,
                order=1,
            ),
            toga.Command(
                self.load_module,
                label="Load module",
                shortcut=toga.Key.MOD_1 + "m",
                group=toga.Group.FILE,
                order=2,
            ),
            toga.Command(
                self.choose_records,
                label="Choose records",
                shortcut=toga.Key.MOD_1 + "d",
                group=toga.Group.FILE,
                order=3,
            ),
            toga.Command(
                self.output_box.choose_output_dir,
                label="Choose output directory",
                shortcut=toga.Key.MOD_1 + "u",
                group=toga.Group.FILE,
                order=4,
            ),
            toga.Command(
                self.on_save_output,
                label="Save plots and results",
                shortcut=toga.Key.MOD_1 + "s",
                group=toga.Group.FILE,
                order=5,
            ),
            toga.Command(
                lambda widget: self.open_latest_version_webpage(),
                label="Install Eddington-GUI latest version",
                group=toga.Group.FILE,
                order=6,
                enabled=self.has_newer_version,
            ),
            toga.Command(
                self.fit,
                label="Fit result",
                shortcut=toga.Key.MOD_1 + "e",
                group=PLOT_GROUP,
            ),
            toga.Command(
                lambda _: self.set_font_size(FontSize.SMALL),
                "Set small font size",
                group=toga.Group.VIEW,
                order=FontSize.SMALL.value,
            ),
            toga.Command(
                lambda _: self.set_font_size(FontSize.MEDIUM),
                "Set medium font size",
                group=toga.Group.VIEW,
                order=FontSize.MEDIUM.value,
            ),
            toga.Command(
                lambda _: self.set_font_size(FontSize.LARGE),
                "Set large font size",
                group=toga.Group.VIEW,
                order=FontSize.LARGE.value,
            ),
        )
        self.set_font_size(FontSize.DEFAULT)
        if not has_matplotlib:
            self.main_window.info_dialog(
                "Error",
                (
                    f"Error loading matplotlib.\nPlease go to {self.faq_url}"
                    " and see how to solve this problem"
                ),
            )
            webbrowser.open(self.faq_url)

        self.main_window.show()

        if self.has_newer_version and self.main_window.question_dialog(
            "Update is available",
            (
                f"A new version of {self.formal_name} is available! "
                "would you like to download it?"
            ),
        ):
            self.open_latest_version_webpage()

    @property
    def has_newer_version(self):
        """Get whether Eddington-GUI has a newer version."""
        return self.__has_newer_version

    @has_newer_version.setter
    def has_newer_version(self, has_newer_version):
        """Set whether Eddington-GUI has a newer version."""
        self.__has_newer_version = has_newer_version

    @property
    def latest_version_url(self):
        """Get URL of latest version."""
        return f"https://github.com/{GITHUB_USER_NAME}/{self.app_name}/releases/latest"

    @property
    def faq_url(self):
        """URL for frequently asked questions."""
        return f"https://{self.app_name}.readthedocs.io/en/latest/tutorials/faq.html"

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
        for plot_box in self.plot_boxes.values():
            plot_box.on_fitting_data_load(fitting_data)

    def on_fitting_function_load(self, fitting_function):
        """Run those methods when fitting function is changed."""
        self.reset_fitting_result()
        self.set_parameters_number(fitting_function)
        for plot_box in self.plot_boxes.values():
            plot_box.on_fitting_function_load(fitting_function)

    def on_save_output(self, widget):  # pylint: disable=unused-argument
        """Handler for the "save to output directory" button."""
        if self.output_box.output_directory is None:
            self.main_window.error_dialog(
                title="Results output save error",
                message="No output directory was chosen",
            )
            return
        output_dir = Path(self.output_box.output_directory)
        if not output_dir.exists():
            output_dir.mkdir()
        for plot_box in self.plot_boxes.values():
            if plot_box.can_plot():
                with plot_box.plot() as fig:
                    show_or_export(fig, output_dir / plot_box.file_name)
        if self.fitting_function_box.fitting_function is not None:
            func_name = self.fitting_function_box.fitting_function.name
            self.fitting_result.save_txt(output_dir / f"{func_name}_result.txt")
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
            fitting_data=self.data_columns_box.fitting_data,
            font_size=self.__font_size,
            app=self,
        )
        window.show()

    def can_plot_fit(self):
        """Can plot a fitting plot."""
        return (
            self.fitting_result is not None
            and self.fitting_function_box.fitting_function is not None  # noqa: W503
            and self.data_columns_box.fitting_data is not None  # noqa: W503
        )

    def can_plot_data(self):
        """Can plot a data plot."""
        return self.data_columns_box.fitting_data is not None

    def can_plot_initial_guess(self):
        """Can plot initial guess plot."""
        return (
            self.initial_guess_box.a0 is not None
            and self.fitting_function_box.fitting_function is not None  # noqa: W503
            and self.data_columns_box.fitting_data is not None  # noqa: W503
        )

    def explore(self, widget):  # pylint: disable=unused-argument
        """Explore different fitting functions and parameters to fit the data."""
        if self.data_columns_box.fitting_data is None:
            self.main_window.info_dialog(
                title="Explore", message="No data has been loaded yet"
            )
            return
        window = ExploreWindow(data=self.data_columns_box.fitting_data, app=self)
        window.show()

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

    def load_module(self, widget):  # pylint: disable=unused-argument
        """
        Open a file dialog in order to load user module.

        This is done in order to add costume fitting functions.
        """
        try:
            file_path = self.main_window.open_file_dialog(
                title="Choose module file", multiselect=False, file_types=["py"]
            )
        except ValueError:
            return
        spec = importlib.util.spec_from_file_location("eddington.dummy", file_path)
        dummy_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(dummy_module)
        self.fitting_function_box.update_fitting_function_options()

    def show_nothing_to_plot(self):
        """Show dialog indicating that there is nothing to plot yet."""
        self.main_window.info_dialog(title="Fit Result", message="Nothing to plot yet")

    def show_figure_window(self, plot_method, title):
        """Open a window with matplotlib window."""
        figure_window = toga.Window(title=title, size=FIGURE_WINDOW_SIZE)
        figure_box = FigureBox(plot_method=plot_method)
        figure_box.add(SaveFigureButton("save", plot_method=plot_method))
        figure_window.content = figure_box
        figure_window.app = self
        figure_window.content.set_font_size(self.__font_size)
        figure_window.content.draw()
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

    def set_font_size(self, font_size: FontSize):
        """Set font size to all components in app."""
        self.__font_size = font_size
        self.main_window.content.set_font_size(font_size)
        for plot_box in self.plot_boxes.values():
            plot_box.set_font_size(font_size)
        self.main_window.content.refresh()

    def check_latest_version(self):
        """Checker whether a new version of Eddington-GUI is available or not."""
        try:
            eddington_latest_version = str(latest(self.app_name))
            self.has_newer_version = parse_version(
                eddington_latest_version
            ) > parse_version(__version__)
        except requests.exceptions.ConnectionError:
            self.has_newer_version = False

    def open_latest_version_webpage(self):
        """Open latest version webpage."""
        webbrowser.open(self.latest_version_url)


def main():
    """Main function."""
    return EddingtonGUI()
