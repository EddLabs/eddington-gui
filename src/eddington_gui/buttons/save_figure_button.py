"""Button for saving figures."""
from pathlib import Path

import toga
from eddington.plot.figure import Figure


class SaveFigureButton(toga.Button):
    """Button for saving matplotlib figures to file."""

    def __init__(self, label, on_draw):
        """Initialize button."""
        super().__init__(label=label, on_press=self.save_figure)
        self.on_draw = on_draw

    async def save_figure(self, widget):
        """Save file dialog."""
        output_path = await self.window.save_file_dialog(
            title="Save Figure",
            suggested_filename="fig",
            file_types=["png", "jpg", "pdf"],
        )
        if output_path is None:
            return

        suffix = output_path.suffix
        if suffix in [".png", ".jpg", ".pdf"]:
            with Figure() as figure:
                self.on_draw(self, figure)
                figure.savefig(fname=output_path)
        else:
            self.window.error_dialog(
                title="Invalid File Suffix",
                message=f"Cannot save figure with suffix {suffix} . \n"
                f"allowed formats: png, jpg, pdf.",
            )
