"""Box for setting up plot configuration for the output graphs."""
from typing import Union
import toga
from toga.style import Pack
from toga.style.pack import COLUMN

from eddington_matplotlib import PlotConfiguration

from eddington_gui.boxes.line_box import LineBox
from eddington_gui.consts import LABEL_WIDTH, LONG_INPUT_WIDTH
from eddington_gui.util import value_or_none


class PlotConfigurationBox(toga.Box):  # pylint: disable=too-many-instance-attributes
    """Visual box to create plot configuration."""

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
        """Initialize box."""
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
        """
        Getter of the plot configuration.

        If plot configuration is None, try to create one.
        """
        if self.__plot_configuration is None:
            self.__build_plot_configuration()
        return self.__plot_configuration

    @plot_configuration.setter
    def plot_configuration(self, plot_configuration):
        """Setter of the plot configuration."""
        self.__plot_configuration = plot_configuration

    @property
    def title(self):
        """Getter of the fitting graph title."""
        return value_or_none(self.__title_input.value)

    @property
    def residuals_title(self):
        """Getter of the residuals graph title."""
        return value_or_none(self.__residuals_title_input.value)

    @property
    def xlabel(self):
        """Getter of the label of the x axis."""
        return value_or_none(self.__xlabel_input.value)

    @property
    def ylabel(self):
        """Getter of the label of the y axis."""
        return value_or_none(self.__ylabel_input.value)

    def on_fit_function_load(self, fit_function):
        """
        Handler to run whenever the fit function is updated.

        Updates the basename and reset the plot configuration.
        """
        if fit_function is None:
            self.__base_name = ""
        else:
            self.__base_name = fit_function.title_name
        self.reset_plot_configuration()

    def on_fit_data_load(self, fit_data):
        """
        Handler to run whenever the fit function is updated.

        Updates the basename and reset the plot configuration.
        """
        if fit_data is None:
            self.__xcolumn, self.__ycolumn = None, None
            self.__xmin, self.__xmax = None, None
        else:
            self.__xcolumn, self.__ycolumn = fit_data.x_column, fit_data.y_column
            self.__xmin, self.__xmax = PlotConfiguration.get_plot_borders(fit_data.x)
        self.reset_plot_configuration()

    def reset_plot_configuration(self):
        """Set plot configuration to be None."""
        self.plot_configuration = None

    def on_input_change(self, widget):  # pylint: disable=unused-argument
        """Run whenever the selection widgets has been changed."""
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
