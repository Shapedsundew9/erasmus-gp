# Default Copilot Instructions

This file contains instructions for GitHub Copilot.

## General

*   Follow the user's requirements carefully and to the letter.
*   Follow Microsoft content policies.
*   Avoid content that violates copyrights.
*   If you are asked to generate content that is harmful, hateful, racist, sexist, lewd, or violent, only respond with "Sorry, I can't assist with that."
*   Keep your answers short and impersonal.

## Project Overview: Erasmus GP

This is a Python-based Genetic Programming framework named "Erasmus GP". It is structured as a monorepo containing multiple interdependent packages (`egpcommon`, `egpdb`, `egpdbmgr`, `egppy`, `egpseed`). The goal is to emulate evolution to solve problems.

### Architecture

*   The system is modular, with a worker pool (`egppy`) performing evolutionary computations.
*   Genetic data is stored in a PostgreSQL database ("Gene Pool"), managed by `egpdb` and `egpdbmgr`.
*   The project is designed for scalability, with considerations for containerization and orchestration (e.g., Kubernetes).
*   A REST API is provided by `egppkrapi`.


## Design Patterns

*   **Common Classes**: All common classes inherit from `egpcommon.common_obj.CommonObj`, which provides validation methods that shall be used to raise exceptions in verify() and consistency(). It also defines a validation pattern in the doc strings to be used consistently across the codebase. All members in a derived common_obj class shall be slotted.
*   **Validator Pattern:** The `egpcommon.validator` module implements a Validator class that encapsulates validation logic for various data types and formats.
*   **Defensive Programming:** Functions and methods must validate their inputs and raise appropriate standard exceptions as early as possible to prevent propagation of invalid data and reduce additional wasted time & resources when used by runtime evolved code through the `egppy.physics.pgc_api` defined API. Runtime type validation shall use assert statements when not enclosed in a `_logger.isEnabledFor(level=DEBUG)` block.
*   **Debug Pattern:** When `_logger.isEnabledFor(level=DEBUG)` is true aggressive verification of the internal data structures, types and object self consistency shall be performed to catch EGP application errors (raising `egpcommon.common.debug_exceptions`).
*   **Immutable object de-duplication:** Standard python immutable objects (e.g., tuples, frozensets) and freeable objects, once frozen, shall use `egpcommon.object_deduplicator` ObjectDeduplicator to ensure de-duplication and memory efficiency.

## Coding

*   **Style:** Write clean, well-documented, and idiomatic Python code. Adhere to the coding style enforced by `black` (100-character line length) and `isort`, as configured in the root `pyproject.toml`.
*   **Type Hinting:** Use type hints for all function signatures and variables where appropriate. The project uses `pyright` for static type checking.
*   **Imports:** Use explicit imports e.g. `from json import dump, load` rather than `import json` to improve code clarity.
*   **Logging:** Use the custom logger from `egpcommon.egp_log` for any new log messages and lazy formatting in log calls.
*   **Immutability:** The function `sha256_signature` in `egpcommon/egpcommon/common.py` is critical for data integrity and **must not be changed**. Its behavior is fundamental to the entire system.
*   **Dependencies:** Add new dependencies to the appropriate `pyproject.toml` and `requirements.txt` file for the relevant package.
*   **Documentation:** Use docstrings to document all modules, classes, and functions, including in test modules. Follow the existing style in the codebase.

## Testing

*   Ensure the virtual environment /workspaces/erasmus-gp/.venv is activated before running tests.
*   Add unit tests for new features and bug fixes using the `unittest` framework.
*   Place new tests in the repository root `tests` directory within a folder `test_[package name]` reflecting the package source structure beneath e.g. `tests/test_egppy/test_physics/test_psql_types.py`.
*   Ensure that all tests, including the dynamic `test_main_blocks.py`, pass before submitting code.

## Documentation

*   Update the Markdown documentation in the `docs` folder of the relevant package whenever you make changes to the architecture, add features, or modify behavior.
*   Use Mermaid diagrams to illustrate architectural changes where appropriate.

## Commits

*   Use meaningful commit messages that clearly describe the changes made.
