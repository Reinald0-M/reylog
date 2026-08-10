# reylog

`reylog` is a small, opinionated Python logger for scripts, research code, and lightweight applications. It provides one stable logging interface across repositories while using [Loguru](https://github.com/Delgan/loguru) as the backend.

The goal is deliberately narrow: stop copying logger setup between projects without maintaining a new logging engine.

## Features

- One import: `from reylog import logger`
- Colored terminal output
- Standard helpers: `debug`, `info`, `success`, `warning`, `error`
- `test()` for validation, benchmark, and experiment stages
- `metric()` for named numerical results
- Configurable minimum level, timestamps, source locations, and colors
- Loguru-style `{}` message formatting
- Source locations report the caller rather than the wrapper internals
- One managed console sink, so repeated `configure()` calls do not duplicate reylog output

## Installation

From PyPI once the package is published:

```bash
pip install reylog
```

Until then, install directly from GitHub:

```bash
pip install "git+https://github.com/Reinald0-M/reylog.git"
```

For development:

```bash
git clone https://github.com/Reinald0-M/reylog.git
cd reylog
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Quick start

```python
from reylog import logger

logger.info("Loading spectra")
logger.test("Running synthetic-mixture benchmark")
logger.metric("NRMSE", 0.0241)
logger.success("Experiment complete")
logger.warning("Calibration file not found; using defaults")
logger.error("Optimization failed")
```

Typical output:

```text
14:23:41 | INFO     | Loading spectra
14:23:41 | TEST     | Running synthetic-mixture benchmark
14:23:41 | METRIC   | NRMSE: 0.0241
14:23:41 | SUCCESS  | Experiment complete
14:23:41 | WARNING  | Calibration file not found; using defaults
14:23:41 | ERROR    | Optimization failed
```

Colors are applied in terminals that support them.

## Public API

### Standard messages

```python
logger.debug("Detailed diagnostic information")
logger.info("Normal program information")
logger.success("A task completed successfully")
logger.warning("Something deserves attention")
logger.error("An operation failed")
```

The methods preserve Loguru's brace-style formatting:

```python
logger.info("Loaded {} samples", 53)
```

### Test messages

Use `test()` for tests, benchmarks, validation steps, or named experiment stages:

```python
logger.test("Evaluating Mg/P synthetic mixtures")
```

`TEST` is a real Loguru level with numeric value `15`, between `DEBUG` (`10`) and `INFO` (`20`). It can therefore be filtered using normal Loguru severity rules.

### Metric messages

Use `metric()` for named scalar results:

```python
logger.metric("RMSE", 0.0317)
logger.metric("MCC", 0.92341, precision=3)
```

Output:

```text
METRIC   | RMSE: 0.0317
METRIC   | MCC: 0.923
```

`METRIC` uses numeric value `26`. Loguru already reserves `25` for `SUCCESS`, so `26` avoids a collision while keeping metrics near ordinary informational/success output.

`precision` must be non-negative. If omitted, `str(value)` is used.

## Configuration

`reylog` works immediately after import. Configure presentation once near the application entry point when needed:

```python
from reylog import logger

logger.configure(
    level="INFO",
    show_time=True,
    show_location=False,
    colorize=True,
)
```

| Argument | Default | Meaning |
|---|---:|---|
| `level` | `"DEBUG"` | Minimum level emitted by reylog's console sink |
| `show_time` | `True` | Include `HH:mm:ss` |
| `show_location` | `False` | Include `module:function:line` |
| `colorize` | `True` | Enable Loguru color markup |

With source locations enabled:

```python
logger.configure(show_location=True)
logger.info("Loading data")
```

```text
14:23:41 | INFO     | loader:load_dataset:42 | Loading data
```

`configure()` replaces only the console sink managed by `reylog`. At import time, the package removes Loguru's stock handler (`0`) if it still exists, but it does not deliberately remove other user-added Loguru sinks.

## Why a wrapper instead of a Loguru fork?

The architecture is intentionally simple:

```text
application code
      |
      v
   reylog API
      |
      v
    Loguru
      |
      v
console / future sinks
```

`reylog` owns conventions: method names, custom levels, colors, output layout, and defaults. Loguru owns records, sinks, formatting machinery, exception handling, and the underlying logging implementation.

A fork would make this project responsible for maintaining Loguru itself, which is unnecessary for the intended use case.

## Project structure

```text
reylog/
├── .github/workflows/ci.yml
├── CHANGELOG.md
├── LICENSE
├── README.md
├── pyproject.toml
├── docs/
│   ├── architecture.md
│   └── releasing.md
├── examples/
│   └── basic.py
├── src/
│   └── reylog/
│       ├── __init__.py
│       ├── logger.py
│       └── styles.py
└── tests/
    └── test_logger.py
```

For implementation details and design decisions, see [`docs/architecture.md`](docs/architecture.md). For versioning, building, tagging, and eventual PyPI publication, see [`docs/releasing.md`](docs/releasing.md).

## Development

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Run the example:

```bash
python examples/basic.py
```

Build a wheel and source distribution:

```bash
python -m build
```

GitHub Actions tests Python 3.10 through 3.13 and runs a package build on pushes and pull requests.

## Design principles

1. Keep the public API small.
2. Add helpers only when they encode a convention useful across multiple repositories.
3. Do not duplicate Loguru functionality without a concrete abstraction reason.
4. Keep `from reylog import logger` sufficient for normal use.
5. Treat methods used by downstream repositories as public API.
6. Prefer backwards-compatible additions over changing existing behavior.

## Versioning

The package uses semantic versioning. Initial version: `0.1.0`.

- patch: compatible bug fixes
- minor: compatible features and new helpers
- major: breaking API changes

See `CHANGELOG.md` for release history.

## Future additions

Potential additions should be driven by repeated use rather than added preemptively. Reasonable candidates include file logging, structured/JSON sinks, experiment context, and timers/context managers.

## License

MIT. See `LICENSE`.
