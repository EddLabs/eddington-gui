"""Box for choosing a fitting function to use."""
import importlib.util
from typing import Callable, List

import toga
from eddington import FitFunction, FitFunctionsRegistry
from toga.style import Pack
from toga.style.pack import COLUMN

from eddington_gui.boxes.line_box import LineBox
from eddington_gui.consts import BIG_PADDING, NO_VALUE, PARAMETER_WIDTH


class FittingFunctionBox(toga.Box):
    """Visual box instance for choosing a fitting function."""

    fitting_function_selection: toga.Selection
    fitting_function_syntax: toga.TextInput
    load_module_button: toga.Button

    __fit_function: FitFunction = None
    __handlers: List[Callable] = []

    def __init__(self, flex):
        """Initialize box."""
        super().__init__(style=Pack(direction=COLUMN, flex=flex))
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

        self.update_fitting_function_options()

    def add_handler(self, handler):
        """
        Add handler to run whenever the fitting function is updated.

        :param handler: Callable
        """
        self.__handlers.append(handler)

    def update_fitting_function_options(self):
        """Update the fitting functions options."""
        self.fitting_function_selection.items = [NO_VALUE] + list(
            FitFunctionsRegistry.names()
        )

    def load_select_fit_function_name(self, widget):  # pylint: disable=unused-argument
        """Load the selection fitting function from the FitFunctionRegistry."""
        if self.fit_function_state == NO_VALUE:
            self.fit_function = None
            self.fitting_function_syntax.value = ""
            return
        self.fit_function = FitFunctionsRegistry.load(self.fit_function_state)
        self.fitting_function_syntax.value = self.fit_function.syntax

    def load_module(self, widget):  # pylint: disable=unused-argument
        """
        Open a file dialog in order to load user module.

        This is done in order to add costume fitting functions.
        """
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

    @property
    def fit_function(self):
        """Getter of the fitting function."""
        return self.__fit_function

    @fit_function.setter
    def fit_function(self, fit_function):
        """
        Setter of the fitting function.

        After setting the fit function, run handlers in order to notify other
        components of the change.
        """
        self.__fit_function = fit_function
        for handler in self.__handlers:
            handler(self.fit_function)

    @property
    def fit_function_state(self):
        """Set fit function state."""
        return self.fitting_function_selection.value
