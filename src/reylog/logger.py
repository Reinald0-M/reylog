"""Public logger implementation for :mod:`reylog`.

`ReyLogger` is intentionally a small facade over Loguru. It owns the stable API
and default presentation used by projects that depend on ``reylog`` while
leaving actual log-record and sink machinery to Loguru.
"""

from __future__ import annotations

import sys
from typing import Any

from loguru import logger as _loguru_logger

from .styles import (
    DEFAULT_LEVEL,
    METRIC_LEVEL_COLOR,
    METRIC_LEVEL_ICON,
    METRIC_LEVEL_NAME,
    METRIC_LEVEL_NO,
    TEST_LEVEL_COLOR,
    TEST_LEVEL_ICON,
    TEST_LEVEL_NAME,
    TEST_LEVEL_NO,
    console_format,
)


def _register_level(name: str, no: int, color: str, icon: str) -> None:
    """Register a custom Loguru level if it does not already exist.

    Loguru keeps levels globally on its logger singleton. Package reloads and
    interactive sessions can therefore encounter an already-registered level.
    In that case, preserving the existing level is safer than raising during
    import.
    """

    try:
        _loguru_logger.level(name)
    except ValueError:
        _loguru_logger.level(name, no=no, color=color, icon=icon)


class ReyLogger:
    """Small, opinionated logging facade backed by Loguru.

    The object is designed to be imported as a singleton:

    .. code-block:: python

        from reylog import logger

        logger.info("Loading data")
        logger.test("Running benchmark")
        logger.metric("RMSE", 0.031)

    Notes
    -----
    ``reylog`` manages one console sink. Calling :meth:`configure` replaces
    only that managed sink, so repeated configuration does not create duplicate
    console messages.
    """

    def __init__(self) -> None:
        _register_level(
            TEST_LEVEL_NAME,
            TEST_LEVEL_NO,
            TEST_LEVEL_COLOR,
            TEST_LEVEL_ICON,
        )
        _register_level(
            METRIC_LEVEL_NAME,
            METRIC_LEVEL_NO,
            METRIC_LEVEL_COLOR,
            METRIC_LEVEL_ICON,
        )

        # Loguru ships with a default stderr sink. reylog replaces it once so
        # users get reylog formatting immediately after import.
        _loguru_logger.remove()
        self._handler_id: int | None = None
        self.configure()

    def configure(
        self,
        *,
        level: str | int = DEFAULT_LEVEL,
        show_time: bool = True,
        show_location: bool = False,
        colorize: bool = True,
    ) -> None:
        """Configure reylog's managed console sink.

        Parameters
        ----------
        level:
            Minimum Loguru level name or numeric severity emitted to the
            console. Defaults to ``"DEBUG"``.
        show_time:
            Include a compact ``HH:mm:ss`` timestamp.
        show_location:
            Include ``module:function:line`` source information.
        colorize:
            Enable Loguru color markup for the console output.
        """

        if self._handler_id is not None:
            _loguru_logger.remove(self._handler_id)

        self._handler_id = _loguru_logger.add(
            sys.stderr,
            level=level,
            format=console_format(
                show_time=show_time,
                show_location=show_location,
            ),
            colorize=colorize,
            backtrace=False,
            diagnose=False,
        )

    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Emit a ``DEBUG`` message."""

        _loguru_logger.opt(depth=1).debug(message, *args, **kwargs)

    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Emit an ``INFO`` message."""

        _loguru_logger.opt(depth=1).info(message, *args, **kwargs)

    def success(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Emit a ``SUCCESS`` message."""

        _loguru_logger.opt(depth=1).success(message, *args, **kwargs)

    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Emit a ``WARNING`` message."""

        _loguru_logger.opt(depth=1).warning(message, *args, **kwargs)

    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Emit an ``ERROR`` message."""

        _loguru_logger.opt(depth=1).error(message, *args, **kwargs)

    def test(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Emit a ``TEST`` message for validation or benchmark stages."""

        _loguru_logger.opt(depth=1).log(
            TEST_LEVEL_NAME,
            message,
            *args,
            **kwargs,
        )

    def metric(
        self,
        name: str,
        value: Any,
        *,
        precision: int | None = None,
    ) -> None:
        """Emit a named scalar result using the ``METRIC`` level.

        Parameters
        ----------
        name:
            Human-readable metric name, such as ``"RMSE"`` or ``"MCC"``.
        value:
            Value to display.
        precision:
            Optional number of digits after the decimal point. If formatting
            fails for the supplied object, reylog falls back to ``str(value)``.
        """

        rendered = str(value)
        if precision is not None:
            if precision < 0:
                raise ValueError("precision must be non-negative")
            try:
                rendered = f"{value:.{precision}f}"
            except (TypeError, ValueError):
                rendered = str(value)

        _loguru_logger.opt(depth=1).log(
            METRIC_LEVEL_NAME,
            "{}: {}",
            name,
            rendered,
        )


logger = ReyLogger()
