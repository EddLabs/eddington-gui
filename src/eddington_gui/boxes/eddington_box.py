"""Eddington extension to the toga's Box widget."""
import toga

from eddington_gui.consts import FontSize


class EddingtonBox(toga.Box):
    """A box widget with extra functionalities."""

    def set_font_size(self, font_size: FontSize):
        """Set font size and refresh."""
        font_size_value = FontSize.get_font_size(font_size)
        button_height_value = FontSize.get_button_height(font_size)
        for child in self.children:
            if isinstance(child, EddingtonBox):
                child.set_font_size(font_size)
            if isinstance(child, toga.Button):
                child.style.height = button_height_value
            child.style.font_size = font_size_value
        self.refresh()
