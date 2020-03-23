from typing import Union
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, CENTER

from eddington import PlotConfiguration

from eddington_gui.boxes.line_box import LineBox
from eddington_gui.consts import X_COLUMN, Y_COLUMN, INPUT_WIDTH
from eddington_gui.util import value_or_none


class PlotConfigurationBox(toga.Box):

    __title_input: toga.TextInput
    __residuals_title_input: toga.TextInput
    __xlabel_input: toga.TextInput
    __ylabel_input: toga.TextInput
    __grid_switch: toga.Switch

    __func_name: Union[str, None] = None
    __xmin: Union[float, None] = None
    __xmax: Union[float, None] = None
    __xcolumn: Union[str, None] = None
    __ycolumn: Union[str, None] = None

    __plot_configuration: Union[PlotConfiguration, None] = None

    def __init__(self):
        super(PlotConfigurationBox, self).__init__(style=Pack(direction=COLUMN, flex=1))

        self.__title_input = self.__add_column_option("Title:")
        self.__residuals_title_input = self.__add_column_option("Residuals title:")
        self.__xlabel_input = self.__add_column_option("X label:")
        self.__ylabel_input = self.__add_column_option("Y label:")

        self.__grid_switch = toga.Switch(
            style=Pack(alignment=CENTER),
            label="Grid",
            on_toggle=lambda _: self.reset_plot_configuration(),
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
            self.__func_name = None
        else:
            self.__func_name = fit_function.title_name
        self.reset_plot_configuration()

    def set_xmin_xmax(self, x):
        self.__xmin, self.__xmax = PlotConfiguration.get_plot_borders(x)
        self.reset_plot_configuration()

    def load_columns(self, columns):
        self.__xcolumn = columns[X_COLUMN]
        self.__ycolumn = columns[Y_COLUMN]
        self.reset_plot_configuration()

    def reset_plot_configuration(self):
        self.plot_configuration = None

    def on_input_change(self, widget):
        self.reset_plot_configuration()

    def __build_plot_configuration(self):
        self.plot_configuration = PlotConfiguration.build(
            func_name=self.__func_name,
            xmin=self.__xmin,
            xmax=self.__xmax,
            xcolumn=self.__xcolumn,
            ycolumn=self.__ycolumn,
            title=self.title,
            residuals_title=self.residuals_title,
            xlabel=self.xlabel,
            ylabel=self.ylabel,
            grid=self.__grid_switch.is_on,
        )

    def __add_column_option(self, label):

        text_input = toga.TextInput(
            on_change=self.on_input_change, style=Pack(width=INPUT_WIDTH),
        )
        line = LineBox(
            children=[toga.Label(text=label), toga.Box(style=Pack(flex=1)), text_input]
        )

        self.add(line)
        return text_input
