"""Box for specifying initial guess for the fitting algorithm."""
from typing import Callable, List, Optional

import numpy as np
import toga
from eddington import EddingtonException
from toga.style import Pack

from eddington_gui.boxes.line_box import LineBox
from eddington_gui.consts import SMALL_INPUT_WIDTH


class InitialGuessBox(LineBox):
    """Visual box for specifying initial guess."""

    main_label: toga.Label
    initial_guess_labels: List[toga.Label] = []
    initial_guess_inputs: List[toga.TextInput] = []
    __n: Optional[int] = None
    __n_in_use: int = 0
    __a0: Optional[np.ndarray] = None
    __on_initial_guess_change: Optional[Callable[[], None]] = None

    def __init__(self, on_initial_guess_change):
        """Initial box."""
        super().__init__()
        self.on_initial_guess_change = on_initial_guess_change
        self.main_label = toga.Label(text="Initial Guess:")
        self.add(self.main_label)
        self.reset_box()

    @property
    def n(self):  # pylint: disable=invalid-name
        """Getter of the expected number of parameters."""
        return self.__n

    @n.setter
    def n(self, n):  # pylint: disable=invalid-name
        """Setter of the expected number of parameters."""
        self.__n = n
        self.reset_initial_guess()
        self.reset_box()

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
        if self.on_initial_guess_change is not None:
            self.on_initial_guess_change()

    @property
    def on_initial_guess_change(self):
        """on_initial_guess_change getter."""
        return self.__on_initial_guess_change

    @on_initial_guess_change.setter
    def on_initial_guess_change(self, on_initial_guess_change):
        """on_initial_guess_change setter."""
        self.__on_initial_guess_change = on_initial_guess_change

    def reset_box(self):
        """Reset initial guess box based on ``n`` value."""
        if self.n is None:
            return
        if self.n > len(self.initial_guess_inputs):
            for i in range(len(self.initial_guess_inputs), self.n):
                self.initial_guess_labels.append(toga.Label(f"a[{i}]:"))
                self.initial_guess_inputs.append(
                    toga.TextInput(
                        style=Pack(width=SMALL_INPUT_WIDTH),
                        on_change=lambda widget: self.reset_initial_guess(),
                    )
                )
        if self.__n_in_use < self.n:
            for i in range(self.__n_in_use, self.n):
                self.add(self.initial_guess_labels[i], self.initial_guess_inputs[i])
        if self.n < self.__n_in_use:
            for i in range(self.n, self.__n_in_use):
                self.remove(self.initial_guess_labels[i], self.initial_guess_inputs[i])
        self.__n_in_use = self.n

    def reset_initial_guess(self):
        """Reset the initial guess."""
        self.a0 = None  # pylint: disable=invalid-name

    def __calculate_a0(self):
        if self.n is None:
            return
        try:
            a0_values = [
                self.initial_guess_inputs[i].value.strip() for i in range(self.n)
            ]
            if all([value == "" for value in a0_values]):
                return
            self.a0 = np.array(list(map(float, a0_values)))
        except ValueError as exc:
            raise EddingtonException(
                "Unable to parse initial guess. "
                "Initial guess should be written as floats."
            ) from exc
