"""Window that presents matplotlib figures."""
from pathlib import Path

import toga
from matplotlib.figure import Figure
from toga.style import Pack
from toga.style.pack import COLUMN
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
        super().__init__(size=(1, 1.05) * (figure.get_size_inches() * figure.get_dpi()))
        chart = Chart()

        save_button = toga.Button(label="Save", on_press=self.save_figure)
        save_box = toga.Box(children=[save_button])
        chart_box = toga.Box(
            children=[chart],
            style=Pack(height=(figure.get_size_inches() * figure.get_dpi())[1]),
        )
        main_box = toga.Box(
            children=[chart_box, save_box], style=Pack(direction=COLUMN)
        )
        self.content = main_box
        chart.draw(figure)

    def save_figure(self, widget):  # pylint: disable=unused-argument
        """Save file dialog."""
        try:
            output_path = Path(
                self.save_file_dialog(
                    title="Save Figure",
                    suggested_filename="fig",
                    file_types=["png", "jpg", "pdf"],
                )
            )
        except ValueError:
            return

        suffix = output_path.suffix
        if suffix in [".png", ".jpg", ".pdf"]:
            self.figure.savefig(fname=output_path)
        else:
            self.error_dialog(
                title="Invalid File Suffix",
                message=f"Cannot save figure with suffix {suffix} . \n"
                f"allowed formats: png, jpg, pdf.",
            )
