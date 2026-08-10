"""Basic reylog usage example."""

from reylog import logger


logger.debug("Debug details are available")
logger.info("Loading spectra")
logger.test("Running synthetic-mixture benchmark")
logger.metric("NRMSE", 0.024137, precision=4)
logger.success("Experiment complete")
logger.warning("Calibration file not found; using defaults")
logger.error("Example error message")
