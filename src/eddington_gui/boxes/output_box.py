"""Box for exporting results to files."""
import toga
from toga.style.pack import Pack

from eddington_gui.boxes.line_box import LineBox
from eddington_gui.consts import SMALL_PADDING
from eddington_gui.util import value_or_none


class OutputBox(LineBox):
    """Visual box for choosing output directory."""

    output_directory_input: toga.TextInput

    plot_data_checkbox: toga.Switch
    plot_fitting_checkbox: toga.Switch
    plot_residuals_checkbox: toga.Switch
    result_text_checkbox: toga.Switch
    result_json_checkbox: toga.Switch

    def __init__(self, on_save_output):
        """Initialize box."""
        super().__init__()
        self.output_directory_input = toga.TextInput(style=Pack(flex=1))
        self.add(
            toga.Label(text="Output directory:"),
            self.output_directory_input,
            toga.Button(
                label="Choose directory",
                on_press=self.choose_output_dir,
                style=Pack(padding_left=SMALL_PADDING),
            ),
            toga.Button(
                label="Save",
                on_press=on_save_output,
                style=Pack(padding_left=SMALL_PADDING, padding_right=SMALL_PADDING),
            ),
        )

    @property
    def output_directory(self):
        """Getter of the output directory."""
        return value_or_none(self.output_directory_input.value)

    @output_directory.setter
    def output_directory(self, output_directory):
        """Setter of the output directory."""
        self.output_directory_input.value = output_directory

    @property
    def export_data_plot(self):
        """Should export data plot."""
        return self.plot_data_checkbox.is_on

    @property
    def export_fitting_plot(self):
        """Should export fitting plot."""
        return self.plot_fitting_checkbox.is_on

    @property
    def export_residuals_plot(self):
        """Should export residuals plot."""
        return self.plot_residuals_checkbox.is_on

    @property
    def export_result_as_text(self):
        """Should export result as text."""
        return self.result_text_checkbox.is_on

    @property
    def export_result_as_json(self):
        """Should export result as json."""
        return self.result_json_checkbox.is_on

    def choose_output_dir(self, widget):  # pylint: disable=unused-argument
        """Open output directory choice dialog."""
        try:
            folder_path = self.window.select_folder_dialog(title="Output directory")
        except ValueError:
            return
        self.output_directory = folder_path[0]
