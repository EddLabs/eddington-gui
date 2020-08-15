"""Row box."""
import toga
from toga.style import Pack
from toga.style.pack import ROW, CENTER

from eddington_gui.consts import LINE_HEIGHT, SMALL_PADDING


class LineBox(toga.Box):  # pylint: disable=too-few-public-methods
    """Visual box representing a horizontal row."""

    def __init__(
        self,
        height=LINE_HEIGHT,
        alignment=CENTER,
        padding_left=SMALL_PADDING,
        padding_right=SMALL_PADDING,
        padding_top=SMALL_PADDING,
        padding_bottom=SMALL_PADDING,
        children=None,
    ):  # pylint: disable=too-many-arguments
        """Initialize box."""
        super(LineBox, self).__init__(
            style=Pack(
                direction=ROW,
                height=height,
                alignment=alignment,
                padding_left=padding_left,
                padding_right=padding_right,
                padding_top=padding_top,
                padding_bottom=padding_bottom,
            ),
            children=children,
        )
