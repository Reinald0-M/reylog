# Changelog

All notable changes to `reylog` are documented here.

The project follows semantic versioning.

## Unreleased

### Added

- Add `logger.metrics(...)` for compact single-record logging of multiple
  metrics, including per-value precision and readable keyword display names.

## 0.1.0 - 2026-08-10

### Added

- Initial installable Python package.
- Loguru-backed `logger` singleton.
- Standard `debug`, `info`, `success`, `warning`, and `error` methods.
- Custom `TEST` level for benchmarks and validation stages.
- Custom `METRIC` level and `metric(name, value, precision=...)` helper.
- Configurable console level, timestamps, source locations, and colors.
- Unit tests and basic usage example.
- Package architecture, installation, API, development, and design documentation.
