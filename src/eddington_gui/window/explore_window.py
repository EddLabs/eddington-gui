import numpy as np
import toga
from eddington import EddingtonException, add_plot, errorbar, get_figure
from toga.style import Pack
from travertino.constants import COLUMN

from eddington_gui.boxes.figure_box import FigureBox
from eddington_gui.boxes.fitting_function_box import FittingFunctionBox
from eddington_gui.boxes.parameters_box import ParametersBox
from eddington_gui.boxes.parameters_options_box import ParametersOptionsBox
from eddington_gui.consts import EXPLORE_WINDOW_SIZE


class ExploreWindow(toga.Window):
    def __init__(self, data, app):
        super().__init__(size=EXPLORE_WINDOW_SIZE)
        self.app = app
        window_width = self.size[0]
        self.controls_box = ParametersOptionsBox(data=data, draw_method=self.draw)
        self.figure_box = FigureBox(
            self.controls_box.plot, width=int(window_width * 0.5)
        )
        self.content = toga.SplitContainer(content=[self.controls_box, self.figure_box])
        self.draw()

    def draw(self):
        try:
            self.figure_box.draw()
        except EddingtonException as error:
            self.error_dialog(title="Explore error", message=str(error))
