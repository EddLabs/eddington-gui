"""Module for the explore window."""
import toga
from eddington import FigureBuilder
from eddington.interval import Interval
from toga.style import Pack
from travertino.constants import COLUMN

from eddington_gui.boxes.eddington_box import EddingtonBox
from eddington_gui.boxes.figure_box import FigureBox
from eddington_gui.boxes.parameters_options_box import ParametersOptionsBox
from eddington_gui.boxes.plot_configuration_box import PlotConfigurationBox
from eddington_gui.buttons.save_figure_button import SaveFigureButton
from eddington_gui.consts import EXPLORE_WINDOW_SIZE, FontSize


class ExploreWindow(toga.Window):  # pylint: disable=too-many-instance-attributes
    """A window class for displaying optional fittings with given parameters."""

    def __init__(self, data, app=None, font_size=FontSize.DEFAULT):
        """Initialize window."""
        super().__init__(size=EXPLORE_WINDOW_SIZE)
        self.app = app
        self.data = data
        self.font_size = font_size
        window_width = self.size[0]
        self.parameters_options_boxes = EddingtonBox(
            children=[self.build_parameters_options_box()], style=Pack(direction=COLUMN)
        )
        self.plot_configuration_box = PlotConfigurationBox(
            additional_instructions=self.additional_plot_instructions, suffix="Explore"
        )
        self.figure_box = FigureBox(
            on_draw=self.plot_configuration_box.on_draw, width=int(window_width * 0.5)
        )
        self.controls_box = EddingtonBox(
            children=[
                self.parameters_options_boxes,
                toga.Box(style=Pack(flex=1)),
                self.plot_configuration_box,
                EddingtonBox(
                    children=[
                        toga.Button("Refresh", on_press=self.refresh),
                        SaveFigureButton(
                            "Save", on_draw=self.plot_configuration_box.on_draw
                        ),
                    ]
                ),
            ],
            style=Pack(direction=COLUMN),
        )
        self.content = toga.SplitContainer(content=[self.controls_box, self.figure_box])

        self.update_font_size()

    def update_font_size(self):
        """Update font size of the window components."""
        self.controls_box.set_font_size(self.font_size)
        self.figure_box.set_font_size(self.font_size)

    def update_parameters_options_boxes(self, parameters_box):
        """Update parameters box according to fitting functions selection."""
        if (
            parameters_box.fitting_function is None
            and len(self.parameters_options_boxes.children) > 1  # noqa: W503
        ):
            self.parameters_options_boxes.remove(parameters_box)
        else:
            parameters_box.n = (
                0
                if parameters_box.fitting_function is None
                else parameters_box.fitting_function.n
            )
        if self.parameters_options_boxes.children[-1].fitting_function is not None:
            self.parameters_options_boxes.add(self.build_parameters_options_box())
            self.update_font_size()

    def additional_plot_instructions(
        self, figure_builder: FigureBuilder, interval: Interval
    ):
        figure_builder.add_data(data=self.data, label="Data")
        plot_added = False
        for parameters_options_box in self.parameters_options_boxes.children[:-1]:
            for label, a0 in parameters_options_box.a0_values:
                plot_added = True
                figure_builder.add_plot(
                    interval=interval.intersect(self.data.x_domain),
                    a=a0,
                    func=parameters_options_box.fitting_function,
                    label=label,
                )
        if plot_added:
            figure_builder.add_legend()

    def refresh(self, widget):
        self.figure_box.draw()

    @classmethod
    def build_parameters_options_box(cls):
        """Build new options box."""
        return ParametersOptionsBox()
