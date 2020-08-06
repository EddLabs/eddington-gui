from typing import Union
import toga
from toga.style import Pack
from toga.style.pack import COLUMN

from eddington_matplotlib import PlotConfiguration

from eddington_gui.boxes.line_box import LineBox
from eddington_gui.consts import LABEL_WIDTH, LONG_INPUT_WIDTH
from eddington_gui.util import value_or_none


class PlotConfigurationBox(toga.Box):

    __title_input: toga.TextInput
    __residuals_title_input: toga.TextInput
    __xlabel_input: toga.TextInput
    __ylabel_input: toga.TextInput
    __grid_switch: toga.Switch

    __base_name: Union[str] = ""
    __xmin: Union[float, None] = None
    __xmax: Union[float, None] = None
    __xcolumn: Union[str, None] = None
    __ycolumn: Union[str, None] = None

    __plot_configuration: Union[PlotConfiguration, None] = None

    def __init__(self, flex):
        super(PlotConfigurationBox, self).__init__(
            style=Pack(direction=COLUMN, flex=flex)
        )

        self.__title_input = self.__add_column_option("Title:")
        self.__residuals_title_input = self.__add_column_option("Residuals title:")
        self.__xlabel_input = self.__add_column_option("X label:")
        self.__ylabel_input = self.__add_column_option("Y label:")

        self.__grid_switch = toga.Switch(
            label="Grid", on_toggle=lambda _: self.reset_plot_configuration(),
        )
        self.add(LineBox(children=[self.__grid_switch]))

    @property
    def plot_configuration(self):
        if self.__plot_configuration is None:
            self.__build_plot_configuration()
        return self.__plot_configuration

    @plot_configuration.setter
    def plot_configuration(self, plot_configuration):
        self.__plot_configuration = plot_configuration

    @property
    def title(self):
        return value_or_none(self.__title_input.value)

    @property
    def residuals_title(self):
        return value_or_none(self.__residuals_title_input.value)

    @property
    def xlabel(self):
        return value_or_none(self.__xlabel_input.value)

    @property
    def ylabel(self):
        return value_or_none(self.__ylabel_input.value)

    def load_fit_function(self, fit_function):
        if fit_function is None:
            self.__base_name = ""
        else:
            self.__base_name = fit_function.title_name
        self.reset_plot_configuration()

    def set_xmin_xmax(self, x):
        self.__xmin, self.__xmax = PlotConfiguration.get_plot_borders(x)
        self.reset_plot_configuration()

    def load_fit_data(self, fit_data):
        self.__xcolumn = fit_data.x_column
        self.__ycolumn = fit_data.y_column
        self.set_xmin_xmax(fit_data.x)
        self.reset_plot_configuration()

    def reset_plot_configuration(self):
        self.plot_configuration = None

    def on_input_change(self, widget):
        self.reset_plot_configuration()

    def __build_plot_configuration(self):
        self.plot_configuration = PlotConfiguration.build(
            base_name=self.__base_name,
            xmin=self.__xmin,
            xmax=self.__xmax,
            xcolumn=self.__xcolumn,
            ycolumn=self.__ycolumn,
            title=self.title,
            residuals_title=self.residuals_title,
            xlabel=self.xlabel,
            ylabel=self.ylabel,
            grid=self.__grid_switch.is_on,
            plot_data=True,
            plot_fitting=True,
            plot_residuals=True,
        )

    def __add_column_option(self, label):

        text_input = toga.TextInput(
            on_change=self.on_input_change, style=Pack(width=LONG_INPUT_WIDTH),
        )
        line = LineBox(
            children=[
                toga.Label(text=label, style=Pack(width=LABEL_WIDTH)),
                text_input,
            ],
        )

        self.add(line)
        return text_input
