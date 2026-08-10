"""reylog: a small, opinionated logging facade backed by Loguru."""

from .logger import ReyLogger, logger

__all__ = ["ReyLogger", "logger"]
__version__ = "0.1.0"
