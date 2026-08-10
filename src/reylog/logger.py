"""Public logger implementation for :mod:`reylog`.

`ReyLogger` is intentionally a small facade over Loguru. It owns the stable API
and default presentation used by projects that depend on ``reylog`` while
leaving actual log-record and sink machinery to Loguru.
"""

from __future__ import annotations

import inspect
import sys
from types import CodeType, FrameType
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
    """Register a custom Loguru level if it does not already exist."""

    try:
        _loguru_logger.level(name)
    except ValueError:
        _loguru_logger.level(name, no=no, color=color, icon=icon)


def _remove_loguru_default_sink() -> None:
    """Remove Loguru's stock handler without touching user-added sinks.

    Loguru's automatically-created stderr handler has identifier ``0``. If it
    was already removed, ``remove(0)`` raises ``ValueError``; that is harmless
    and means there is nothing for reylog to replace.
    """

    try:
        _loguru_logger.remove(0)
    except ValueError:
        pass


def _class_qualname_for_code(owner: type[Any], code: CodeType) -> str | None:
    """Find the qualified class member name associated with ``code``.

    Python 3.11+ exposes ``code.co_qualname`` directly. This lookup is the
    compatibility fallback for Python 3.10, including methods called directly
    on a class without ``self`` or ``cls`` parameters.
    """

    for name, value in vars(owner).items():
        candidate = value

        if isinstance(value, (staticmethod, classmethod)):
            candidate = value.__func__
        elif isinstance(value, property):
            accessors = (value.fget, value.fset, value.fdel)
            if any(
                accessor is not None and getattr(accessor, "__code__", None) is code
                for accessor in accessors
            ):
                return f"{owner.__qualname__}.{name}"

        if getattr(candidate, "__code__", None) is code:
            return f"{owner.__qualname__}.{name}"

        if isinstance(value, type):
            nested = _class_qualname_for_code(value, code)
            if nested is not None:
                return nested

    return None


def _qualified_name(frame: FrameType) -> str:
    """Return the most informative callable name available for ``frame``."""

    code = frame.f_code

    # Python 3.11+ provides the exact lexical qualified name, including class
    # membership, without requiring any runtime object lookup.
    qualname = getattr(code, "co_qualname", None)
    if qualname:
        return qualname

    # Fast Python 3.10 paths for ordinary instance and class methods.
    instance = frame.f_locals.get("self")
    if instance is not None:
        return f"{type(instance).__qualname__}.{code.co_name}"

    cls = frame.f_locals.get("cls")
    if isinstance(cls, type):
        return f"{cls.__qualname__}.{code.co_name}"

    # Handles methods such as ``def init(): ...; TestClass.init()`` where no
    # ``self`` or ``cls`` variable exists in the frame.
    for value in frame.f_globals.values():
        if isinstance(value, type):
            resolved = _class_qualname_for_code(value, code)
            if resolved is not None:
                return resolved

    return code.co_name


def _location_from_frame(frame: FrameType) -> str:
    """Render a caller frame as ``qualified_name:line``."""

    return f"{_qualified_name(frame)}:{frame.f_lineno}"


class ReyLogger:
    """Small, opinionated logging facade backed by Loguru.

    Consumers should normally use the package singleton rather than creating
    instances directly:

    .. code-block:: python

        from reylog import logger

        logger.info("Loading data")
        logger.test("Running benchmark")
        logger.metric("RMSE", 0.031)

    ``reylog`` manages one console sink. Calling :meth:`configure` replaces
    only that managed sink, so repeated configuration does not duplicate its
    console output.
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

        _remove_loguru_default_sink()
        self._handler_id: int | None = None
        self._show_location = False
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
            Include ``qualified_function:line`` source information, such as
            ``Trainer.fit:42`` or ``load_data:18``.
        colorize:
            Enable Loguru color markup for the console output.
        """

        if self._handler_id is not None:
            try:
                _loguru_logger.remove(self._handler_id)
            except ValueError:
                # An advanced user may have removed all Loguru sinks manually.
                # Reconfiguration should recover by installing a fresh sink.
                pass

        self._show_location = show_location
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

    def _caller_logger(self):
        """Bind the user call site when location display is enabled."""

        if not self._show_location:
            return _loguru_logger

        frame = inspect.currentframe()
        try:
            # current frame -> _caller_logger -> public reylog method -> caller
            caller = frame.f_back.f_back if frame is not None else None
            location = _location_from_frame(caller) if caller is not None else "unknown:0"
        finally:
            # Explicitly break frame reference cycles.
            del frame

        return _loguru_logger.bind(reylog_location=location)

    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Emit a ``DEBUG`` message."""

        self._caller_logger().opt(depth=1).debug(message, *args, **kwargs)

    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Emit an ``INFO`` message."""

        self._caller_logger().opt(depth=1).info(message, *args, **kwargs)

    def success(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Emit a ``SUCCESS`` message."""

        self._caller_logger().opt(depth=1).success(message, *args, **kwargs)

    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Emit a ``WARNING`` message."""

        self._caller_logger().opt(depth=1).warning(message, *args, **kwargs)

    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Emit an ``ERROR`` message."""

        self._caller_logger().opt(depth=1).error(message, *args, **kwargs)

    def test(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Emit a ``TEST`` message for validation or benchmark stages."""

        self._caller_logger().opt(depth=1).log(
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

        self._caller_logger().opt(depth=1).log(
            METRIC_LEVEL_NAME,
            "{}: {}",
            name,
            rendered,
        )


logger = ReyLogger()
