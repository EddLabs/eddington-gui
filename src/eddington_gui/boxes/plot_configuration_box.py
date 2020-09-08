"""Box for setting up plot configuration for the output graphs."""
from typing import Union

import toga
from eddington import plot_data, plot_fitting, plot_residuals
from toga.style import Pack
from toga.style.pack import COLUMN

from eddington_gui.boxes.line_box import LineBox
from eddington_gui.consts import LABEL_WIDTH, LONG_INPUT_WIDTH


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

    def __init__(self, flex):
        """Initialize box."""
        super().__init__(style=Pack(direction=COLUMN, flex=flex))

        self.__title_input = self.__add_column_option("Title:")
        self.__residuals_title_input = self.__add_column_option("Residuals title:")
        self.__xlabel_input = self.__add_column_option("X label:")
        self.__ylabel_input = self.__add_column_option("Y label:")

        self.__grid_switch = toga.Switch(label="Grid")
        self.add(LineBox(children=[self.__grid_switch]))

    @property
    def title(self):
        """Getter of the fitting graph title."""
        if self.__title_input.value != "":
            return self.__title_input.value
        if self.__base_name is not None:
            return self.__base_name
        return None

    @property
    def data_title(self):
        """Getter of the data graph title."""
        if self.__base_name is not None:
            return f"{self.__base_name} - Data"
        return None

    @property
    def residuals_title(self):
        """Getter of the residuals graph title."""
        if self.__residuals_title_input.value != "":
            return self.__residuals_title_input.value
        if self.__base_name is not None:
            return f"{self.__base_name} - Residuals"
        return None

    @property
    def xlabel(self):
        """Getter of the label of the x axis."""
        if self.__xlabel_input.value != "":
            return self.__xlabel_input.value
        if self.__xcolumn is not None:
            return self.__xcolumn
        return None

    @property
    def ylabel(self):
        """Getter of the label of the y axis."""
        if self.__ylabel_input.value != "":
            return self.__ylabel_input.value
        if self.__ycolumn is not None:
            return self.__ycolumn
        return None

    @property
    def grid(self):
        """Should or should not add grid lines to plots."""
        return self.__grid_switch.is_on

    def plot_data(self, data):
        """Create a data plot."""
        return plot_data(
            data=data,
            title_name=self.data_title,
            xlabel=self.xlabel,
            ylabel=self.ylabel,
            grid=self.grid,
        )

    def plot_fitting(self, func, data, a):  # pylint: disable=invalid-name
        """Create a fitting plot."""
        return plot_fitting(
            func=func,
            data=data,
            title_name=self.title,
            xlabel=self.xlabel,
            ylabel=self.ylabel,
            grid=self.grid,
            a=a,
        )

    def plot_residuals(self, func, data, a):  # pylint: disable=invalid-name
        """Create residuals plot."""
        return plot_residuals(
            func=func,
            data=data,
            title_name=self.residuals_title,
            xlabel=self.xlabel,
            ylabel=self.ylabel,
            grid=self.grid,
            a=a,
        )

    def on_fit_function_load(self, fit_function):
        """
        Handler to run whenever the fit function is updated.

        Updates the basename and reset the plot configuration.
        """
        if fit_function is None:
            self.__base_name = ""
        else:
            self.__base_name = fit_function.title_name

    def on_fit_data_load(self, fit_data):
        """
        Handler to run whenever the fit function is updated.

        Updates the basename and reset the plot configuration.
        """
        if fit_data is None:
            self.__xcolumn, self.__ycolumn = None, None
        else:
            self.__xcolumn, self.__ycolumn = fit_data.x_column, fit_data.y_column

    def __add_column_option(self, label):

        text_input = toga.TextInput(style=Pack(width=LONG_INPUT_WIDTH))
        line = LineBox(
            children=[
                toga.Label(text=label, style=Pack(width=LABEL_WIDTH)),
                text_input,
            ],
        )

        self.add(line)
        return text_input
