import numpy as np
import toga
from eddington import get_figure, errorbar, add_plot, EddingtonException
from toga.style import Pack
from travertino.constants import COLUMN

from eddington_gui.boxes.eddington_box import EddingtonBox
from eddington_gui.boxes.fitting_function_box import FittingFunctionBox
from eddington_gui.boxes.parameters_box import ParametersBox
from eddington_gui.boxes.save_figure_button import SaveFigureButton


class ParametersOptionsBox(EddingtonBox):

    def __init__(self, data, draw_method):
        super().__init__(style=Pack(direction=COLUMN))
        self.data = data
        self.min_x, self.max_x = np.min(data.x), np.max(data.x)

        self.fitting_function_box = FittingFunctionBox(
            on_fitting_function_load=self.on_fitting_function_load
        )
        self.add(self.fitting_function_box)

        self.parameters_boxes = EddingtonBox(
            children=[ParametersBox()],
            style=Pack(direction=COLUMN, padding_left=20)
        )
        self.add(self.parameters_boxes)

        self.add_parameters_button = toga.Button("+", on_press=self.add_parameters)
        self.remove_parameters_button = toga.Button(
            "-", on_press=self.remove_parameters, enabled=False
        )
        self.add(
            EddingtonBox(
                children=[self.add_parameters_button, self.remove_parameters_button]
            )
        )

        self.add(toga.Box(style=Pack(flex=1)))
        self.add(
            EddingtonBox(
                children=[
                    toga.Button("Refresh", on_press=lambda widget: draw_method()),
                    SaveFigureButton("Save", plot_method=self.plot)
                ]
            )
        )

    def on_fitting_function_load(self, _):
        for child in self.parameters_boxes.children:
            child.n = self.n

    def add_parameters(self, widget):
        parameters_box = ParametersBox()
        parameters_box.n = self.n
        self.parameters_boxes.add(parameters_box)
        self.enable_or_disable_remove()

    def remove_parameters(self, widget):
        self.parameters_boxes.remove(self.parameters_boxes.children[-1])
        self.enable_or_disable_remove()

    def enable_or_disable_remove(self):
        number_of_parameters_box = len(self.parameters_boxes.children)
        self.remove_parameters_button.enabled = number_of_parameters_box > 1

    def plot(self):
        ax, figure = get_figure("Explore")
        errorbar(ax, self.data)
        step = (self.max_x - self.min_x) * 0.001
        x = np.arange(self.min_x, self.max_x, step=step)
        fitting_function = self.fitting_function_box.fitting_function
        if fitting_function is None:
            return figure
        for parameters_box in self.parameters_boxes.children:
            if parameters_box.a0 is not None:
                add_plot(ax, x, fitting_function(parameters_box.a0, x))
        return figure

    @property
    def n(self):
        fitting_function = self.fitting_function_box.fitting_function
        return 0 if fitting_function is None else fitting_function.n
