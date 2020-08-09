import toga
from matplotlib.figure import Figure
from toga_chart import Chart


class FigureWindow(toga.Window):
    def __init__(self, figure: Figure):
        super(FigureWindow, self).__init__(
            size=figure.get_size_inches() * figure.get_dpi()
        )
        chart = Chart()
        self.content = toga.Box(children=[chart])
        chart.draw(figure)
