"""Constants list."""
from enum import IntEnum

from toga.fonts import SYSTEM_DEFAULT_FONT_SIZE
from toga.style.pack import MONOSPACE

GITHUB_USER_NAME = "EddLabs"

NO_VALUE = "----------"
POLYNOMIAL = "polynomial"

LOGO_SIZE = 192
MAIN_WINDOW_SIZE = (1200, 675)
RECORD_WINDOW_SIZE = (1000, 500)
FIGURE_WINDOW_SIZE = (650, 675)
EXPLORE_WINDOW_SIZE = (1250, 500)

SMALL_PADDING = 2
BIG_PADDING = 5
TITLES_LINE_HEIGHT = 60
COLUMN_WIDTH = 180
LINE_HEIGHT = 30

PARAMETER_WIDTH = 75
LABEL_WIDTH = 150
SELECTION_WIDTH = 200
SMALL_INPUT_WIDTH = 100
LONG_INPUT_WIDTH = 350

FOOTER_FONT_FAMILY = MONOSPACE
SMALL_FONT_SIZE = 10


class FontSize(IntEnum):
    """Font size enum for the Eddington app."""

    SMALL = 1
    MEDIUM = 2
    LARGE = 3
    DEFAULT = 1

    @classmethod
    def get_font_size(cls, font_size: "FontSize"):
        """Get the actual font size from enum value."""
        if font_size == FontSize.SMALL:
            return 10
        if font_size == FontSize.MEDIUM:
            return 12
        if font_size == FontSize.LARGE:
            return 15
        return SYSTEM_DEFAULT_FONT_SIZE

    @classmethod
    def get_button_height(cls, font_size: "FontSize"):
        """Get the height of button, related to font size."""
        if font_size == FontSize.SMALL:
            return 25
        if font_size == FontSize.MEDIUM:
            return 30
        if font_size == FontSize.LARGE:
            return 35
        return None
