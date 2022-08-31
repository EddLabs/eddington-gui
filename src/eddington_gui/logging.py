import io
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from eddington_gui.consts import DEFAULT_BACKUP_COUNT, DEFAULT_MAX_BYTES, ENCODING


def create_logger(
    name: str, level: int = logging.INFO, log_file: Optional[Path] = None
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.level = level
    logger.addHandler(build_stream_handler())
    if log_file is not None:
        logger.addHandler(build_rotating_file_handler(log_file))
        logger.info("Logs are saved in %s", log_file)
    return logger


def build_stream_handler():
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(build_formatter())
    return stream_handler


def build_rotating_file_handler(log_file: Path):
    file_handler = RotatingFileHandler(
        log_file,
        encoding=ENCODING,
        maxBytes=DEFAULT_MAX_BYTES,
        backupCount=DEFAULT_BACKUP_COUNT,
    )
    file_handler.setFormatter(build_formatter())
    return file_handler


def build_formatter():
    return logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")


class LoggerStream:
    def __init__(self, logger: logging.Logger, level: int):
        self.logger = logger
        self.level = level

    def write(self, message):
        if message != "\n":
            self.logger.log(level=self.level, msg=message)

    def flush(self):
        pass
