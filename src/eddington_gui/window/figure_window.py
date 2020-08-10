"""Window that presents matplotlib figures."""
import toga
from matplotlib.figure import Figure
from toga_chart import Chart


class FigureWindow(toga.Window):
    """
    Window that contains a chart with a *matplotlib* figure.

    This is made using toga.Chart widget.
    """

    def __init__(self, figure: Figure):
        """Initialize window."""
        super(FigureWindow, self).__init__(
            size=figure.get_size_inches() * figure.get_dpi()
        )
        chart = Chart()
        self.content = toga.Box(children=[chart])
        chart.draw(figure)
