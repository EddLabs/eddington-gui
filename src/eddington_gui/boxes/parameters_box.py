"""Box for specifying parameters for the fitting algorithm."""
from typing import Callable, List, Optional

import numpy as np
import toga
from eddington import EddingtonException
from toga.style import Pack
from toga.validators import Number

from eddington_gui.boxes.line_box import LineBox
from eddington_gui.consts import SMALL_INPUT_WIDTH, FontSize


class ParametersBox(LineBox):  # pylint: disable=too-many-instance-attributes
    """Visual box for specifying parameters."""

    parameters_labels: List[toga.Label]
    parameters_inputs: List[toga.TextInput]
    __n: Optional[int]
    __a0: Optional[np.ndarray]
    __on_parameters_change: Optional[Callable[[], None]]
    __font_size: Optional[FontSize]

    def __init__(self, on_parameters_change=None, n=0):
        """Initial box."""
        super().__init__()
        self.__n = None
        self.parameters_labels = []
        self.parameters_inputs = []
        self.on_parameters_change = on_parameters_change
        self.n = n  # pylint: disable=invalid-name
        self.a0 = None  # pylint: disable=invalid-name
        self.__font_size = None

    @property
    def n(self):  # pylint: disable=invalid-name
        """Getter of the expected number of parameters."""
        return self.__n

    @n.setter
    def n(self, n):  # pylint: disable=invalid-name
        """Setter of the expected number of parameters."""
        self.reset_initial_guess()
        old_n = 0 if self.__n is None else self.__n
        self.__n = n
        if self.n > len(self.parameters_inputs):
            font_size_value = FontSize.get_font_size(self.__font_size)
            for i in range(len(self.parameters_inputs), self.n):
                self.parameters_labels.append(
                    toga.Label(f"a[{i}]:", style=Pack(font_size=font_size_value))
                )
                self.parameters_inputs.append(
                    toga.TextInput(
                        style=Pack(width=SMALL_INPUT_WIDTH, font_size=font_size_value),
                        on_change=lambda widget: self.reset_initial_guess(),
                        validators=[Number()],
                    )
                )
        if old_n < self.n:
            for i in range(old_n, self.n):
                self.add(self.parameters_labels[i], self.parameters_inputs[i])
        if self.n < old_n:
            for i in range(self.n, old_n):
                self.remove(self.parameters_labels[i], self.parameters_inputs[i])

    @property
    def a0(self):  # pylint: disable=invalid-name
        """Getter of the parameters."""
        if self.__a0 is None:
            self.__calculate_a0()
        return self.__a0

    @a0.setter
    def a0(self, a0):  # pylint: disable=invalid-name
        """
        Setter of the parameters.

        Whenever new parameters are set, run handlers to update dependant components.
        """
        self.__a0 = a0
        if self.on_parameters_change is not None:
            self.on_parameters_change()

    @property
    def on_parameters_change(self):
        """on_parameters_change getter."""
        return self.__on_parameters_change

    @on_parameters_change.setter
    def on_parameters_change(self, on_initial_guess_change):
        """on_parameters_change setter."""
        self.__on_parameters_change = on_initial_guess_change

    def reset_initial_guess(self):
        """Reset the parameters."""
        self.a0 = None  # pylint: disable=invalid-name

    def set_font_size(self, font_size: FontSize):
        super().set_font_size(font_size)
        font_size_value = FontSize.get_font_size(font_size)
        for label in self.parameters_labels:
            label.style.font_size = font_size_value
        for text_input in self.parameters_inputs:
            text_input.style.font_size = font_size_value
        self.__font_size = font_size

    def __calculate_a0(self):
        if self.n is None:
            return
        try:
            a0_values = [self.parameters_inputs[i].value.strip() for i in range(self.n)]
            if all([value == "" for value in a0_values]):
                return
            self.a0 = np.array(list(map(float, a0_values)))
        except ValueError as exc:
            raise EddingtonException(
                "Unable to parse parameters. "
                "Initial guess should be written as floats."
            ) from exc
