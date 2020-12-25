"""Constants list."""
from enum import Enum

from toga.style.pack import MONOSPACE

NO_VALUE = "----------"
POLYNOMIAL = "polynomial"

LOGO_SIZE = 192
WINDOW_SIZE = (1200, 670)

SMALL_PADDING = 2
BIG_PADDING = 5
RECORD_WINDOW_SIZE = (1000, 500)
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


class FontSize(Enum):

    SMALL = 1
    MEDIUM = 2
    LARGE = 3
    DEFAULT = 1

    @classmethod
    def get_font_size(cls, font_size: "FontSize"):
        if font_size == FontSize.SMALL:
            return 10
        if font_size == FontSize.MEDIUM:
            return 12
        if font_size == FontSize.LARGE:
            return 15
        return None

    @classmethod
    def get_button_height(cls, font_size: "FontSize"):
        if font_size == FontSize.SMALL:
            return 25
        if font_size == FontSize.MEDIUM:
            return 30
        if font_size == FontSize.LARGE:
            return 35
        return None

    @classmethod
    def get_line_height(cls, font_size: "FontSize"):
        return LINE_HEIGHT

    def __lt__(self, other):
        return self.value < other.value
