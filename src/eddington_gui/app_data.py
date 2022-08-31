"""Application data to be saved from different runs."""
import json
import shutil
from pathlib import Path
from typing import Callable, Optional

from platformdirs import user_data_dir, user_log_dir

from eddington_gui.consts import ENCODING


class AppData:
    """Class for keeping application data and logs."""

    def __init__(self, name: str):
        """Constructor."""
        self.name = name

    @property
    def data_dir(self) -> Path:
        """App data directory."""
        data_dir = Path(user_data_dir(appname=self.name))
        data_dir.mkdir(exist_ok=True, parents=True)
        return data_dir

    @property
    def style_data_path(self) -> Path:
        """Path where style is saved."""
        return self.data_dir / "style.json"

    @property
    def log_dir(self) -> Path:
        """Directory where all logs are saved."""
        log_dir = Path(user_log_dir(appname=self.name))
        log_dir.mkdir(exist_ok=True, parents=True)
        return log_dir

    @property
    def log_path(self) -> Path:
        """Rotating path for logs."""
        return self.log_dir / "eddington.log"

    def clear(self, confirmation_function: Optional[Callable[[], None]] = None):
        """Clear app data and all of its content."""
        if confirmation_function is not None and not confirmation_function():
            return
        shutil.rmtree(self.data_dir)

    def save_style(self, **kwargs):
        """Save style to app data."""
        with open(self.style_data_path, mode="w", encoding=ENCODING) as fd:
            json.dump(kwargs, fd, indent=2)

    def load_style(self):
        """Load style from app data."""
        if not self.style_data_path.exists():
            return {}
        with open(self.style_data_path, mode="r", encoding=ENCODING) as fd:
            return json.load(fd)
