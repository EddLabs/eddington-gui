"""Box for specifying initial guess for the fitting algorithm."""
import re
from typing import Callable, List, Union

import numpy as np
import toga
from eddington import EddingtonException
from toga.style import Pack

from eddington_gui.boxes.line_box import LineBox
from eddington_gui.consts import MEDIUM_INPUT_WIDTH


class InitialGuessBox(LineBox):
    """Visual box for specifying initial guess."""

    initial_guess_input: toga.TextInput
    __n: Union[int, None] = None
    __a0: np.ndarray = None
    __handlers: List[Callable] = []

    def __init__(self):
        """Initial box."""
        super().__init__()
        self.add(toga.Label(text="Initial Guess:"))
        self.initial_guess_input = toga.TextInput(
            style=Pack(width=MEDIUM_INPUT_WIDTH),
            on_change=lambda widget: self.reset_initial_guess(),
        )
        self.initial_guess_input.value = None
        self.add(self.initial_guess_input)

    @property
    def n(self):  # pylint: disable=invalid-name
        """Getter of the expected number of parameters."""
        return self.__n

    @n.setter
    def n(self, n):  # pylint: disable=invalid-name
        """Setter of the expected number of parameters."""
        self.__n = n
        self.reset_initial_guess()

    @property
    def a0(self):  # pylint: disable=invalid-name
        """Getter of the initial guess."""
        if self.__a0 is None:
            self.__calculate_a0()
        return self.__a0

    @a0.setter
    def a0(self, a0):  # pylint: disable=invalid-name
        """
        Setter of the initial guess.

        Whenever a new initial guess is set, run handlers to update dependant
        components.
        """
        self.__a0 = a0
        for handler in self.__handlers:
            handler(a0)

    @property
    def initial_guess_string(self):
        """Getter of the initial guess string from the text input."""
        if self.initial_guess_input.value == "":
            return None
        return self.initial_guess_input.value

    def reset_initial_guess(self):
        """Reset the initial guess."""
        self.a0 = None  # pylint: disable=invalid-name

    def add_handler(self, handler):
        """
        Add handler to the handlers list.

        Handlers are running whenever the initial guess has changed.
        """
        self.__handlers.append(handler)

    def __calculate_a0(self):
        if self.initial_guess_string is None:
            self.a0 = None
            return
        a0_values = [
            value.strip() for value in re.split(r",[ \n\t]?", self.initial_guess_string)
        ]
        a0_values = [value for value in a0_values if value != ""]
        try:
            self.a0 = np.array(list(map(float, a0_values)))
        except ValueError as exc:
            raise EddingtonException(
                "Unable to parse initial guess. "
                "Initial guess should be written as numbers divided by commas."
            ) from exc
        if self.n is None:
            return
        number_of_parameters = self.a0.shape[0]
        if number_of_parameters != self.n:
            self.a0 = None
            raise EddingtonException(
                f"Initial guess has {number_of_parameters} parameters, "
                f"but {self.n} were expected."
            )
