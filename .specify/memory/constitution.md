# Erasmus GP Constitution

## Core Principles

### I. Meta-Evolution First

Erasmus GP is a meta-genetic programming system: it simultaneously evolves the solutions, the mutation operators, and the selection operators. All three populations ($G$, $M$, $Z$) obey the same evolutionary mechanics. Every architectural decision must preserve this recursive "turtles all the way down" property. Features or optimizations that would break the symmetry between populations are rejected.

### II. Modular Monorepo

The system is structured as a monorepo of interdependent packages (`egpcommon`, `egpdb`, `egpdbmgr`, `egppy`, `egppkrapi`). Each package has a clear, singular responsibility:

- `egpcommon` — shared primitives, validation, logging, security
- `egppy` — evolutionary engine, physics, genetic codes
- `egpdb` — database access layer
- `egpdbmgr` — Gene Pool lifecycle management
- `egppkrapi` — REST API

Packages must be independently installable with well-defined dependency direction (`egpcommon` ← `egppy`/`egpdb` ← `egpdbmgr` ← `egppkrapi`). Circular dependencies are forbidden.

### III. Defensive Validation (NON-NEGOTIABLE)

All classes inheriting from `CommonObj`/`CommonObjABC` must implement the two-tier validation pattern:

- **`verify()`** — fast, fail-at-first-error validation of individual values (type, range, format). Called eagerly on all inputs.
- **`consistency()`** — expensive cross-field and structural validation (graph integrity, referential checks). Deferred until after all `verify()` calls pass.

Functions and methods validate inputs at the boundary and raise standard exceptions immediately. Runtime assertions guard developer invariants. The `Validator` mixin provides reusable check methods returning booleans; callers decide exception type.

### IV. Data Integrity via Immutable Signatures

The `sha256_signature` function in `egpcommon/common.py` is the identity system for all genetic codes. **It must never be changed.** Signatures encode lineage, computational graph, inline code, imports, and creator UUID. Different evolutionary paths always produce different signatures. All public data at rest is JSON and digitally signed (Ed25519/RSA) with `dump_signed_json`.

### V. Scalable, Stateless Workers

Workers and fitness executors are independent, stateless containers. A worker connects to exactly one Gene Pool (PostgreSQL). Gene Pools connect to Genomic Libraries for broader storage. The storage hierarchy is designed to scale: worker cache (1 MB) → worker 2nd-level cache (1 GB) → Gene Pool (1 TB) → Archive/Biome (1 PB). Kubernetes orchestration is the target deployment model.

### VI. Memory Efficiency & De-duplication

All `CommonObj`-derived classes use `__slots__`. Standard immutable objects (tuples, frozensets) and common immutable cluston objects use `ObjectDeduplicator` (LRU-cache backed) when the expected hit rate justifies the ~120 bytes of per-entry overhead. Deduplicator statistics are monitored via the global registry.

### VII. Research-Driven Incrementalism

EGP is a research project, not a product. The primary goal is to demonstrate meta-learning: that a system can learn how to learn better. Version $N$ illuminates the path to version $N+1$. Over-engineering for hypothetical future requirements is avoided. Complexity must be justified by current, demonstrable need.

## Security & Data Integrity

- **Signed artifacts**: All released data and codons are cryptographically signed. Private keys are injected via environment secrets, never committed. Public keys ship in `egpcommon/data/public_keys/`.
- **Secret management**: Devcontainer secrets are sourced from environment variables or GitHub Codespaces secrets, not from committed files.
- **Input validation**: All external inputs (user data, API payloads, database reads) are validated at the boundary using `verify()` + `consistency()` or the `Validator` mixin. Hostnames, passwords, URLs, filenames, and datetimes have dedicated validators enforcing RFC compliance and safe patterns.
- **CI gate**: Pull requests run unit tests without requiring repository secrets. Integration tests requiring real credentials are kept out of the default PR gate.

## Coding Standards & Quality Gates

- **Formatter**: `black` with 100-character line length, targeting Python 3.12.
- **Import sorting**: `isort` with black-compatible profile, 100-character line length.
- **Type checking**: `pyright` on all function signatures and variables.
- **Imports**: Explicit (`from json import dump, load`), never wildcard or module-level.
- **Logging**: Custom logger from `egpcommon.egp_log` with levels FLOW, GC_DEBUG, OBJECT, TRACE, and integrity levels VERIFY / CONSISTENCY. Lazy formatting required; expensive computations guarded by `_logger.isEnabledFor()`.
- **Docstrings**: Google style for all modules, classes, and functions, including tests.
- **Testing**: `unittest` framework only. Do not use `pytest`. Tests in `tests/test_<package>/` mirroring source structure. Class/test fixtures for expensive setup. `coverage` measured; high coverage mandatory for critical components. All PRs must pass all unit tests and summarise results.
- **Documentation**: Markdown in `docs/`, LaTeX for formulas, compact tables, Mermaid diagrams with the Erasmus dark theme and semantic color mapping defined in the style guide.
- **Versioned API**: `egppy.physics.pgc_api` is the single source of truth for types and operations consumed by evolved code. It preserves binary compatibility across refactors.

## Governance

This constitution supersedes all ad-hoc practices and is the authoritative reference for project standards. All pull requests and code reviews must verify compliance with these principles.

- **Amendments** require documented rationale and explicit approval before merging.
- **Complexity** must be justified by the current task; speculative abstractions are rejected.
- **The copilot-instructions.md** file (`.github/copilot-instructions.md`) provides the operational implementation of these principles for AI and human contributors.

**Version**: 1.0.0 | **Ratified**: 2026-03-07 | **Last Amended**: 2026-03-07
