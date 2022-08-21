"""Button for plotting in a designated window."""

import toga
from eddington import EddingtonException


class PlotButton(toga.Button):
    """Plot button."""

    def __init__(  # pylint: disable=too-many-arguments
        self, label, can_plot, on_draw, plot_title, app=None
    ):
        """Initialize button."""
        super().__init__(label=label, on_press=lambda widget: self.plot())
        self.app = app
        self.can_plot = can_plot
        self.plot_title = plot_title
        self.on_draw = on_draw

    def plot(self):
        """Run when plot button is pressed."""
        if not self.can_plot():
            self.app.show_nothing_to_plot()
            return
        try:
            self.app.show_figure_window(on_draw=self.on_draw, title=self.plot_title)
        except EddingtonException as error:
            self.window.error_dialog(title="Plot error", message=str(error))
