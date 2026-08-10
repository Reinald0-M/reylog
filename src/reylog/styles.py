"""Presentation constants used by :mod:`reylog`.

This module deliberately contains no logging behavior. Keeping presentation
choices separate makes it easy to change colors or layout without changing the
public logger API.
"""

from __future__ import annotations

TEST_LEVEL_NAME = "TEST"
TEST_LEVEL_NO = 15
TEST_LEVEL_COLOR = "<cyan><bold>"
TEST_LEVEL_ICON = "T"

METRIC_LEVEL_NAME = "METRIC"
# Loguru's SUCCESS level is 25, so METRIC intentionally uses 26.
METRIC_LEVEL_NO = 26
METRIC_LEVEL_COLOR = "<magenta><bold>"
METRIC_LEVEL_ICON = "M"

DEFAULT_LEVEL = "DEBUG"

LEVEL_WIDTH = 8
TIME_FORMAT = "HH:mm:ss"


def console_format(*, show_time: bool, show_location: bool) -> str:
    """Build the default Loguru format string for the console sink.

    Parameters
    ----------
    show_time:
        Include a compact ``HH:mm:ss`` timestamp.
    show_location:
        Include a qualified callable location such as ``Trainer.fit:42`` or
        ``load_data:18``.

    Returns
    -------
    str
        A Loguru-compatible format string.
    """

    parts: list[str] = []

    if show_time:
        parts.append(f"<green>{{time:{TIME_FORMAT}}}</green>")

    parts.append(f"<level>{{level: <{LEVEL_WIDTH}}}</level>")

    if show_location:
        parts.append("<cyan>{extra[reylog_location]}</cyan>")

    parts.append("<level>{message}</level>")
    return " | ".join(parts)
