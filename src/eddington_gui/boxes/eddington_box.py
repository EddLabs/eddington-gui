"""Eddington extension to the toga's Box widget."""
import toga

from eddington_gui.consts import FontSize


class EddingtonBox(toga.Box):
    """A box widget with extra functionalities."""

    __font_size: FontSize

    def __init__(self, *args, font_size=None, fix_font_size: bool = False, **kwargs):
        """Initialize box."""
        super().__init__(*args, **kwargs)
        self.font_size = font_size
        self.fix_font_size = fix_font_size

    def set_font_size(self, font_size: FontSize):
        """Set font size and refresh."""
        if self.font_size != font_size:
            self.font_size = font_size
            return
        if font_size is None:
            return
        font_size_value = font_size.get_font_size()
        button_height_value = font_size.get_button_height()
        for child in self.children:
            if isinstance(child, EddingtonBox) and not child.fix_font_size:
                child.set_font_size(font_size)
            if isinstance(child, toga.Button):
                child.style.height = button_height_value
            child.style.font_size = font_size_value
        self.refresh()

    @property
    def font_size(self):
        """Return this font size of the box."""
        return self.__font_size

    @font_size.setter
    def font_size(self, font_size):
        self.__font_size = font_size
        self.set_font_size(font_size)
