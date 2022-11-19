"""Main app."""
import logging
import sys
import webbrowser
from typing import Callable, Dict, Optional

import requests
import toga
from lastversion.lastversion import latest
from packaging.version import parse as parse_version
from toga.style import Pack
from travertino.constants import COLUMN

from eddington_gui import __version__, has_matplotlib
from eddington_gui.app_data import AppData
from eddington_gui.boxes.eddington_box import EddingtonBox
from eddington_gui.boxes.figure_box import FigureBox
from eddington_gui.boxes.main_box import MainBox
from eddington_gui.boxes.plot_configuration_box import PlotConfigurationBox
from eddington_gui.boxes.welcome_box import WelcomeBox
from eddington_gui.buttons.save_figure_button import SaveFigureButton
from eddington_gui.consts import (
    CHART_HEIGHT_SIZE,
    FIGURE_WINDOW_SIZE,
    GITHUB_USER_NAME,
    MAIN_WINDOW_SIZE,
    FontSize,
)
from eddington_gui.logging import LoggerStream, create_logger


class EddingtonGUI(toga.App):  # pylint: disable=too-many-instance-attributes
    """Main app instance."""

    logger: logging.Logger
    welcome_box: WelcomeBox
    main_box: MainBox
    main_window: toga.Window
    plot_boxes: Dict[str, PlotConfigurationBox]
    can_plot_map: Dict[str, Callable[[], bool]]
    app_data: AppData

    __font_size: Optional[FontSize] = None
    __has_newer_version: bool = False

    def startup(self):
        """
        Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        self.app_data = AppData(self.name)
        self.logger = create_logger(
            name="eddington_gui.app", log_file=self.app_data.log_path
        )
        sys.stdout = LoggerStream(self.logger, logging.INFO)
        sys.stderr = LoggerStream(self.logger, logging.ERROR)

        self.main_window = toga.MainWindow(
            title=self.formal_name, size=MAIN_WINDOW_SIZE
        )
        self.on_exit = self.save_style
        self.welcome_box = WelcomeBox(on_start=self.on_start)
        self.main_box = MainBox(on_back=self.on_back)
        self.main_window.content = EddingtonBox(style=Pack(direction=COLUMN))
        self.main_window.content.add(self.welcome_box)

        self.check_latest_version()
        self.commands.add(
            # File group
            toga.Command(
                lambda widget: self.open_latest_version_webpage(),
                label="Install Eddington-GUI latest version",
                group=toga.Group.FILE,
                order=6,
                enabled=self.has_newer_version,
            ),
            toga.Command(
                lambda _: self.set_font_size(FontSize.SMALL),
                "Set small font size",
                group=toga.Group.VIEW,
                order=FontSize.SMALL.value,
            ),
            toga.Command(
                lambda _: self.set_font_size(FontSize.MEDIUM),
                "Set medium font size",
                group=toga.Group.VIEW,
                order=FontSize.MEDIUM.value,
            ),
            toga.Command(
                lambda _: self.set_font_size(FontSize.LARGE),
                "Set large font size",
                group=toga.Group.VIEW,
                order=FontSize.LARGE.value,
            ),
        )
        self.load_style()
        if not has_matplotlib:
            self.main_window.info_dialog(
                "Error",
                (
                    f"Error loading matplotlib.\nPlease go to {self.faq_url}"
                    " and see how to solve this problem"
                ),
            )
            webbrowser.open(self.faq_url)

        self.main_window.show()

        if self.has_newer_version and self.main_window.question_dialog(
            "Update is available",
            (
                f"A new version of {self.formal_name} is available! "
                "would you like to download it?"
            ),
        ):
            self.open_latest_version_webpage()

    @property
    def has_newer_version(self):
        """Get whether Eddington-GUI has a newer version."""
        return self.__has_newer_version

    @has_newer_version.setter
    def has_newer_version(self, has_newer_version):
        """Set whether Eddington-GUI has a newer version."""
        self.__has_newer_version = has_newer_version

    @property
    def latest_version_url(self):
        """Get URL of latest version."""
        return f"https://github.com/{GITHUB_USER_NAME}/{self.app_name}/releases/latest"

    @property
    def faq_url(self):
        """URL for frequently asked questions."""
        return f"https://{self.app_name}.readthedocs.io/en/latest/tutorials/faq.html"

    def on_start(self):
        """Move to main box."""
        self.set_main_window_content(self.main_box)

    def on_back(self):
        """Move to welcome box."""
        self.set_main_window_content(self.welcome_box)

    def save_style(self, app, **kwargs):  # pylint: disable=unused-argument
        """Save style in application data."""
        self.app_data.save_style(font_size=self.__font_size.name)
        return True

    def load_style(self):
        """Load style from app data."""
        style_dict = self.app_data.load_style()
        font_size = style_dict.get("font_size", FontSize.DEFAULT.name)
        self.set_font_size(FontSize[font_size])

    def set_main_window_content(self, box: EddingtonBox):
        """Set the content of the window as the given box."""
        for child_box in self.main_window.content.children:
            self.main_window.content.remove(child_box)
        self.main_window.content.add(box)
        self.update_content_font()

    def set_font_size(self, font_size: FontSize):
        """Set font size to all components in app."""
        self.__font_size = font_size
        self.update_content_font()

    def check_latest_version(self):
        """Checker whether a new version of Eddington-GUI is available or not."""
        try:
            eddington_latest_version = str(latest(self.app_name))
            self.has_newer_version = parse_version(
                eddington_latest_version
            ) > parse_version(__version__)
        except requests.exceptions.ConnectionError:
            self.has_newer_version = False

    def open_latest_version_webpage(self):
        """Open latest version webpage."""
        webbrowser.open(self.latest_version_url)

    def show_nothing_to_plot(self):
        """Show dialog indicating that there is nothing to plot yet."""
        self.main_window.info_dialog(title="Fit Result", message="Nothing to plot yet")

    def show_figure_window(self, on_draw, title):
        """Open a window with matplotlib window."""
        figure_window = toga.Window(title=title, size=FIGURE_WINDOW_SIZE)
        figure_box = FigureBox(on_draw=on_draw, height=CHART_HEIGHT_SIZE)
        figure_box.add(SaveFigureButton("save", on_draw=on_draw))
        figure_window.content = figure_box
        figure_window.app = self.app
        figure_window.content.set_font_size(self.__font_size)
        figure_window.show()

    def update_content_font(self):
        """Update the font of the content widget."""
        self.main_window.content.set_font_size(self.__font_size)
        self.main_window.content.refresh()


def main():
    """Main function."""
    return EddingtonGUI()
