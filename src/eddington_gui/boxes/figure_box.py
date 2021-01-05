from pathlib import Path
from typing import Callable

import toga
from matplotlib.figure import Figure
from toga.style import Pack
from toga_chart import Chart
from travertino.constants import COLUMN

from eddington_gui.boxes.eddington_box import EddingtonBox


class FigureBox(EddingtonBox):
    def __init__(self, plot_method: Callable[[], Figure], height=0, width=0):
        """Initialize box."""
        super().__init__(style=Pack(direction=COLUMN, height=height, width=width))
        self.plot_method = plot_method
        self.chart = Chart()
        self.add(self.chart)

    def draw(self):
        with self.plot_method() as figure:
            self.chart.style.height = (figure.get_size_inches() * figure.get_dpi())[1]
            self.chart.draw(figure)

