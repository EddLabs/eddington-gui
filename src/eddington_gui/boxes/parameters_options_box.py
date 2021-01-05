import numpy as np
import toga
from eddington import add_legend, add_plot, plot_data
from eddington.plot import get_plot_borders
from toga.style import Pack
from travertino.constants import COLUMN

from eddington_gui.boxes.eddington_box import EddingtonBox
from eddington_gui.boxes.fitting_function_box import FittingFunctionBox
from eddington_gui.boxes.parameters_box import ParametersBox
from eddington_gui.boxes.plot_configuration_box import PlotConfigurationBox
from eddington_gui.buttons.save_figure_button import SaveFigureButton


class ParametersOptionsBox(EddingtonBox):
    def __init__(self, data, draw_method):
        super().__init__(style=Pack(direction=COLUMN))
        self.data = data

        self.fitting_function_box = FittingFunctionBox(
            on_fitting_function_load=self.on_fitting_function_load
        )
        self.add(self.fitting_function_box)

        self.parameters_boxes = EddingtonBox(
            children=[ParametersBox()], style=Pack(direction=COLUMN, padding_left=20)
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

        self.add(
            toga.Box(style=Pack(flex=1)),
        )

        self.plot_configuration_box = PlotConfigurationBox(
            plot_method=None, suffix="Explore"
        )
        self.add(
            self.plot_configuration_box,
            EddingtonBox(
                children=[
                    toga.Button("Refresh", on_press=lambda widget: draw_method()),
                    SaveFigureButton("Save", plot_method=self.plot),
                ]
            ),
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
        kwargs = self.plot_configuration_box.get_plot_kwargs()
        legend = kwargs.pop("legend")
        figure = plot_data(self.data, **kwargs)
        ax = figure.get_axes()[0]
        xmin, xmax = get_plot_borders(
            x=self.data.x,
            xmin=self.plot_configuration_box.xmin,
            xmax=self.plot_configuration_box.xmax,
        )
        step = (xmax - xmin) * 0.001
        x = np.arange(xmin, xmax, step=step)
        fitting_function = self.fitting_function_box.fitting_function
        if fitting_function is None:
            return figure
        for parameters_box in self.parameters_boxes.children:
            a0 = parameters_box.a0
            if a0 is not None:
                label = ", ".join(f"a[{i}]={val}" for i, val in enumerate(a0))
                add_plot(ax, x, fitting_function(a0, x), label=label)
        if len(self.parameters_boxes.children) > 0:
            add_legend(ax, legend)
        return figure

    @property
    def n(self):
        fitting_function = self.fitting_function_box.fitting_function
        return 0 if fitting_function is None else fitting_function.n
