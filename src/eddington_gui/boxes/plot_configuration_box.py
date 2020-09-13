"""Box for setting up plot configuration for the output graphs."""
from typing import Union

import toga
from eddington import EddingtonException, plot_data, plot_fitting, plot_residuals
from toga.style import Pack
from toga.style.pack import COLUMN, HIDDEN, VISIBLE

from eddington_gui.boxes.line_box import LineBox
from eddington_gui.consts import LABEL_WIDTH, LONG_INPUT_WIDTH


class PlotConfigurationBox(toga.Box):  # pylint: disable=too-many-instance-attributes
    """Visual box to create plot configuration."""

    __title_input: toga.TextInput
    __residuals_title_input: toga.TextInput
    __xlabel_input: toga.TextInput
    __ylabel_input: toga.TextInput
    __grid_switch: toga.Switch
    __x_domain_switch: toga.Switch
    __x_min_title: toga.Label
    __x_min_input: toga.TextInput
    __x_max_title: toga.Label
    __x_max_input: toga.TextInput

    __base_name: Union[str] = ""
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

        self.__x_domain_switch = toga.Switch(
            label="Custom X domain", on_toggle=lambda _: self.x_domain_switch_handler()
        )
        self.__x_min_title = toga.Label("X minimum:", style=Pack(visibility=HIDDEN))
        self.__x_min_input = toga.TextInput(style=Pack(visibility=HIDDEN))
        self.__x_max_title = toga.Label("X maximum:", style=Pack(visibility=HIDDEN))
        self.__x_max_input = toga.TextInput(style=Pack(visibility=HIDDEN))
        self.add(
            LineBox(
                children=[
                    self.__x_domain_switch,
                    self.__x_min_title,
                    self.__x_min_input,
                    self.__x_max_title,
                    self.__x_max_input,
                ]
            )
        )

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

    @property
    def xmin(self):
        """Get minimum value of X, if presented by user."""
        if not self.__x_domain_switch.is_on or self.__x_min_input.value == "":
            return None
        try:
            return float(self.__x_min_input.value)
        except ValueError as error:
            raise EddingtonException(
                "X minimum value must a floating number"
            ) from error

    @property
    def xmax(self):
        """Get minimum value of X, if presented by user."""
        if not self.__x_domain_switch.is_on or self.__x_max_input.value == "":
            return None
        try:
            return float(self.__x_max_input.value)
        except ValueError as error:
            raise EddingtonException(
                "X maximum value must a floating number"
            ) from error

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
            xmin=self.xmin,
            xmax=self.xmax,
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
            xmin=self.xmin,
            xmax=self.xmax,
        )

    def on_fitting_function_load(self, fitting_function):
        """
        Handler to run whenever the fit function is updated.

        Updates the basename and reset the plot configuration.
        """
        if fitting_function is None:
            self.__base_name = ""
        else:
            self.__base_name = fitting_function.title_name

    def on_fitting_data_load(self, fitting_data):
        """
        Handler to run whenever the fit function is updated.

        Updates the basename and reset the plot configuration.
        """
        if fitting_data is None:
            self.__xcolumn, self.__ycolumn = None, None
        else:
            self.__xcolumn, self.__ycolumn = fitting_data.x_column, fitting_data.y_column

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

    def x_domain_switch_handler(self):
        """Handler to run whenever the custom x domain toggle is switched."""
        if self.__x_domain_switch.is_on:
            self.__x_min_title.style.visibility = VISIBLE
            self.__x_min_input.style.visibility = VISIBLE
            self.__x_max_title.style.visibility = VISIBLE
            self.__x_max_input.style.visibility = VISIBLE
        else:
            self.__x_min_input.value, self.__x_max_input.value = "", ""
            self.__x_min_title.style.visibility = HIDDEN
            self.__x_min_input.style.visibility = HIDDEN
            self.__x_max_title.style.visibility = HIDDEN
            self.__x_max_input.style.visibility = HIDDEN
