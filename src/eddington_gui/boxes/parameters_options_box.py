"""Parameters box for multiple parameters options."""
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
from eddington_gui.consts import FontSize


class ParametersOptionsBox(EddingtonBox):
    """A box for displaying multiple parameters options for a fitting function."""

    def __init__(self, data, draw_method):
        """Initialize box."""
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

    def on_fitting_function_load(self, widget):  # pylint: disable=unused-argument
        """Set function number of parameters to each parameters box."""
        for child in self.parameters_boxes.children:
            child.n = self.n

    def add_parameters(self, widget):  # pylint: disable=unused-argument
        """Add parameters box."""
        parameters_box = ParametersBox()
        parameters_box.n = self.n
        self.parameters_boxes.add(parameters_box)
        parameters_box.font_size = self.font_size
        self.enable_or_disable_remove()

    def remove_parameters(self, widget):  # pylint: disable=unused-argument
        """Remove parameters box."""
        self.parameters_boxes.remove(self.parameters_boxes.children[-1])
        self.enable_or_disable_remove()

    def enable_or_disable_remove(self):
        """Enable or disable the remove parameters button."""
        number_of_parameters_box = len(self.parameters_boxes.children)
        self.remove_parameters_button.enabled = number_of_parameters_box > 1

    def plot(self):
        """Plot all the different parameter options."""
        kwargs = self.plot_configuration_box.get_plot_kwargs()
        legend = kwargs.pop("legend")
        figure = plot_data(self.data, **kwargs)
        ax = figure.get_axes()[0]  # pylint: disable=invalid-name
        xmin, xmax = get_plot_borders(
            x=self.data.x,
            xmin=self.plot_configuration_box.xmin,
            xmax=self.plot_configuration_box.xmax,
        )
        step = (xmax - xmin) * 0.001
        x = np.arange(xmin, xmax, step=step)  # pylint: disable=invalid-name
        fitting_function = self.fitting_function_box.fitting_function
        if fitting_function is None:
            return figure
        for parameters_box in self.parameters_boxes.children:
            a0 = parameters_box.a0  # pylint: disable=invalid-name
            if a0 is not None:
                label = ", ".join(f"a[{i}]={val}" for i, val in enumerate(a0))
                add_plot(ax, x, fitting_function(a0, x), label=label)
        if len(self.parameters_boxes.children) > 0:
            add_legend(ax, legend)
        return figure

    @property
    def n(self):  # pylint: disable=invalid-name
        """Get the number of parameters from the fitting function box."""
        fitting_function = self.fitting_function_box.fitting_function
        return 0 if fitting_function is None else fitting_function.n
