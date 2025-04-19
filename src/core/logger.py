from datetime import datetime
import logging
from zoneinfo import ZoneInfo


class CustomFormatter(logging.Formatter):
    """Log formatter that prints time in a specific timezone and unified template."""

    def __init__(
        self, tz_name: str = "America/Sao_Paulo", datefmt: str = "%d/%m/%Y %H:%M:%S"
    ):
        super().__init__()
        self.timezone = ZoneInfo(tz_name)
        self.datefmt = datefmt
        self._template = (
            "%(levelname)s: %(asctime)s - %(module)s/%(funcName)s - LOG: %(message)s"
        )
        self._formatter = logging.Formatter(self._template, datefmt=self.datefmt)

    def formatTime(self, record: logging.LogRecord, datefmt=None):
        ct = datetime.fromtimestamp(record.created, self.timezone)
        return ct.strftime(datefmt or self.datefmt)

    def format(self, record: logging.LogRecord):
        return self._formatter.format(record)


def setup_logging(
    level: int = logging.INFO, tz_name: str = "America/Sao_Paulo"
) -> None:
    """Configure root logger with the custom formatter.

    Call this once at application start before other modules create loggers.
    """
    handler = logging.StreamHandler()
    handler.setFormatter(CustomFormatter(tz_name=tz_name))

    # Force=True to reset any previous basicConfig
    logging.basicConfig(level=level, handlers=[handler], force=True)
