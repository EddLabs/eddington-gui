"""Module for the explore window."""
import toga
from eddington import EddingtonException

from eddington_gui.boxes.figure_box import FigureBox
from eddington_gui.boxes.parameters_options_box import ParametersOptionsBox
from eddington_gui.consts import EXPLORE_WINDOW_SIZE, FontSize


class ExploreWindow(toga.Window):
    """A window class for displaying optional fittings with given parameters."""

    def __init__(self, data, app=None, font_size=FontSize.DEFAULT):
        """Initialize window."""
        super().__init__(size=EXPLORE_WINDOW_SIZE)
        self.app = app
        window_width = self.size[0]
        self.controls_box = ParametersOptionsBox(data=data, draw_method=self.draw)
        self.figure_box = FigureBox(
            self.controls_box.plot, width=int(window_width * 0.5)
        )
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
