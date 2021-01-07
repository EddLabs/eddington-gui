"""Module for the explore window."""
import toga
from eddington import EddingtonException, plot_data
from eddington.plot import add_legend, get_plot_borders
from toga.style import Pack
from travertino.constants import COLUMN

from eddington_gui.boxes.eddington_box import EddingtonBox
from eddington_gui.boxes.figure_box import FigureBox
from eddington_gui.boxes.parameters_options_box import ParametersOptionsBox
from eddington_gui.boxes.plot_configuration_box import PlotConfigurationBox
from eddington_gui.buttons.save_figure_button import SaveFigureButton
from eddington_gui.consts import EXPLORE_WINDOW_SIZE, FontSize


class ExploreWindow(toga.Window):
    """A window class for displaying optional fittings with given parameters."""

    def __init__(self, data, app=None, font_size=FontSize.DEFAULT):
        """Initialize window."""
        super().__init__(size=EXPLORE_WINDOW_SIZE)
        self.app = app
        self.data = data
        window_width = self.size[0]
        self.parameters_options_boxes = EddingtonBox(
            children=[ParametersOptionsBox()], style=Pack(direction=COLUMN)
        )
        self.plot_configuration_box = PlotConfigurationBox(
            plot_method=None, suffix="Explore"
        )
        self.controls_box = EddingtonBox(
            children=[
                self.parameters_options_boxes,
                toga.Box(style=Pack(flex=1)),
                self.plot_configuration_box,
                EddingtonBox(
                    children=[
                        toga.Button("Refresh", on_press=lambda widget: self.draw()),
                        SaveFigureButton("Save", plot_method=self.plot),
                    ]
                ),
            ],
            style=Pack(direction=COLUMN),
        )
        self.figure_box = FigureBox(self.plot, width=int(window_width * 0.5))
        self.content = toga.SplitContainer(content=[self.controls_box, self.figure_box])

        self.controls_box.set_font_size(font_size)
        self.figure_box.set_font_size(font_size)

        self.draw()

    def draw(self):
        """Draw the figure."""
        try:
            self.figure_box.draw()
        except EddingtonException as error:
            self.error_dialog(title="Explore error", message=str(error))

    def plot(self):
        """Plot figure to figure box."""
        kwargs = self.plot_configuration_box.get_plot_kwargs()
        legend = kwargs.pop("legend")
        xmin, xmax = kwargs.pop("xmin"), kwargs.pop("xmax")
        xmin, xmax = get_plot_borders(x=self.data.x, xmin=xmin, xmax=xmax)
        figure = plot_data(self.data, **kwargs)
        ax = figure.get_axes()[0]  # pylint: disable=invalid-name
        step = (xmax - xmin) * 0.001
        for parameters_options_box in self.parameters_options_boxes.children[:-1]:
            parameters_options_box.plot(ax=ax, xmin=xmin, xmax=xmax, step=step)
            legend = legend and len(parameters_options_box.a0_values) != 0
        add_legend(ax, legend)
        return figure

    def update_parameters_options_boxes(self, parameters_box):
        """Update parameters box according to fitting functions selection."""
        if (
            parameters_box.fitting_function is None
            and len(self.parameters_options_boxes.children) > 1  # noqa: W503
        ):
            self.parameters_options_boxes.remove(parameters_box)
        if self.parameters_options_boxes.children[-1].fitting_function is not None:
            self.parameters_options_boxes.add(ParametersOptionsBox())
