"""Parameters box for multiple parameters options."""
import numpy as np
import toga
from eddington import add_plot
from toga.style import Pack
from travertino.constants import BOLD, COLUMN

from eddington_gui.boxes.eddington_box import EddingtonBox
from eddington_gui.boxes.fitting_function_box import FittingFunctionBox
from eddington_gui.boxes.parameters_box import ParametersBox
from eddington_gui.consts import SMALL_INPUT_WIDTH, SMALL_PADDING, TAB_PADDING


class ParametersOptionsBox(EddingtonBox):
    """A box for displaying multiple parameters options for a fitting function."""

    def __init__(self, **kwargs):
        """Initialize box."""
        super().__init__(**kwargs, style=Pack(direction=COLUMN))

        self.fitting_function_box = FittingFunctionBox(
            on_fitting_function_load=(
                lambda widget: self.window.update_parameters_options_boxes(self)
            )
        )
        self.add(self.fitting_function_box)

        self.parameters_boxes = EddingtonBox(
            children=[self.build_parameters_box()],
            style=Pack(direction=COLUMN, padding_left=TAB_PADDING),
        )
        self.add(self.parameters_boxes)

        self.add_parameters_button = toga.Button(
            "+", on_press=lambda widget: self.add_parameters(), enabled=False
        )
        self.remove_parameters_button = toga.Button(
            "-", on_press=lambda widget: self.remove_parameters(), enabled=False
        )
        self.add(
            EddingtonBox(
                children=[self.add_parameters_button, self.remove_parameters_button],
                style=Pack(padding_left=TAB_PADDING),
            )
        )

    def add_parameters(self):
        """Add parameters box."""
        self.parameters_boxes.add(self.build_parameters_box())
        self.enable_or_disable_buttons()
        self.set_font_size(self.font_size)

    def build_parameters_box(self):
        """Build a new parameters box."""
        parameters_box = ParametersBox()
        parameters_box.n = self.n
        parameters_box.insert(
            0,
            toga.Label(
                "Label",
                style=Pack(padding_left=SMALL_PADDING, font_weight=BOLD),
            ),
        )
        parameters_box.insert(
            1,
            toga.TextInput(
                style=Pack(width=SMALL_INPUT_WIDTH, padding_left=SMALL_PADDING)
            ),
        )
        return parameters_box

    def remove_parameters(self):
        """Remove parameters box."""
        self.parameters_boxes.remove(self.parameters_boxes.children[-1])
        self.enable_or_disable_buttons()
        self.set_font_size(self.font_size)

    def enable_or_disable_buttons(self):
        """Enable or disable the remove parameters button."""
        number_of_parameters_box = len(self.parameters_boxes.children)
        self.remove_parameters_button.enabled = number_of_parameters_box > 1
        self.add_parameters_button.enabled = self.fitting_function is not None

    def plot(self, ax, xmin, xmax, step):  # pylint: disable=invalid-name
        """Plot all the different parameter options."""
        x = np.arange(xmin, xmax, step=step)  # pylint: disable=invalid-name
        a0_values = self.a0_values
        if len(a0_values) == 0:
            return
        for label, a0 in a0_values:  # pylint: disable=invalid-name
            if label == "":
                label = ", ".join(f"a[{i}]={val}" for i, val in enumerate(a0))
            add_plot(
                ax,
                x,
                self.fitting_function(a0, x),  # pylint: disable=not-callable
                label=label,
            )

    @property
    def n(self):  # pylint: disable=invalid-name
        """Get the number of parameters from the fitting function box."""
        return 0 if self.fitting_function is None else self.fitting_function.n

    @n.setter
    def n(self, n):  # pylint: disable=invalid-name
        for child in self.parameters_boxes.children:
            child.n = n
        if n == 0:
            while len(self.parameters_boxes.children) > 1:
                self.remove_parameters()
        self.enable_or_disable_buttons()

    @property
    def a0_values(self):
        """Get a0 values from parameters boxes."""
        parameters_boxes = [
            parameters_box
            for parameters_box in self.parameters_boxes.children
            if parameters_box.a0 is not None
        ]
        a0_values = [
            (parameters_box.children[1].value.strip(), parameters_box.a0)
            for parameters_box in parameters_boxes
        ]
        return a0_values

    @property
    def fitting_function(self):
        """Get the fitting function."""
        return self.fitting_function_box.fitting_function
