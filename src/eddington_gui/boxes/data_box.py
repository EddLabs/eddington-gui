from typing import List, Union
from collections import OrderedDict

from eddington.fit_functions.fit_functions_registry import FitFunctionsRegistry
from eddington.plot.configuration import PlotConfiguration
from eddington.fit_data import FitData
from eddington.input.reduction import reduce_data
from eddington.input.util import get_a0
from eddington.fit_util import fit_to_data

import toga
from toga.style import Pack
from toga.style.pack import ROW, COLUMN, LEFT

from eddington_gui.consts import NO_VALUE


class DataBox(toga.Box):

    SELECTION_WIDTH = 200

    __data_dict: OrderedDict = None
    __items: List[str] = []
    __selection_enabled: bool = False

    __fit_function = None
    __fit_data = None
    __fit_result = None
    __plot_configuration: Union[PlotConfiguration, None] = None

    fitting_function_selection: toga.Selection
    fitting_function_syntax: toga.TextInput

    x_selection: toga.Selection
    xerr_selection: toga.Selection
    y_selection: toga.Selection
    yerr_selection: toga.Selection

    def __init__(self):
        super(DataBox, self).__init__(style=Pack(direction=COLUMN))

        fitting_function_box = toga.Box(style=Pack(direction=ROW))
        fitting_function_box.add(toga.Label(text="Fitting function:"))
        self.fitting_function_selection = toga.Selection(items=[NO_VALUE] + list(FitFunctionsRegistry.names()),
                                                         on_select=self.load_fit_function)
        fitting_function_box.add(self.fitting_function_selection)
        self.fitting_function_syntax = toga.TextInput(readonly=True, style=Pack(padding_left=5, padding_right=5, flex=1))
        fitting_function_box.add(self.fitting_function_syntax)
        self.add(fitting_function_box)

        columns_box = toga.Box(style=Pack(direction=ROW, padding_top=5))
        labels_column = toga.Box(style=Pack(direction=COLUMN, flex=1))
        labels_column.add(toga.Label(text="X column:", style=Pack()))
        labels_column.add(toga.Label(text="X error column:"))
        labels_column.add(toga.Label(text="Y column:"))
        labels_column.add(toga.Label(text="Y error column:"))
        columns_box.add(labels_column)

        self.x_selection = toga.Selection(enabled=self.selection_enabled, on_select=self.reset_fit,
                                          style=Pack(alignment=LEFT, width=self.SELECTION_WIDTH))
        self.xerr_selection = toga.Selection(enabled=self.selection_enabled, on_select=self.reset_fit,
                                             style=Pack(alignment=LEFT, width=self.SELECTION_WIDTH))
        self.y_selection = toga.Selection(enabled=self.selection_enabled, on_select=self.reset_fit,
                                          style=Pack(alignment=LEFT, width=self.SELECTION_WIDTH))
        self.yerr_selection = toga.Selection(enabled=self.selection_enabled, on_select=self.reset_fit,
                                             style=Pack(alignment=LEFT, width=self.SELECTION_WIDTH))
        columns_box.add(toga.Box(style=Pack(direction=COLUMN, flex=2),
                                 children=[self.x_selection, self.xerr_selection,
                                           self.y_selection, self.yerr_selection]))
        self.add(columns_box)

    @property
    def items(self):
        return self.__items

    @items.setter
    def items(self, items):
        self.__items = items
        self.x_selection.items = items
        self.xerr_selection.items = items
        self.y_selection.items = items
        self.yerr_selection.items = items

    @property
    def selection_enabled(self):
        return self.__selection_enabled

    @selection_enabled.setter
    def selection_enabled(self, selection_enabled):
        self.__selection_enabled = selection_enabled
        self.x_selection.enabled = selection_enabled
        self.xerr_selection.enabled = selection_enabled
        self.y_selection.enabled = selection_enabled
        self.yerr_selection.enabled = selection_enabled

    @property
    def data_dict(self):
        return self.__data_dict

    @data_dict.setter
    def data_dict(self, data_dict):
        self.__data_dict = data_dict
        if data_dict is None:
            self.items = []
            self.selection_enabled = False
        else:
            self.items = list(data_dict.keys())
            self.selection_enabled = True

    @property
    def fit_function(self):
        return self.__fit_function

    @fit_function.setter
    def fit_function(self, fit_function):
        self.__fit_function = fit_function

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

    @property
    def plot_configuration(self):
        if self.__plot_configuration is None:
            self.__load_plot_configuration()
        return self.__plot_configuration

    @plot_configuration.setter
    def plot_configuration(self, plot_configuration):
        self.__plot_configuration = plot_configuration

    def load_fit_function(self, widget):
        self.fit_data = None
        self.fit_result = None
        self.plot_configuration = None
        if self.fitting_function_selection.value == NO_VALUE:
            self.fit_function = None
            self.fitting_function_syntax.value = None
        else:
            self.fit_function = FitFunctionsRegistry.load(self.fitting_function_selection.value)
            self.fitting_function_syntax.value = self.fit_function.syntax

    def __calculate_fit_data(self):
        if self.data_dict is None or self.fit_function is None:
            self.fit_data = None
            return
        reduced_data = reduce_data(data_dict=self.data_dict,
                                   x_column=self.x_selection.value, xerr_column=self.xerr_selection.value,
                                   y_column=self.y_selection.value, yerr_column=self.yerr_selection.value)
        self.fit_data = FitData.build_from_data_dict(data_dict=reduced_data, a0=get_a0(self.fit_function.n))

    def __calculate_fit_result(self):
        if self.fit_data is None or self.fit_function is None:
            self.fit_result = None
        else:
            self.fit_result = fit_to_data(self.fit_data, self.fit_function)

    def __load_plot_configuration(self):
        if self.fit_data is None:
            return None
        xmin, xmax = PlotConfiguration.get_plot_borders(self.fit_data.x)
        self.plot_configuration = PlotConfiguration.build(func_name=self.fit_function.name, xmin=xmin, xmax=xmax,
                                                          xcolumn=self.x_selection.value,
                                                          ycolumn=self.y_selection.value)

    def reset_fit(self, widget):
        self.fit_data = None
        self.fit_result = None
        self.plot_configuration = None
