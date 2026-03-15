# Implementation Plan: Diamond Inheritance Documentation & MRO Safety Tests

**Branch**: `002-diamond-inheritance` | **Date**: 2026-03-15 | **Spec**: `/workspaces/erasmus-gp/specs/002-diamond-inheritance/spec.md`
**Input**: Feature specification from `/workspaces/erasmus-gp/specs/002-diamond-inheritance/spec.md`

## Summary

Implement WP7 Option C as a documentation-and-tests feature: document the existing,
intentional diamond inheritance pattern across the genetic code class families and
add explicit MRO/subclass regression tests to prevent accidental base-order or
inheritance-chain breakage.

No production behavior changes are planned; this work strengthens maintainability,
onboarding clarity, and refactor safety.

## Technical Context

**Language/Version**: Python 3.12 (`requires-python >=3.12`, black target `py312`)  
**Primary Dependencies**: Standard library `unittest`; existing project packages (`egppy`, `egpcommon`)  
**Storage**: Markdown documentation files under `docs/` and spec artifacts under `specs/`  
**Testing**: `python -m unittest discover -s tests` (project standard; no pytest)  
**Target Platform**: Linux devcontainer and CI environments running Python 3.12  
**Project Type**: Python monorepo (library/framework packages)  
**Performance Goals**: N/A for runtime throughput; test additions should remain fast and deterministic  
**Constraints**: No runtime behavior changes; preserve existing API/import compatibility; follow Google docstring style and black/isort formatting  
**Scale/Scope**: 5 inheritance diamonds across 4 families; 20 classes receive explicit hierarchy docstrings; one new MRO-focused test module

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Research Gate Review

- **I. Meta-Evolution First**: PASS. Work is documentation/tests only and does not alter evolutionary symmetry.
- **II. Modular Monorepo**: PASS. Changes are scoped primarily to `egppy` plus shared docs and tests, with no dependency direction changes.
- **III. Defensive Validation**: PASS. No changes to validation boundary behavior.
- **IV. Data Integrity via Immutable Signatures**: PASS. `sha256_signature` untouched; no signature logic changes.
- **V. Scalable, Stateless Workers**: PASS. No worker/runtime architecture changes.
- **VI. Memory Efficiency & De-duplication**: PASS. No object layout/perf mutations in runtime code paths.
- **VII. Research-Driven Incrementalism**: PASS. Minimal, targeted change for current maintainability need.

**Gate Status**: PASS

### Post-Design Gate Review

- Planned artifacts remain documentation + tests only.
- No constitutional principle conflicts introduced by data model, contracts, or quickstart design.
- No exceptions/waivers required.

**Gate Status**: PASS (re-validated)

## Project Structure

### Documentation (this feature)

```text
specs/002-diamond-inheritance/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── mro-documentation-contract.md
└── tasks.md               # created later by /speckit.tasks
```

### Source Code (repository root)

```text
docs/
└── components/
    └── worker/
        └── diamond_inheritance.md      # implementation target from spec

egppy/
└── egppy/
    └── genetic_code/
        ├── c_graph_abc.py
        ├── frozen_c_graph.py
        ├── c_graph.py
        ├── interface_abc.py
        ├── frozen_interface.py
        ├── interface.py
        ├── endpoint_abc.py
        ├── frozen_endpoint.py
        ├── endpoint.py
        ├── ep_ref_abc.py
        ├── frozen_ep_ref.py
        └── ep_ref.py

tests/
└── test_egppy/
    └── test_genetic_code/
        ├── test_mutability_contract.py
        └── test_mro_diamond.py         # new
```

**Structure Decision**: Use existing monorepo package structure; add one worker documentation file
and one dedicated MRO regression test file while preserving all existing package boundaries.

## Complexity Tracking

No constitution violations requiring justification.
