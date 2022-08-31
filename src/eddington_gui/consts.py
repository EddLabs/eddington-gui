"""Constants list."""
from enum import IntEnum

from toga.fonts import SYSTEM_DEFAULT_FONT_SIZE
from toga.style.pack import MONOSPACE

ENCODING = "utf-8"

DEFAULT_BACKUP_COUNT = 5  # Maximum of 5 backup files
DEFAULT_MAX_BYTES = 1e7  # 10MB

GITHUB_USER_NAME = "EddLabs"

NO_VALUE = "----------"
POLYNOMIAL = "polynomial"

LOGO_SIZE = 300
MAIN_WINDOW_SIZE = (1000, 500)
RECORD_WINDOW_SIZE = (1000, 500)
FIGURE_WINDOW_SIZE = (500, 550)
CHART_HEIGHT_SIZE = 500
EXPLORE_WINDOW_SIZE = (1250, 500)

SMALL_PADDING = 2
BIG_PADDING = 5
TAB_PADDING = 20

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

    def get_font_size(self):
        """Get the actual font size from enum value."""
        if self == FontSize.SMALL:
            return 10
        if self == FontSize.MEDIUM:
            return 12
        if self == FontSize.LARGE:
            return 15
        return SYSTEM_DEFAULT_FONT_SIZE

    def get_button_height(self):
        """Get the height of button, related to font size."""
        if self == FontSize.SMALL:
            return 25
        if self == FontSize.MEDIUM:
            return 30
        if self == FontSize.LARGE:
            return 35
        return None
