"""Box for choosing a fitting function to use."""
import importlib.util
from typing import Callable, List

import toga
from eddington import FittingFunction, FittingFunctionsRegistry, polynomial
from toga.style import Pack
from toga.style.pack import COLUMN

from eddington_gui.boxes.line_box import LineBox
from eddington_gui.consts import BIG_PADDING, NO_VALUE, POLYNOMIAL


class FittingFunctionBox(toga.Box):  # pylint: disable=too-many-instance-attributes
    """Visual box instance for choosing a fitting function."""

    fit_function_box: LineBox
    fitting_function_selection: toga.Selection
    fitting_function_syntax: toga.TextInput
    polynomial_degree_title: toga.Label
    polynomial_degree_input: toga.NumberInput
    load_module_button: toga.Button

    __fit_function: FittingFunction = None
    __handlers: List[Callable] = []
    __polynomial_is_set: bool = False

    def __init__(self, flex):
        """Initialize box."""
        super().__init__(style=Pack(direction=COLUMN, flex=flex))
        self.fit_function_box = LineBox()
        self.fit_function_box.add(toga.Label(text="Fitting function:"))
        self.fitting_function_selection = toga.Selection(
            on_select=self.load_select_fit_function_name,
        )
        self.fit_function_box.add(self.fitting_function_selection)
        self.fitting_function_syntax = toga.TextInput(
            readonly=True,
            style=Pack(flex=1, padding_left=BIG_PADDING, padding_right=BIG_PADDING),
        )
        self.fit_function_box.add(self.fitting_function_syntax)
        self.load_module_button = toga.Button(
            label="Load module", on_press=self.load_module
        )
        self.fit_function_box.add(self.load_module_button)
        self.add(self.fit_function_box)

        self.polynomial_degree_title = toga.Label("Degree:")
        self.polynomial_degree_input = toga.NumberInput(
            min_value=1,
            max_value=5,
            default=1,
            on_change=lambda widget: self.set_polynomial_degree(),
        )

        self.update_fitting_function_options()

    def add_handler(self, handler):
        """
        Add handler to run whenever the fitting function is updated.

        :param handler: Callable
        """
        self.__handlers.append(handler)

    def update_fitting_function_options(self):
        """Update the fitting functions options."""
        self.fitting_function_selection.items = [NO_VALUE, POLYNOMIAL] + list(
            FittingFunctionsRegistry.names()
        )

    def load_select_fit_function_name(self, widget):  # pylint: disable=unused-argument
        """Load the selection fitting function from the FittingFunctionRegistry."""
        if self.fit_function_state == POLYNOMIAL and not self.__polynomial_is_set:
            self.fit_function_box.insert(2, self.polynomial_degree_title)
            self.fit_function_box.insert(3, self.polynomial_degree_input)
            self.set_polynomial_degree()
            self.__polynomial_is_set = True
            return
        if self.fit_function_state != POLYNOMIAL and self.__polynomial_is_set:
            self.fit_function_box.remove(self.polynomial_degree_title)
            self.fit_function_box.remove(self.polynomial_degree_input)
            self.__polynomial_is_set = False
        if self.fit_function_state == NO_VALUE:
            self.fit_function = None
            self.fitting_function_syntax.value = ""
            return
        self.fit_function = FittingFunctionsRegistry.load(self.fit_function_state)
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

    def set_polynomial_degree(self):
        """Set fitting function to be polynomial based on given degree."""
        degree = int(self.polynomial_degree_input.value)
        self.fit_function = polynomial(degree)
        if degree == 1:
            self.fitting_function_syntax.value = "a[0] + a[1] * x"
        else:
            self.fitting_function_syntax.value = "a[0] + a[1] * x + " + " + ".join(
                [f"a[{i}] * x ^ {i}" for i in range(2, degree + 1)]
            )

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
