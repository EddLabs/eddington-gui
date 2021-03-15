"""Button for plotting in a designated window."""

import toga
from eddington import EddingtonException


class PlotButton(toga.Button):
    """Plot button."""

    def __init__(  # pylint: disable=too-many-arguments
        self, label: str, can_plot, plot_method, plot_title: str, app: toga.App = None
    ):
        """
        Initialize button.

        :param label: Label of the button
        :type label: str
        :param can_plot: method for checking whether can plot or not
        :param plot_method: Method for creating the plot figure
        :param plot_title: Title of the figure
        :type plot_title: str
        :param app: Toga app reference
        :type app: toga.App
        """
        super().__init__(label=label, on_press=lambda widget: self.plot())
        self.app = app
        self.can_plot = can_plot
        self.plot_title = plot_title
        self.plot_method = plot_method

    def plot(self):
        """Run when plot button is pressed."""
        if not self.can_plot():
            self.app.show_nothing_to_plot()
            return
        try:
            self.app.show_figure_window(
                plot_method=self.plot_method, title=self.plot_title
            )
        except EddingtonException as error:
            self.window.error_dialog(title="Plot error", message=str(error))
