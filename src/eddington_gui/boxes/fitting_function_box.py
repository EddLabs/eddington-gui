import toga
from toga.style import Pack

from eddington import FitFunctionsRegistry

from eddington_gui.boxes.line_box import LineBox
from eddington_gui.consts import NO_VALUE, BIG_PADDING


class FittingFunctionBox(LineBox):

    fitting_function_selection: toga.Selection
    fitting_function_syntax: toga.TextInput

    __fit_function = None
    __handlers = []

    def __init__(self):
        super(FittingFunctionBox, self).__init__()
        self.add(toga.Label(text="Fitting function:"))
        self.fitting_function_selection = toga.Selection(
            items=[NO_VALUE] + list(FitFunctionsRegistry.names()),
            on_select=self.load_fit_function,
        )
        self.add(self.fitting_function_selection)
        self.fitting_function_syntax = toga.TextInput(
            readonly=True,
            style=Pack(flex=1, padding_left=BIG_PADDING, padding_right=BIG_PADDING),
        )
        self.add(self.fitting_function_syntax)

    def add_handler(self, handler):
        self.__handlers.append(handler)

    def load_fit_function(self, widget):
        if self.fitting_function_selection.value == NO_VALUE:
            self.fit_function = None
            self.fitting_function_syntax.value = None
        else:
            self.fit_function = FitFunctionsRegistry.load(
                self.fitting_function_selection.value
            )
            self.fitting_function_syntax.value = self.fit_function.syntax
        for handler in self.__handlers:
            handler(self.fit_function)

    @property
    def fit_function(self):
        return self.__fit_function

    @fit_function.setter
    def fit_function(self, fit_function):
        self.__fit_function = fit_function
