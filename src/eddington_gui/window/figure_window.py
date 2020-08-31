"""Window that presents matplotlib figures."""
from pathlib import Path

import toga
from matplotlib.figure import Figure
from toga.style import Pack
from toga.style.pack import ROW
from toga_chart import Chart


class FigureWindow(toga.Window):  # pylint: disable=too-few-public-methods
    """
    Window that contains a chart with a *matplotlib* figure.

    This is made using toga.Chart widget.
    """

    figure: Figure

    def __init__(self, figure: Figure):
        """Initialize window."""
        self.figure = figure
        super().__init__(size=(1.1, 1) * (figure.get_size_inches() * figure.get_dpi()))
        chart = Chart()
        save_button = toga.Button(
            label="Save", style=Pack(flex=1), on_press=self.save_figure
        )
        self.content = toga.Box(
            children=[save_button, chart], style=Pack(direction=ROW)
        )
        chart.draw(figure)

    def save_figure(self, widget):  # pylint: disable=unused-argument
        """Save file dialog."""
        try:
            output_path = Path(
                self.save_file_dialog(
                    title="Save Figure", suggested_filename="fig", file_types=["png"]
                )
            )
        except ValueError:
            return

        self.figure.savefig(fname=output_path.with_suffix(".png"), format="png")
