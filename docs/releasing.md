# Releasing reylog

This document describes the intended release process. Version `0.1.0` is prepared as an installable package, but publishing to PyPI is a separate action and is not automated yet.

## 1. Make and test changes

Create a virtual environment and install development dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Run the tests:

```bash
pytest
```

Build the distributions:

```bash
python -m build
```

GitHub Actions performs the same essential checks on supported Python versions.

## 2. Choose the next version

Use semantic versioning:

- patch: backwards-compatible fixes, e.g. `0.1.0 -> 0.1.1`
- minor: backwards-compatible functionality, e.g. `0.1.0 -> 0.2.0`
- major: breaking public-API changes, e.g. `0.x -> 1.0.0` once the API is considered stable

During the early `0.x` period, breaking changes should still be documented explicitly.

## 3. Update version information

Update the version in both:

- `pyproject.toml`
- `src/reylog/__init__.py`

Then add a dated entry to `CHANGELOG.md` describing user-visible changes.

## 4. Build and inspect distributions

Clean old artifacts if necessary:

```bash
rm -rf dist build
python -m build
```

Expected outputs include a wheel and source distribution in `dist/`.

Optionally inspect package metadata with Twine:

```bash
python -m pip install twine
python -m twine check dist/*
```

## 5. Tag the release

After the release commit is on `main`:

```bash
git tag -a v0.1.0 -m "reylog 0.1.0"
git push origin v0.1.0
```

Use the actual release version rather than copying `v0.1.0` for later releases.

## 6. PyPI publishing

Before the first PyPI release, confirm that the `reylog` project name is available and create/configure the appropriate PyPI account or trusted publisher.

A manual upload would use:

```bash
python -m twine upload dist/*
```

Do not publish until package ownership, credentials, and the intended public release are confirmed.

## 7. Post-release verification

Install the released version in a clean environment:

```bash
python -m venv /tmp/reylog-release-check
source /tmp/reylog-release-check/bin/activate
pip install reylog
python -c 'from reylog import logger; logger.success("reylog installed")'
```

Then verify the GitHub release/tag and update downstream projects deliberately rather than relying on unpinned development installs.
