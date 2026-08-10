# reylog

`reylog` is a small, opinionated Python logger for personal scripts, research code, and lightweight applications. It provides a consistent logging API across repositories while delegating the underlying logging machinery to [Loguru](https://github.com/Delgan/loguru).

The goal is not to replace Loguru. The goal is to give your projects one stable interface and one set of conventions instead of copying logger configuration from repository to repository.

## Features

- One import: `from reylog import logger`
- Colored terminal output
- Familiar severity methods: `debug`, `info`, `success`, `warning`, and `error`
- Research/workflow helpers: `test` and `metric`
- Configurable minimum level, timestamps, and source locations
- Loguru underneath, so the package stays small
- No application-specific dependencies beyond Loguru

## Installation

From PyPI once published:

```bash
pip install reylog
```

During local development:

```bash
git clone https://github.com/Reinald0-M/reylog.git
cd reylog
pip install -e ".[dev]"
```

To use the GitHub version directly from another project:

```bash
pip install "git+https://github.com/Reinald0-M/reylog.git"
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

Typical output is intentionally compact:

```text
14:23:41 | INFO     | Loading spectra
14:23:41 | TEST     | Running synthetic-mixture benchmark
14:23:41 | METRIC   | NRMSE: 0.0241
14:23:41 | SUCCESS  | Experiment complete
14:23:41 | WARNING  | Calibration file not found; using defaults
14:23:41 | ERROR    | Optimization failed
```

Colors are applied in terminals that support them.

## API

### Standard messages

```python
logger.debug("Detailed diagnostic information")
logger.info("Normal program information")
logger.success("A task completed successfully")
logger.warning("Something deserves attention")
logger.error("An operation failed")
```

### Test messages

Use `test()` for tests, benchmarks, validation steps, or named experiment stages:

```python
logger.test("Evaluating Mg/P synthetic mixtures")
```

`TEST` is registered as a custom Loguru level with numeric value `15`, between `DEBUG` (`10`) and `INFO` (`20`). This makes it filterable like any other log level.

### Metric messages

Use `metric()` for named scalar results:

```python
logger.metric("RMSE", 0.0317)
logger.metric("MCC", 0.92, precision=3)
```

Output:

```text
METRIC   | RMSE: 0.0317
METRIC   | MCC: 0.920
```

`METRIC` is registered as a custom Loguru level with numeric value `25`, between `INFO` (`20`) and `SUCCESS` (`25` in Loguru). Because Loguru already uses `25` for `SUCCESS`, `reylog` internally assigns `METRIC` the distinct value `26` to avoid a numeric collision.

`precision` only affects values that support standard numeric formatting. If no precision is supplied, `str(value)` is used.

## Configuration

`reylog` is usable immediately after import. For project-specific presentation, call `configure()` once near the entry point of your program:

```python
from reylog import logger

logger.configure(
    level="INFO",
    show_time=True,
    show_location=False,
)
```

Available arguments:

| Argument | Default | Meaning |
|---|---:|---|
| `level` | `"DEBUG"` | Minimum level emitted by the console sink |
| `show_time` | `True` | Include `HH:mm:ss` in each message |
| `show_location` | `False` | Include `module:function:line` |
| `colorize` | `True` | Enable Loguru color markup |

Example with source locations:

```python
logger.configure(show_location=True)
logger.info("Loading data")
```

```text
14:23:41 | INFO     | loader:load_dataset:42 | Loading data
```

Calling `configure()` replaces the console sink managed by `reylog`; it does not change your application code or public logging API.

## Why a wrapper instead of a Loguru fork?

Forking Loguru would make `reylog` responsible for maintaining a logging engine, tracking upstream changes, and carrying a large amount of code that is unrelated to the actual goal.

Instead, the architecture is:

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
stderr / future sinks
```

`reylog` owns:

- method names
- custom levels
- colors
- output layout
- defaults
- project-wide conventions

Loguru owns:

- sink management
- log records
- formatting engine
- exception handling
- thread/process-safe logging behavior
- the underlying logging implementation

This separation keeps `reylog` small enough to maintain while still giving all of your repositories the same interface.

## Project structure

```text
reylog/
├── pyproject.toml
├── README.md
├── LICENSE
├── CHANGELOG.md
├── .gitignore
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

## Design principles

1. **Small public API.** Add helpers only when they represent a convention that is useful across multiple repositories.
2. **Do not rebuild Loguru.** Backend functionality belongs in the dependency unless `reylog` needs a stable abstraction around it.
3. **Useful defaults first.** `from reylog import logger` should be enough for normal scripts.
4. **Configuration at the application boundary.** Libraries should generally emit messages; executable applications decide presentation.
5. **Backwards compatibility matters.** Once another repository depends on a public `reylog` method, changes to that method should be treated as API changes.

## Development

Create a virtual environment and install the package with development dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Run the test suite:

```bash
pytest
```

Run the example:

```bash
python examples/basic.py
```

Build distributable artifacts:

```bash
python -m build
```

The resulting wheel and source distribution will be written to `dist/`.

## Versioning

The package uses semantic versioning:

- patch: bug fixes that preserve the public API
- minor: backwards-compatible features or new helpers
- major: breaking API changes

The initial package version is `0.1.0`.

## Future additions

Potential additions should remain optional and justified by repeated use across projects. Examples include:

- file logging
- JSON/structured sinks
- experiment context via `bind()`
- timers/context managers
- richer metric metadata

These are intentionally not part of `0.1.0`.

## License

MIT. See `LICENSE`.
