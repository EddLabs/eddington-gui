"""Box for exporting results to files."""
import toga
from toga.style import Pack

from eddington_gui.boxes.line_box import LineBox
from eddington_gui.consts import MAIN_BOTTOM_PADDING, SMALL_PADDING
from eddington_gui.util import value_or_none


class OutputBox(LineBox):
    """Visual box for choosing output directory."""

    output_directory_input: toga.TextInput

    def __init__(self, on_save_output):
        """Initialize box."""
        super().__init__(padding_bottom=MAIN_BOTTOM_PADDING)
        self.output_directory_input = toga.TextInput(style=Pack(flex=1))
        self.add(toga.Label(text="Output directory:"))
        self.add(self.output_directory_input)
        self.add(
            toga.Button(
                label="Choose directory",
                on_press=self.choose_output_dir,
                style=Pack(padding_left=SMALL_PADDING),
            )
        )
        self.add(
            toga.Button(
                label="Save",
                on_press=on_save_output,
                style=Pack(padding_left=SMALL_PADDING, padding_right=SMALL_PADDING),
            )
        )

    @property
    def output_directory(self):
        """Getter of the output directory."""
        return value_or_none(self.output_directory_input.value)

    @output_directory.setter
    def output_directory(self, output_directory):
        """Setter of the output directory."""
        self.output_directory_input.value = output_directory

    def choose_output_dir(self, widget):  # pylint: disable=unused-argument
        """Open output directory choice dialog."""
        try:
            folder_path = self.window.select_folder_dialog(title="Output directory")
        except ValueError:
            return
        self.output_directory = folder_path[0]
