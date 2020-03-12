import toga
from toga.style import Pack
from toga.style.pack import ROW

from eddington import FitFunctionsRegistry
from eddington_gui.consts import NO_VALUE


class FittingFunctionBox(toga.Box):

    fitting_function_selection: toga.Selection
    fitting_function_syntax: toga.TextInput

    __fit_function = None
    __handlers = []

    def __init__(self):
        super(FittingFunctionBox, self).__init__(style=Pack(direction=ROW))
        self.add(toga.Label(text="Fitting function:"))
        self.fitting_function_selection = toga.Selection(items=[NO_VALUE] + list(FitFunctionsRegistry.names()),
                                                         on_select=self.load_fit_function)
        self.add(self.fitting_function_selection)
        self.fitting_function_syntax = toga.TextInput(readonly=True,
                                                      style=Pack(padding_left=5, padding_right=5, flex=1))
        self.add(self.fitting_function_syntax)

    def add_handler(self, handler):
        self.__handlers.append(handler)

    def load_fit_function(self, widget):
        if self.fitting_function_selection.value == NO_VALUE:
            self.fit_function = None
            self.fitting_function_syntax.value = None
        else:
            self.fit_function = FitFunctionsRegistry.load(self.fitting_function_selection.value)
            self.fitting_function_syntax.value = self.fit_function.syntax
        for handler in self.__handlers:
            handler()

    @property
    def fit_function(self):
        return self.__fit_function

    @fit_function.setter
    def fit_function(self, fit_function):
        self.__fit_function = fit_function
