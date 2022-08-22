"""Box for choosing a fitting function to use."""
from typing import Callable, Optional

import toga
from eddington import FittingFunction, FittingFunctionsRegistry, polynomial
from toga.style import Pack

from eddington_gui.boxes.line_box import LineBox
from eddington_gui.consts import BIG_PADDING, NO_VALUE, POLYNOMIAL


class FittingFunctionBox(LineBox):  # pylint: disable=too-many-instance-attributes
    """Visual box instance for choosing a fitting function."""

    fitting_function_selection: toga.Selection
    fitting_function_syntax: toga.TextInput
    polynomial_degree_title: toga.Label
    polynomial_degree_input: toga.NumberInput
    load_module_button: toga.Button

    __fitting_function: Optional[FittingFunction]
    __on_fitting_function_load: Optional[Callable[[FittingFunction], None]]
    __polynomial_is_set: bool

    def __init__(self, on_fitting_function_load):
        """Initialize box."""
        super().__init__()
        self.__fitting_function = None
        self.on_fitting_function_load = None
        self.__polynomial_is_set = False

        self.add(toga.Label(text="Fitting function:"))
        self.fitting_function_selection = toga.Selection(
            on_select=self.load_select_fitting_function_name,
        )
        self.fitting_function_syntax = toga.TextInput(
            readonly=True,
            style=Pack(flex=1, padding_left=BIG_PADDING, padding_right=BIG_PADDING),
        )
        self.add(self.fitting_function_selection, self.fitting_function_syntax)

        self.polynomial_degree_title = toga.Label("Degree:")
        self.polynomial_degree_input = toga.NumberInput(
            min_value=1,
            max_value=5,
            value=1,
            on_change=lambda widget: self.set_polynomial_degree(),
        )

        self.update_fitting_function_options()
        self.on_fitting_function_load = on_fitting_function_load

    @property
    def fitting_function(self):
        """Getter of the fitting function."""
        return self.__fitting_function

    @fitting_function.setter
    def fitting_function(self, fitting_function):
        """
        Setter of the fitting function.

        After setting the fit function, run handlers in order to notify other
        components of the change.
        """
        self.__fitting_function = fitting_function
        if self.on_fitting_function_load is not None:
            self.on_fitting_function_load(self.fitting_function)

    @property
    def fitting_function_state(self):
        """Set fit function state."""
        return self.fitting_function_selection.value

    @property
    def on_fitting_function_load(self) -> Optional[Callable]:
        """on_fitting_function_load getter."""
        return self.__on_fitting_function_load

    @on_fitting_function_load.setter
    def on_fitting_function_load(self, on_fitting_function_load):
        """on_fitting_function_load setter."""
        self.__on_fitting_function_load = on_fitting_function_load

    def update_fitting_function_options(self):
        """Update the fitting functions options."""
        self.fitting_function_selection.items = [NO_VALUE, POLYNOMIAL] + list(
            FittingFunctionsRegistry.names()
        )

    def load_select_fitting_function_name(
        self, widget
    ):  # pylint: disable=unused-argument
        """Load the selection fitting function from the FittingFunctionRegistry."""
        if self.fitting_function_state == POLYNOMIAL and not self.__polynomial_is_set:
            self.insert(2, self.polynomial_degree_title)
            self.insert(3, self.polynomial_degree_input)
            self.set_polynomial_degree()
            self.__polynomial_is_set = True
            return
        if self.fitting_function_state != POLYNOMIAL and self.__polynomial_is_set:
            self.remove(self.polynomial_degree_title)
            self.remove(self.polynomial_degree_input)
            self.__polynomial_is_set = False
        if self.fitting_function_state == NO_VALUE:
            self.fitting_function = None
            self.fitting_function_syntax.value = ""
            return
        self.fitting_function = FittingFunctionsRegistry.load(
            self.fitting_function_state
        )
        self.fitting_function_syntax.value = self.fitting_function.syntax

    def set_polynomial_degree(self):
        """Set fitting function to be polynomial based on given degree."""
        degree = int(self.polynomial_degree_input.value)
        self.fitting_function = polynomial(degree)
        if degree == 1:
            self.fitting_function_syntax.value = "a[0] + a[1] * x"
        else:
            self.fitting_function_syntax.value = "a[0] + a[1] * x + " + " + ".join(
                [f"a[{i}] * x ^ {i}" for i in range(2, degree + 1)]
            )
