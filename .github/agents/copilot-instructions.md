# erasmus-gp Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-03-14

## Active Technologies

- Python 3.12 (project baseline; black target) + stdlib (`abc`, `typing`, `collections.abc`), `egpcommon` (`CommonObj`, validators, logging), package-local `egppy.genetic_code` modules (001-anti-pattern-fixes)

## Project Structure

```text
egpcommon/
egpdb/
egpdbmgr/
egppkrapi/
egppy/
tests/
docs/
specs/
```

## Commands

```bash
source /workspaces/erasmus-gp/.venv/bin/activate
python -m unittest discover -s tests
```

## Code Style

- Python 3.12, formatted with `black` (100-character line length) and `isort`
- Type checking with `pyright`
- Google-style docstrings
- Explicit imports (e.g. `from json import dump, load`)

## Recent Changes

- 001-anti-pattern-fixes: Refactored mutable/frozen genetic-code classes for MRO-safe initialization, enforced `__hash__ = None` for mutable objects, and hardened `GGCDict` to immutable-by-construction.

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
