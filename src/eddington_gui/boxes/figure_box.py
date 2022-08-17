"""A box displaying a figure."""
from eddington.plot.figure import Figure
from toga.style import Pack
from toga_chart import Chart
from travertino.constants import COLUMN

from eddington_gui.boxes.eddington_box import EddingtonBox


class FigureBox(EddingtonBox):
    """A box widget for displaying matplotlib figures."""

    def __init__(self, on_draw, height=0, width=0):
        """Initialize box."""
        super().__init__(style=Pack(direction=COLUMN, height=height, width=width))
        self.chart = Chart(on_draw=on_draw)
        self.add(self.chart)

    def draw(self):
        with Figure() as figure:
            self.chart.draw(figure)
