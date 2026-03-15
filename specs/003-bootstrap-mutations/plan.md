# Implementation Plan: Bootstrap Mutations Implementation

**Branch**: `003-bootstrap-mutations` | **Date**: 2026-03-15 | **Spec**: [/workspaces/erasmus-gp/specs/003-bootstrap-mutations/spec.md]
**Input**: Feature specification from `/specs/003-bootstrap-mutations/spec.md`

## Summary

This feature implements the "Bootstrap Mutations" work package for Erasmus GP. It involves completing and implementing a full set of mutation primitives (`Create`, `Wrap`, `Insert`, `Crossover`, `Rewire`, `Delete`, `Split`, `Iterate`) that operate on the Connection Graph (`CGraph`). These mutations are governed by specific "Connection Processes" that enforce idiomatic wiring through "Force Primary" logic. The implementation also includes structural optimizations like "Unused Parameter Removal" and "Dead Code Elimination".

## Technical Context

**Language/Version**: Python 3.12 (as per Constitution)
**Primary Dependencies**: Internal Erasmus GP packages (`egpcommon`, `egppy`)
**Storage**: N/A (Mutations operate on in-memory `EGCode` objects)
**Testing**: `unittest` framework (Constitution requirement)
**Target Platform**: Linux (development in devcontainer)
**Project Type**: Library / Engine Component (part of `egppy.physics`)
**Performance Goals**: Favor structural correctness over speed; handle complex mutation chains atomically.
**Constraints**: Maximum graph size limits; Directed Acyclic Graph (DAG) integrity; Copy-on-Write for atomicity.
**Scale/Scope**: 8 mutation primitives, 4 connection processes, 2 optimization passes.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
| :--- | :--- | :--- |
| **I. Meta-Evolution First** | PASS | Mutations operate on genetic codes which are themselves evolved. |
| **II. Modular Monorepo** | PASS | Implementation stays within `egppy` and uses `egpcommon`. |
| **III. Defensive Validation** | PASS | `verify()` and `consistency()` to be used for `EGCode` and `CGraph`. |
| **IV. Data Integrity** | PASS | Does not modify `sha256_signature`; produces JSON-serializable output. |
| **V. Scalable Workers** | PASS | Logic is stateless and operates on individual genetic codes. |
| **VI. Memory Efficiency** | PASS | `__slots__` and `ObjectDeduplicator` to be used where appropriate. |
| **VII. Research-Driven** | PASS | Implements current design requirements without speculative overhead. |

## Project Structure

### Documentation (this feature)

```text
specs/003-bootstrap-mutations/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
egppy/
└── egppy/
    └── physics/
        ├── mutations/      # New: Internal library for primitives
        ├── processes.py    # New: Connection process logic
        └── optimization.py # New: DCE and parameter removal
tests/
└── test_egppy/
    └── test_physics/
        ├── test_mutations.py
        ├── test_processes.py
        └── test_optimization.py
```

**Structure Decision**: Logic will be integrated into `egppy.physics`, following the existing package structure. Primitives will be grouped in a sub-module for clarity.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
| ----------- | ------------ | ------------------------------------- |
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
