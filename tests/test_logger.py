from __future__ import annotations

import pytest

from reylog import logger


def reset_console(*, level: str = "DEBUG") -> None:
    logger.configure(
        level=level,
        colorize=False,
        show_time=False,
        show_location=False,
    )


def test_standard_levels_emit(capsys: pytest.CaptureFixture[str]) -> None:
    reset_console()

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
    reset_console()

    logger.test("benchmark")
    logger.metric("RMSE", 0.0317)

    output = capsys.readouterr().err
    assert "TEST" in output
    assert "benchmark" in output
    assert "METRIC" in output
    assert "RMSE: 0.0317" in output


def test_metric_precision(capsys: pytest.CaptureFixture[str]) -> None:
    reset_console()

    logger.metric("MCC", 0.92341, precision=3)

    output = capsys.readouterr().err
    assert "MCC: 0.923" in output


def test_metric_rejects_negative_precision() -> None:
    reset_console()

    with pytest.raises(ValueError, match="precision must be non-negative"):
        logger.metric("RMSE", 1.0, precision=-1)


def test_level_filtering(capsys: pytest.CaptureFixture[str]) -> None:
    reset_console(level="WARNING")

    logger.info("hidden")
    logger.warning("visible")

    output = capsys.readouterr().err
    assert "hidden" not in output
    assert "visible" in output


def test_reconfigure_does_not_duplicate_messages(
    capsys: pytest.CaptureFixture[str],
) -> None:
    reset_console()
    reset_console()
    reset_console()

    logger.info("exactly once")

    output = capsys.readouterr().err
    assert output.count("exactly once") == 1


def test_loguru_style_format_arguments(capsys: pytest.CaptureFixture[str]) -> None:
    reset_console()

    logger.info("Loaded {} samples", 53)
    logger.test("Testing {}", "mixture A")

    output = capsys.readouterr().err
    assert "Loaded 53 samples" in output
    assert "Testing mixture A" in output


def test_location_points_to_plain_function(capsys: pytest.CaptureFixture[str]) -> None:
    logger.configure(
        level="DEBUG",
        colorize=False,
        show_time=False,
        show_location=True,
    )

    logger.info("location check")

    output = capsys.readouterr().err
    assert "test_location_points_to_plain_function:" in output
    assert "reylog.logger" not in output


def test_location_includes_class_name(capsys: pytest.CaptureFixture[str]) -> None:
    logger.configure(
        level="DEBUG",
        colorize=False,
        show_time=False,
        show_location=True,
    )

    class TestClass:
        def init():
            logger.info("class location check")

    TestClass.init()

    output = capsys.readouterr().err
    assert "TestClass.init:" in output
    assert "class location check" in output


def test_location_includes_instance_method_class(
    capsys: pytest.CaptureFixture[str],
) -> None:
    logger.configure(
        level="DEBUG",
        colorize=False,
        show_time=False,
        show_location=True,
    )

    class Trainer:
        def fit(self) -> None:
            logger.info("training")

    Trainer().fit()

    output = capsys.readouterr().err
    assert "Trainer.fit:" in output
    assert "training" in output
