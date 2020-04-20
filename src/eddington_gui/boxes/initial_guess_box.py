import re
from typing import Union
import numpy as np
import toga
from eddington_fit import get_a0

from eddington_gui.boxes.line_box import LineBox


class InitialGuessBox(LineBox):
    initial_guess_input: toga.TextInput
    __n: Union[int, None] = None
    __a0: np.ndarray = None
    __handlers = []

    def __init__(self):
        super(InitialGuessBox, self).__init__()
        self.add(toga.Label(text="Initial Guess:"))
        self.initial_guess_input = toga.TextInput(
            on_change=lambda widget: self.reset_initial_guess()
        )
        self.initial_guess_input.value = None
        self.add(self.initial_guess_input)

    @property
    def n(self):
        return self.__n

    @n.setter
    def n(self, n):
        self.__n = n
        self.reset_initial_guess()

    @property
    def a0(self):
        if self.__a0 is None:
            self.__calculate_a0()
        return self.__a0

    @a0.setter
    def a0(self, a0):
        self.__a0 = a0
        for handler in self.__handlers:
            handler(a0)

    @property
    def initial_guess_string(self):
        if self.initial_guess_input.value == "":
            return None
        return self.initial_guess_input.value

    def reset_initial_guess(self):
        self.a0 = None

    def add_handler(self, handler):
        self.__handlers.append(handler)

    def __calculate_a0(self):
        if self.initial_guess_string is not None:
            self.a0 = np.array(
                list(map(float, re.split(r",[ \n\t]+", self.initial_guess_string)))
            )
            return
        if self.n is not None:
            self.a0 = get_a0(self.n)
            return
        self.a0 = None
