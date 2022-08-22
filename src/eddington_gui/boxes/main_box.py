import importlib
from pathlib import Path
from typing import Optional, Union

import numpy as np
import toga
from eddington import (
    EddingtonException,
    FigureBuilder,
    FittingData,
    FittingDataError,
    FittingResult,
    fit,
    show_or_export,
)
from eddington.interval import Interval
from eddington.plot.figure import Figure
from toga.style import Pack
from travertino.constants import COLUMN

from eddington_gui.boxes.data_columns_box import DataColumnsBox
from eddington_gui.boxes.eddington_box import EddingtonBox
from eddington_gui.boxes.fitting_function_box import FittingFunctionBox
from eddington_gui.boxes.footer_box import FooterBox
from eddington_gui.boxes.header_box import HeaderBox
from eddington_gui.boxes.input_file_box import InputFileBox
from eddington_gui.boxes.output_box import OutputBox
from eddington_gui.boxes.parameters_box import ParametersBox
from eddington_gui.boxes.plot_configuration_box import PlotConfigurationBox
from eddington_gui.buttons.plot_button import PlotButton
from eddington_gui.consts import NO_VALUE, SMALL_PADDING
from eddington_gui.window.explore_window import ExploreWindow
from eddington_gui.window.records_choice_window import RecordsChoiceWindow


class MainBox(EddingtonBox):

    input_file_box: InputFileBox
    fitting_function_box: FittingFunctionBox
    initial_guess_box: ParametersBox
    data_columns_box: DataColumnsBox
    plot_options_container: toga.OptionContainer
    output_box: OutputBox

    __a0: Optional[np.ndarray] = None
    __fitting_result: Optional[FittingResult] = None

    def __init__(self):
        super(MainBox, self).__init__(style=Pack(direction=COLUMN))

        self.add(HeaderBox())
        self.input_file_box = InputFileBox(on_choose_record=self.choose_records)
        self.input_file_box.on_input_file_change = self.reset_fitting_data
        self.input_file_box.on_csv_read = self.read_csv
        self.input_file_box.on_excel_read = self.read_excel
        self.input_file_box.on_select_excel_file = self.select_default_sheet
        self.add(self.input_file_box)

        self.data_columns_box = DataColumnsBox(
            on_columns_change=self.on_data_columns_change
        )
        self.data_columns_box.add(
            toga.Button(
                "Explore", on_press=self.explore, style=Pack(padding_left=SMALL_PADDING)
            )
        )
        self.add(self.data_columns_box)

        self.fitting_function_box = FittingFunctionBox(
            on_fitting_function_load=self.on_fitting_function_load
        )
        self.fitting_function_box.add(
            toga.Button(text="Fit", on_press=self.fit),
            toga.Button(text="Load module", on_press=self.load_module),
        )
        self.add(self.fitting_function_box)

        self.initial_guess_box = ParametersBox(
            on_parameters_change=self.reset_fitting_result
        )
        self.initial_guess_box.add(toga.Label(text="Initial Guess:"))
        self.add(self.initial_guess_box)

        self.plot_boxes = {}
        self.can_plot_map = {}
        self.add_plot_configuration_box(
            option_text="Data",
            button_text="Plot data",
            additional_instructions=self.plot_data_instructions,
            can_plot=self.can_plot_data,
            suffix="Data",
            has_legend=False,
        )
        self.add_plot_configuration_box(
            option_text="Initial guess",
            button_text="Plot initial guess",
            additional_instructions=self.plot_initial_guess_instructions,
            suffix="Initial Guess",
            can_plot=self.can_plot_initial_guess,
        )
        self.add_plot_configuration_box(
            option_text="Fit",
            button_text="Plot fit",
            additional_instructions=self.plot_fitting_instructions,
            suffix="Fitting",
            can_plot=self.can_plot_fit,
        )
        self.add_plot_configuration_box(
            option_text="Residuals",
            button_text="Plot residuals",
            additional_instructions=self.plot_residuals_instructions,
            suffix="Residuals",
            can_plot=self.can_plot_fit,
            has_legend=False,
        )
        self.plot_options_container = toga.OptionContainer(style=Pack(flex=5))
        for label, box in self.plot_boxes.items():
            self.plot_options_container.add(label, box)

        self.add(self.plot_options_container)

        self.output_box = OutputBox(on_save_output=self.on_save_output)
        self.add(self.output_box)

        self.add(FooterBox())

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

    def add_plot_configuration_box(  # pylint: disable=too-many-arguments
        self,
        option_text,
        button_text,
        additional_instructions,
        can_plot,
        suffix,
        has_legend=True,
    ):
        """Build a plot configuration box."""
        plot_configuration_box = PlotConfigurationBox(
            additional_instructions=additional_instructions,
            suffix=suffix,
            has_legend=has_legend,
        )
        plot_configuration_box.add(
            PlotButton(
                text=button_text,
                can_plot=can_plot,
                on_draw=plot_configuration_box.on_draw,
                plot_title=suffix,
            )
        )
        self.plot_boxes[option_text] = plot_configuration_box
        self.can_plot_map[option_text] = can_plot

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
            self.window.error_dialog(
                title="Results output save error",
                message="No output directory was chosen",
            )
            return
        output_dir = Path(self.output_box.output_directory)
        if not output_dir.exists():
            output_dir.mkdir()
        for option_label, plot_box in self.plot_boxes.items():
            if self.can_plot_map[option_label]():
                with Figure() as fig:
                    plot_box.on_draw(plot_box, fig)
                    show_or_export(fig, output_dir / plot_box.file_name)
        if self.fitting_function_box.fitting_function is not None:
            func_name = self.fitting_function_box.fitting_function.name
            self.fitting_result.save_txt(output_dir / f"{func_name}_result.txt")
            self.fitting_result.save_json(output_dir / f"{func_name}_result.json")
        self.window.info_dialog(
            title="Save output", message="All plots have been saved successfully!"
        )

    def read_csv(self, filepath: Union[str, Path]):
        """
        Read data from csv file.

        If failing to read the file, reset the input file path and fit data.

        :param filepath: path of the csv file
        :type filepath: Union[str, Path]
        """
        try:
            self.data_columns_box.read_csv(filepath)
        except FittingDataError as error:
            self.window.error_dialog(title="Input data error", message=str(error))
            self.data_columns_box.fitting_data = None
            self.input_file_box.file_path = None

    def read_excel(self, filepath: Union[str, Path], sheet: str):
        """
        Read data from excel file.

        If failing to read the file, reset the selected sheet and fit data.

        :param filepath: path of the excel file
        :type filepath: Union[str, Path]
        :param sheet: sheet from which to read the data.
        :type sheet: str
        """
        try:
            self.data_columns_box.read_excel(filepath, sheet)
        except FittingDataError as error:
            self.window.error_dialog(title="Input data error", message=str(error))
            self.data_columns_box.fitting_data = None
            self.input_file_box.selected_sheet = None

    def choose_records(self, widget):  # pylint: disable=unused-argument
        """Open the choose records window."""
        if self.data_columns_box.fitting_data is None:
            self.window.info_dialog(
                title="Choose Records", message="No data been given yet"
            )
            return
        window = RecordsChoiceWindow(
            fitting_data=self.data_columns_box.fitting_data,
            font_size=self.__font_size,
            app=self.app,
        )
        window.show()

    def can_plot_fit(self):
        """Can plot a fitting plot."""
        return (
            self.fitting_result is not None
            and self.fitting_function_box.fitting_function is not None  # noqa: W503
            and self.__has_data()  # noqa: W503
        )

    def can_plot_data(self):
        """Can plot a data plot."""
        return self.__has_data()

    def can_plot_initial_guess(self):
        """Can plot initial guess plot."""
        return (
            self.initial_guess_box.a0 is not None
            and self.fitting_function_box.fitting_function is not None  # noqa: W503
            and self.__has_data()  # noqa: W503
        )

    def plot_data_instructions(
        self, figure_builder: FigureBuilder, interval: Interval
    ):  # pylint: disable=unused-argument
        """Instruction for plotting data."""
        figure_builder.add_data(data=self.data_columns_box.fitting_data, label="Data")

    def plot_initial_guess_instructions(
        self, figure_builder: FigureBuilder, interval: Interval
    ):
        """Instruction for plotting initial guess."""
        figure_builder.add_plot(
            interval=interval.intersect(self.data_columns_box.fitting_data.x_domain),
            func=self.fitting_function_box.fitting_function,
            a=self.fitting_result.a0,
            label="Initial Guess",
        )

    def plot_fitting_instructions(
        self, figure_builder: FigureBuilder, interval: Interval
    ):
        """Instruction for plotting fitting."""
        figure_builder.add_plot(
            interval=interval.intersect(self.data_columns_box.fitting_data.x_domain),
            func=self.fitting_function_box.fitting_function,
            a=self.fitting_result.a,
            label="Fitting",
        )

    def plot_residuals_instructions(  # pylint: disable=unused-argument
        self, figure_builder: FigureBuilder, interval: Interval
    ):
        """Instruction for plotting residuals."""
        y = self.fitting_function_box.fitting_function(  # pylint: disable=not-callable
            self.fitting_result.a, self.data_columns_box.fitting_data.x
        )
        figure_builder.add_error_bar(
            x=self.data_columns_box.fitting_data.x,
            y=y,
            xerr=self.data_columns_box.fitting_data.xerr,
            yerr=self.data_columns_box.fitting_data.yerr,
            label="Residuals",
        )

    def explore(self, widget):  # pylint: disable=unused-argument
        """Explore different fitting functions and parameters to fit the data."""
        if not self.__has_data():
            self.app.show_nothing_to_plot()
            return
        window = ExploreWindow(
            data=self.data_columns_box.fitting_data,
            app=self.app,
            font_size=self.window.content.font_size,
        )
        window.show()

    def fit(self, widget):  # pylint: disable=unused-argument
        """Handler for the "fit" button."""
        try:
            if self.fitting_result is None:
                self.app.show_nothing_to_plot()
                return
        except EddingtonException:
            return
        self.window.info_dialog(title="Fit Result", message=str(self.fitting_result))

    async def load_module(self, widget):  # pylint: disable=unused-argument
        """
        Open a file dialog in order to load user module.

        This is done in order to add costume fitting functions.
        """
        file_path = await self.window.open_file_dialog(
            title="Choose module file", multiselect=False, file_types=["py"]
        )
        if file_path is None:
            return
        spec = importlib.util.spec_from_file_location("eddington.dummy", file_path)
        dummy_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(dummy_module)
        self.fitting_function_box.update_fitting_function_options()

    def reset_fitting_data(self):
        """Set fit data to None."""
        self.data_columns_box.fitting_data = None

    def reset_fitting_result(self):
        """Set fit result to None."""
        self.fitting_result = None

    def set_parameters_number(self, func):
        """Set number of parameters."""
        self.initial_guess_box.n = 0 if func is None else func.n

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
            self.window.error_dialog(
                title="Input data error",
                message=(
                    "No sheet available with valid data.\n"
                    "Please fix the file or load another one."
                ),
            )
            self.input_file_box.file_path = None

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
            self.window.error_dialog(title="Fit result error", message=str(error))
            raise error

    def __has_data(self):
        return self.data_columns_box.fitting_data is not None and any(
            self.data_columns_box.fitting_data.records_indices
        )
