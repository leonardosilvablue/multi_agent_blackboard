from datetime import datetime
import logging
from zoneinfo import ZoneInfo


class CustomFormatter(logging.Formatter):
    def __init__(
        self, tz_name: str = "America/Sao_Paulo", datefmt: str = "%d/%m/%Y %H:%M:%S"
    ):
        super().__init__()
        self.timezone = ZoneInfo(tz_name)
        self.datefmt = datefmt
        self._template = "%(levelname)s: %(asctime)s - %(module)s - %(message)s"
        self._formatter = logging.Formatter(self._template, datefmt=self.datefmt)

    def formatTime(self, record: logging.LogRecord, datefmt=None):
        ct = datetime.fromtimestamp(record.created, self.timezone)
        return ct.strftime(datefmt or self.datefmt)

    def format(self, record: logging.LogRecord):
        return self._formatter.format(record)


class RuntimeFilter(logging.Filter):
    """Filter to exclude noisy internal agent runtime logs"""

    def filter(self, record):
        # Don't show internal agent runtime logs
        if (
            "_single_threaded_agent_runtime" in record.name
            or record.module == "_single_threaded_agent_runtime"
        ):
            return False

        # Filter out serialization messages
        if "could not be serialized" in record.getMessage():
            return False

        # Filter out routine/debug runtime logs but allow errors and warnings
        if record.name.startswith("autogen_") and record.levelno < logging.WARNING:
            return False

        return True


def setup_logging(
    level: int = logging.INFO, tz_name: str = "America/Sao_Paulo"
) -> None:
    # Configure root logger
    handler = logging.StreamHandler()
    handler.setFormatter(CustomFormatter(tz_name=tz_name))
    handler.addFilter(RuntimeFilter())

    # Set default level for all loggers
    logging.basicConfig(level=level, handlers=[handler], force=True)

    # Set higher level for noisy modules
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("autogen").setLevel(logging.WARNING)
