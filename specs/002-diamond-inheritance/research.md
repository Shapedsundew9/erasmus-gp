# Phase 0 Research: Diamond Inheritance Documentation & MRO Safety Tests

## Decision 1: Use documentation-only WP7 strategy (Option C)

- Decision: Keep current inheritance architecture intact and document it explicitly; add regression tests instead of restructuring class hierarchy.
- Rationale: The spec and existing tests indicate current C3 MRO behavior is correct and stable. Risk is maintainability confusion, not runtime defect.
- Alternatives considered:
  - Option A (merge frozen concrete into frozen ABC): rejected for this WP due to high refactor risk and broad import impact.
  - Option B (composition): rejected for this WP due to behavior and API surface risk.

## Decision 2: Place architecture documentation in worker component docs

- Decision: Write the feature architecture reference at `docs/components/worker/diamond_inheritance.md`.
- Rationale: Genetic code hierarchy belongs to the worker engine domain (`egppy`), and existing component docs are already organized under `docs/components/worker/`.
- Alternatives considered:
  - `docs/design/diamond_inheritance.md`: rejected because this is component-operational documentation rather than cross-cutting design governance.
  - `egppy/docs/diamond_inheritance.md`: rejected to avoid splitting core architecture docs across multiple roots.

## Decision 3: Create dedicated MRO regression module

- Decision: Add a new test file `tests/test_egppy/test_genetic_code/test_mro_diamond.py`.
- Rationale: Isolates MRO hierarchy invariants from existing mutability contract tests and simplifies maintenance/diagnosis.
- Alternatives considered:
  - Extend `test_mutability_contract.py`: rejected to avoid mixing orthogonal test concerns in one file.

## Decision 4: Model hierarchy scope as four families and five diamonds

- Decision: Treat CGraph, Interface, EndPoint, and EPRef/EPRefs as four families with five independent diamond linearizations.
- Rationale: EPRef and EPRefs each have distinct classes/MRO but are grouped in one family by source and conceptual domain.
- Alternatives considered:
  - Treat as five families: rejected for documentation consistency with existing code organization.

## Decision 5: Define explicit documentation contract for class docstrings

- Decision: Require class docstrings to include role, direct parents, shared grandparent, and why parent order matters.
- Rationale: This directly addresses onboarding confusion and provides an executable checklist for code review.
- Alternatives considered:
  - Minimal one-line docstrings: rejected because they do not communicate inheritance intent.

## Decision 6: Define strict MRO assertion strategy

- Decision: Assert exact `__mro__` sequence and subclass contracts in tests with clear expected vs actual output.
- Rationale: Exact sequence checks catch parent reordering/mixin insertion regressions that `issubclass` alone cannot detect.
- Alternatives considered:
  - Only `issubclass` checks: rejected as insufficient to detect dispatch-order regressions.
  - Snapshot text output comparisons: rejected as brittle and less clear on failure.

## Decision 7: Keep interface-contract artifact even for internal-only work

- Decision: Add a contract artifact in `specs/002-diamond-inheritance/contracts/` that defines documentation and test obligations.
- Rationale: This feature has no external API but still has verifiable internal contracts required for acceptance criteria.
- Alternatives considered:
  - Omit contracts directory: rejected because a lightweight internal contract improves phase handoff and task generation precision.
