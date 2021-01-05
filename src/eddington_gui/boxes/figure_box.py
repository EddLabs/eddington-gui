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
        save_button = toga.Button(label="Save", on_press=self.save_figure)
        self.add(self.chart, save_button)

    def draw(self):
        with self.plot_method() as figure:
            self.chart.style.height = (figure.get_size_inches() * figure.get_dpi())[1]
            self.chart.draw(figure)

    def save_figure(self, widget):  # pylint: disable=unused-argument
        """Save file dialog."""
        try:
            output_path = Path(
                self.window.save_file_dialog(
                    title="Save Figure",
                    suggested_filename="fig",
                    file_types=["png", "jpg", "pdf"],
                )
            )
        except ValueError:
            return

        suffix = output_path.suffix
        if suffix in [".png", ".jpg", ".pdf"]:
            with self.plot_method() as figure:
                figure.savefig(fname=output_path)
        else:
            self.window.error_dialog(
                title="Invalid File Suffix",
                message=f"Cannot save figure with suffix {suffix} . \n"
                f"allowed formats: png, jpg, pdf.",
            )