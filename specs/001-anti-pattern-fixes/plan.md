# Implementation Plan: Anti-Pattern Fixes for Genetic Code Class Hierarchy (WP4-WP6)

**Branch**: `001-anti-pattern-fixes` | **Date**: 2026-03-14 | **Spec**: `specs/001-anti-pattern-fixes/spec.md`
**Input**: Feature specification from `specs/001-anti-pattern-fixes/spec.md`

## Summary

Implement the remaining anti-pattern work packages in `egppy/genetic_code` by:
1. Refactoring mutable/frozen initialization paths so mutable classes stop bypassing parent
   initialization (WP4).
2. Removing hashability from mutable objects by setting `__hash__ = None` contracts on
   mutable ABCs and fixing all mutable-hash call sites (WP5).
3. Replacing `GGCDict` runtime immutability flag flow with single-step immutable
   construction using `EGCDict` as builder input (WP6).

WP7 is explicitly deferred out of scope for this branch.

## Technical Context

**Language/Version**: Python 3.12 (project baseline; black target)  
**Primary Dependencies**: stdlib (`abc`, `typing`, `collections.abc`), `egpcommon` (`CommonObj`, validators, logging), package-local `egppy.genetic_code` modules  
**Storage**: In-memory genetic code objects persisted via PostgreSQL-facing layers (`egpdb`, `egpdbmgr`) and signed JSON artifacts  
**Testing**: `unittest` via `python -m unittest discover -s tests` (pytest prohibited)  
**Target Platform**: Linux dev containers / stateless worker runtime
**Project Type**: Python monorepo library + worker engine  
**Performance Goals**: No regression in graph object construction and hashing paths; preserve existing de-duplication throughput characteristics  
**Constraints**: Keep API compatibility where feasible, no unrelated changes, maintain black/isort/pyright compliance, preserve frozen hash semantics  
**Scale/Scope**: `egppy/genetic_code` primary edits with audit/fix across `egppy`, `egpdb`, `egpdbmgr`, and tests for mutable hash usage and GGCDict construction

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Meta-Evolution First**: PASS. Changes are implementation-safety refactors only; no
  change to evolutionary symmetry among populations.
- **II. Modular Monorepo**: PASS. Work is scoped to package boundaries; no new cross-package
  cycles.
- **III. Defensive Validation**: PASS. Plan preserves input validation behavior and requires
  explicit validation on new constructor flows (`GGCDict`).
- **IV. Immutable Signatures**: PASS. No changes to `sha256_signature` or signing mechanics.
- **V. Stateless Workers**: PASS. No worker state model changes.
- **VI. Memory Efficiency / __slots__**: PASS. No deviation from slotted CommonObj-derived
  design; class-shape changes remain compatible.
- **VII. Research-Driven Incrementalism**: PASS. Scope restricted to current anti-patterns;
  WP7 deferred to reduce risk.

**Gate Result (Pre-Phase 0)**: PASS

## Project Structure

### Documentation (this feature)

```text
specs/001-anti-pattern-fixes/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── genetic-code-mutability-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
egppy/egppy/genetic_code/
├── c_graph.py
├── c_graph_abc.py
├── endpoint.py
├── endpoint_abc.py
├── ep_ref.py
├── ep_ref_abc.py
├── frozen_c_graph.py
├── frozen_endpoint.py
├── frozen_ep_ref.py
├── frozen_interface.py
├── ggc_dict.py
├── egc_dict.py
└── interface.py

egpdb/
egpdbmgr/

tests/
└── test_egppy/
    └── test_genetic_code/
```

**Structure Decision**: Use the existing monorepo package layout. Modify only targeted
`egppy/genetic_code` modules and add focused unit tests under
`tests/test_egppy/test_genetic_code/`, with cross-package hash/construction audits for
`egpdb` and `egpdbmgr` call sites.

## Phase 0 Research Summary

Research decisions are documented in `specs/001-anti-pattern-fixes/research.md` and resolve
all specification clarifications with explicit choices for WP4/WP5/WP6.

## Phase 1 Design Summary

- Data model and state transitions: `specs/001-anti-pattern-fixes/data-model.md`
- Interface contract: `specs/001-anti-pattern-fixes/contracts/genetic-code-mutability-contract.md`
- Implementation quickstart and verification flow: `specs/001-anti-pattern-fixes/quickstart.md`

## Constitution Check (Post-Design)

- **Validation pattern preserved**: Design requires constructor validation to remain explicit.
- **Testing gate compliance**: Design mandates unittest-only verification and migration tests.
- **Incremental scope discipline**: WP7 remains out of scope by contract and artifacts.

**Gate Result (Post-Phase 1)**: PASS

## Complexity Tracking

No constitution violations requiring exceptions.
