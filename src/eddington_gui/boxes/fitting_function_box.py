import importlib.util
from typing import List, Callable

import toga
from toga.style import Pack
from toga.style.pack import COLUMN

from eddington import (
    FitFunctionsRegistry,
    FitFunction,
)

from eddington_gui.boxes.line_box import LineBox
from eddington_gui.consts import NO_VALUE, BIG_PADDING, PARAMETER_WIDTH


class FittingFunctionBox(toga.Box):

    fitting_function_selection: toga.Selection
    fitting_function_syntax: toga.TextInput
    parameters_box: LineBox
    parameter_inputs: toga.TextInput
    load_module_button: toga.Button

    __fit_function: FitFunction = None
    __handlers: List[Callable] = []

    def __init__(self, flex):
        super(FittingFunctionBox, self).__init__(
            style=Pack(direction=COLUMN, flex=flex)
        )
        fit_function_box = LineBox()
        fit_function_box.add(toga.Label(text="Fitting function:"))
        self.fitting_function_selection = toga.Selection(
            on_select=self.load_select_fit_function_name,
        )
        fit_function_box.add(self.fitting_function_selection)
        self.fitting_function_syntax = toga.TextInput(
            readonly=True,
            style=Pack(flex=1, padding_left=BIG_PADDING, padding_right=BIG_PADDING),
        )
        fit_function_box.add(self.fitting_function_syntax)
        self.load_module_button = toga.Button(
            label="Load module", on_press=self.load_module
        )
        fit_function_box.add(self.load_module_button)
        self.add(fit_function_box)

        self.parameters_box = LineBox()
        self.parameters_box.add(toga.Label("Parameters:"))
        self.parameter_inputs = toga.TextInput(
            readonly=True,
            style=Pack(width=PARAMETER_WIDTH),
            on_change=self.on_parameters_change,
        )
        self.parameters_box.add(self.parameter_inputs)
        self.add(self.parameters_box)

        self.update_fitting_function_options()

    def add_handler(self, handler):
        self.__handlers.append(handler)

    def update_fitting_function_options(self):
        self.fitting_function_selection.items = [NO_VALUE] + list(
            FitFunctionsRegistry.names()
        )

    def load_select_fit_function_name(self, widget):
        self.disable_free_syntax()
        if self.fit_function_state == NO_VALUE:
            self.reset_fit_function()
            return
        self.fit_function = FitFunctionsRegistry.load(self.fit_function_state)
        self.fitting_function_syntax.value = self.fit_function.syntax

    def load_module(self, widget):
        try:
            file_path = self.window.open_file_dialog(
                title="Choose module file", multiselect=False
            )
        except ValueError:
            return
        spec = importlib.util.spec_from_file_location("eddington.dummy", file_path)
        dummy_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(dummy_module)
        self.update_fitting_function_options()

    def on_parameters_change(self, widget):
        self.reset_fit_function()

    def reset_fit_function(self):
        self.fit_function = None

    @property
    def fit_function(self):
        return self.__fit_function

    @fit_function.setter
    def fit_function(self, fit_function):
        self.__fit_function = fit_function
        for handler in self.__handlers:
            handler(self.fit_function)

    @property
    def fit_function_state(self):
        return self.fitting_function_selection.value

    def enable_free_syntax(self):
        self.fitting_function_syntax.value = None
        self.fitting_function_syntax.placeholder = "Enter fit function in python syntax"
        self.fitting_function_syntax.readonly = False

    def disable_free_syntax(self):
        self.fitting_function_syntax.value = None
        self.fitting_function_syntax.placeholder = None
        self.fitting_function_syntax.readonly = True
