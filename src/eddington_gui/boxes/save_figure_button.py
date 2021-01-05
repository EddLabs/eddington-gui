from pathlib import Path

import toga


class SaveFigureButton(toga.Button):
    def __init__(self, label, plot_method):
        super().__init__(label=label, on_press=lambda widget: self.save_figure())
        self.plot_method = plot_method

    def save_figure(self):  # pylint: disable=unused-argument
        """Save file dialog."""
        try:
            output_path = Path(
                self.window.save_file_dialog(
                    title="Save Figure",
                    suggested_filename="fig",
                    file_types=["png", "jpg", "pdf"],
                )
            )
        except ValueError:
            return

        suffix = output_path.suffix
        if suffix in [".png", ".jpg", ".pdf"]:
            with self.plot_method() as figure:
                figure.savefig(fname=output_path)
        else:
            self.window.error_dialog(
                title="Invalid File Suffix",
                message=f"Cannot save figure with suffix {suffix} . \n"
                f"allowed formats: png, jpg, pdf.",
            )
