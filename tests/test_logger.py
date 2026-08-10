from __future__ import annotations

import pytest

from reylog import ReyLogger


def make_logger() -> ReyLogger:
    logger = ReyLogger()
    logger.configure(colorize=False, show_time=False, show_location=False)
    return logger


def test_standard_levels_emit(capsys: pytest.CaptureFixture[str]) -> None:
    logger = make_logger()

    logger.debug("debug message")
    logger.info("info message")
    logger.success("success message")
    logger.warning("warning message")
    logger.error("error message")

    output = capsys.readouterr().err
    assert "DEBUG" in output and "debug message" in output
    assert "INFO" in output and "info message" in output
    assert "SUCCESS" in output and "success message" in output
    assert "WARNING" in output and "warning message" in output
    assert "ERROR" in output and "error message" in output


def test_custom_levels_emit(capsys: pytest.CaptureFixture[str]) -> None:
    logger = make_logger()

    logger.test("benchmark")
    logger.metric("RMSE", 0.0317)

    output = capsys.readouterr().err
    assert "TEST" in output
    assert "benchmark" in output
    assert "METRIC" in output
    assert "RMSE: 0.0317" in output


def test_metric_precision(capsys: pytest.CaptureFixture[str]) -> None:
    logger = make_logger()

    logger.metric("MCC", 0.92341, precision=3)

    output = capsys.readouterr().err
    assert "MCC: 0.923" in output


def test_metric_rejects_negative_precision() -> None:
    logger = make_logger()

    with pytest.raises(ValueError, match="precision must be non-negative"):
        logger.metric("RMSE", 1.0, precision=-1)


def test_level_filtering(capsys: pytest.CaptureFixture[str]) -> None:
    logger = make_logger()
    logger.configure(
        level="WARNING",
        colorize=False,
        show_time=False,
        show_location=False,
    )

    logger.info("hidden")
    logger.warning("visible")

    output = capsys.readouterr().err
    assert "hidden" not in output
    assert "visible" in output


def test_reconfigure_does_not_duplicate_messages(
    capsys: pytest.CaptureFixture[str],
) -> None:
    logger = make_logger()
    logger.configure(colorize=False, show_time=False, show_location=False)
    logger.configure(colorize=False, show_time=False, show_location=False)

    logger.info("exactly once")

    output = capsys.readouterr().err
    assert output.count("exactly once") == 1


def test_loguru_style_format_arguments(capsys: pytest.CaptureFixture[str]) -> None:
    logger = make_logger()

    logger.info("Loaded {} samples", 53)
    logger.test("Testing {}", "mixture A")

    output = capsys.readouterr().err
    assert "Loaded 53 samples" in output
    assert "Testing mixture A" in output
