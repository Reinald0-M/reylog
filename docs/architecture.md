# Architecture

## Purpose

`reylog` is an opinionated facade over Loguru. It exists to centralize logging conventions that would otherwise be copied into each repository.

It is intentionally not a new logging engine.

## Dependency direction

```text
consumer repository
      |
      v
src/reylog/logger.py
      |
      +----> src/reylog/styles.py
      |
      v
    Loguru
      |
      v
managed stderr sink
```

Consumer code should import only the public API:

```python
from reylog import logger
```

Code outside the package should not depend on internal modules such as `reylog.styles` unless it deliberately accepts that those internals may change.

## Public API

Version `0.1.0` exposes one configured singleton named `logger` with these methods:

- `debug(message, *args, **kwargs)`
- `info(message, *args, **kwargs)`
- `success(message, *args, **kwargs)`
- `warning(message, *args, **kwargs)`
- `error(message, *args, **kwargs)`
- `test(message, *args, **kwargs)`
- `metric(name, value, precision=None)`
- `configure(...)`

The wrapper accepts Loguru-style `{}` formatting arguments for ordinary messages.

## Levels

Standard levels are provided by Loguru. `reylog` adds two levels:

| Level | Number | Intended use |
|---|---:|---|
| `TEST` | 15 | Tests, benchmarks, validation stages, experiment steps |
| `METRIC` | 26 | Named numerical or scalar results |

`TEST` lies between Loguru's `DEBUG` and `INFO` levels. `METRIC` is intentionally assigned `26` rather than `25` because Loguru already uses `25` for `SUCCESS`.

The numeric values matter because Loguru filters records by severity number.

## Sink ownership

Loguru creates a default stderr sink when imported. On creation of the package singleton, `reylog` removes that default and installs its own stderr sink.

After initialization, `configure()` tracks the sink identifier returned by Loguru and replaces only that managed sink. This prevents duplicate console messages when configuration is called repeatedly.

The initial version is intended primarily for application and research-script entry points. If `reylog` later needs to coexist with independently configured Loguru sinks in larger libraries, sink ownership should be revisited explicitly rather than changed implicitly.

## Presentation

`styles.py` contains presentation constants and the console-format builder. This keeps color/layout decisions separate from behavior.

Current defaults are:

- timestamps shown as `HH:mm:ss`
- level names padded to a fixed width
- source location hidden by default
- color enabled by default
- `TEST` displayed in bold cyan
- `METRIC` displayed in bold magenta

## Source locations

The wrapper uses Loguru's `opt(depth=1)` before emitting records. Without this, Loguru would identify the wrapper method inside `reylog` as the call site. Increasing the depth by one reports the consumer's call site instead.

This is why:

```python
logger.configure(show_location=True)
logger.info("Loading data")
```

can display the location of the user's call rather than `reylog/logger.py`.

## Metric formatting

`metric()` supports an optional decimal precision:

```python
logger.metric("MCC", 0.92341, precision=3)
```

which displays:

```text
MCC: 0.923
```

Negative precision is rejected. Objects that do not support numeric fixed-point formatting fall back to `str(value)`.

## What should not be added casually

Features should be added only when they provide a reusable convention across repositories. In particular, avoid duplicating Loguru APIs simply to expose them under another name.

Examples that should require a concrete use case before implementation include:

- custom serialization systems
- networking transports
- database logging
- a second exception framework
- a bespoke asynchronous queue
- custom rotation logic already handled by Loguru

The maintenance target is a thin package with a stable surface, not a general logging framework.
