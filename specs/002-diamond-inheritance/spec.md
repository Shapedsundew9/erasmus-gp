# Feature Specification: Diamond Inheritance Documentation & MRO Safety Tests

**Feature Branch**: `002-diamond-inheritance`
**Created**: 2026-03-14
**Status**: Draft
**Input**: User description: "Implement WP7 — Diamond Inheritance Simplification using Option C: document the diamond pattern explicitly in docstrings and architecture docs, and add MRO tests to prevent accidental breakage."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Developer Understands Class Hierarchy (Priority: P1)

A contributor new to the Erasmus GP codebase opens a genetic code source file
(e.g. `c_graph.py`) and needs to understand why the mutable class inherits from
both a frozen concrete class and a mutable ABC. Clear, consistent docstrings
and an architecture document explain the diamond pattern, why it exists, and
how Python's MRO resolves it safely.

**Why this priority**: Without clear documentation, the diamond pattern is the
single most confusing structural aspect of the genetic code module. Every new
contributor encounters it and risks making breaking changes.

**Independent Test**: Can be verified by reviewing the updated docstrings and
architecture document for completeness and accuracy.

**Acceptance Scenarios**:

1. **Given** a developer opens any frozen ABC, frozen concrete, mutable ABC, or
   mutable concrete class in the genetic code module, **When** they read the
   class-level docstring, **Then** the docstring explains the class's role in
   the diamond hierarchy and names its direct parents and shared grandparent.
2. **Given** a developer wants to understand the overall pattern, **When** they
   open the architecture document, **Then** they find a single-page reference
   with diagrams, MRO listings, and rationale for all four class families.

---

### User Story 2 - MRO Regression Protection (Priority: P1)

A developer refactors a frozen or mutable class (e.g. adds a new base class or
reorders parents). Automated MRO tests catch any change to the expected method
resolution order and fail loudly, preventing silent behavioural regressions.

**Why this priority**: The diamond pattern is correct today because of specific
parent ordering. A single reorder can silently change which `__init__` or
`__hash__` is called. MRO tests are the only reliable safety net.

**Independent Test**: Can be verified by running the MRO test suite and
confirming all tests pass. Can be regression-tested by intentionally reordering
a parent list and confirming the test fails.

**Acceptance Scenarios**:

1. **Given** the four class families with their current parent orderings,
   **When** the MRO test suite runs, **Then** every class's MRO matches the
   expected linearisation exactly.
2. **Given** a developer accidentally reorders the parents of `CGraph` (e.g.
   `CGraph(CGraphABC, FrozenCGraph)` instead of `CGraph(FrozenCGraph, CGraphABC)`),
   **When** the MRO test suite runs, **Then** the test for `CGraph` fails with
   a clear message indicating the expected vs. actual MRO.
3. **Given** a developer adds a new base class to any class in the hierarchy,
   **When** the MRO test suite runs, **Then** the test detects the changed MRO
   and fails.

---

### User Story 3 - Subclass Contract Verification (Priority: P2)

A developer creates a new mutable class or modifies an existing one and needs
assurance that fundamental subclass relationships (`isinstance`, `issubclass`)
are preserved. Contract tests verify that every mutable class is a subclass of
its frozen ABC and that frozen classes are not subclasses of mutable ABCs.

**Why this priority**: `isinstance` checks against frozen ABCs are used
throughout the persistence layer and physics module. Breaking these silently
would cause runtime failures in production.

**Independent Test**: Can be verified by running the subclass contract tests
and confirming all assertions hold.

**Acceptance Scenarios**:

1. **Given** the four class families, **When** subclass contract tests run,
   **Then** every mutable concrete class is confirmed as a subclass of its
   frozen ABC.
2. **Given** the four class families, **When** subclass contract tests run,
   **Then** no frozen concrete class is a subclass of its mutable ABC.

---

### User Story 4 - Init Pattern Documentation (Priority: P2)

A developer needs to add a new frozen/mutable class pair following the same
pattern. The architecture document describes the three init patterns used
(optional-args-with-early-return, separated-hash-computation, and
template-method-with-override) so the developer can choose and apply the
correct one.

**Why this priority**: Without documenting the init patterns, new class pairs
risk introducing init-chain bugs that WP4 already fixed. This story prevents
regression of knowledge.

**Independent Test**: Can be verified by reviewing the architecture document
for completeness of init pattern descriptions and by running architecture-doc
content tests that assert required sections are present.

**Acceptance Scenarios**:

1. **Given** a developer reads the architecture document, **When** they look
   for init pattern guidance, **Then** they find a named description of each
   pattern with the class families that use it.
2. **Given** a developer creates a new frozen/mutable pair, **When** they
   follow the documented pattern, **Then** the new classes pass the existing
   MRO and init-chain test framework.

### Edge Cases

- What happens if a future refactor introduces a fifth class family? The
  architecture document must be generic enough to serve as a template, and
  the MRO test framework must be easy to extend.
- What happens if Python's MRO algorithm changes in a future version? The MRO
  tests will fail immediately, alerting maintainers.
- What happens if a class inherits from an additional mixin? The MRO tests
  will detect the changed linearisation.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every frozen ABC, frozen concrete, mutable ABC, and mutable
  concrete class in the four genetic code families (CGraph, Interface,
  EndPoint, EPRef/EPRefs — 5 diamonds total) MUST have a class-level docstring
  that names its direct parents, its role in the diamond hierarchy (frozen ABC,
  frozen concrete, mutable ABC, or mutable concrete), and the shared
  grandparent. Compliance MUST be verifiable either through explicit assertions
  in `tests/test_egppy/test_genetic_code/test_mro_diamond.py` or a reviewer
  checklist that maps each covered class to these required docstring elements.
- **FR-002**: An architecture document at `docs/components/worker/diamond_inheritance.md`
  MUST exist that describes the diamond inheritance pattern with a diagram for
  each of the four class families (5 diamonds), their full MRO listings, and
  the rationale for the pattern.
- **FR-003**: The architecture document MUST describe the three init patterns
  (optional-args-with-early-return, separated-hash-computation,
  template-method-with-override) and which families use each.
- **FR-004**: A test module at `tests/test_egppy/test_genetic_code/test_mro_diamond.py`
  MUST exist that validates the exact MRO of every class in all four families
  (5 diamonds: CGraph, Interface, EndPoint, EPRef, EPRefs).
- **FR-005**: The MRO test module MUST include subclass contract tests
  verifying that mutable concretes are subclasses of their frozen ABCs and
  that frozen concretes are not subclasses of mutable ABCs.
- **FR-006**: The MRO test module MUST produce a deterministic failure message
  when the actual MRO differs from the expected MRO. The message MUST include
  the target class name, the expected MRO sequence, and the actual MRO
  sequence.
- **FR-007**: The architecture document MUST include guidance for adding new
  frozen/mutable class pairs following the established pattern.
- **FR-008**: All existing tests MUST continue to pass after the documentation
  and test additions (no behavioural changes to production code).

### Key Entities

- **Class Family**: A group of related classes (FrozenFooABC, FrozenFoo,
  FooABC, Foo) that form a diamond inheritance structure. There are four
  families (CGraph, Interface, EndPoint, EPRef/EPRefs) containing five
  diamonds total, since EPRef and EPRefs each form an independent diamond
  within the same family. Key attributes: shared grandparent, init pattern,
  slot declarations.
- **MRO (Method Resolution Order)**: The linearised sequence of classes that
  Python searches when resolving a method call. Critical for correct
  `__init__`, `__hash__`, and `verify()` dispatch.

## Clarifications

### Session 2026-03-14

- Q: Where should the architecture document live? → A: `docs/components/worker/diamond_inheritance.md`
- Q: Should MRO tests go in the existing mutability contract file or a new module? → A: New file `tests/test_egppy/test_genetic_code/test_mro_diamond.py`
- Q: How to count EPRef vs EPRefs: 4 or 5 families? → A: 4 families with EPRef containing 2 sub-diamonds (5 diamonds total)

## Assumptions

- The diamond inheritance pattern is correct and intentional; this work package
  does not change any production code.
- Python's C3 linearisation algorithm will continue to resolve the diamonds
  correctly in all supported Python versions (3.10+).
- The existing `test_mutability_contract.py` tests for init chains and hash
  behaviour remain authoritative; the new MRO tests complement rather than
  replace them.
- The three init patterns identified (optional-args-with-early-return,
  separated-hash-computation, template-method-with-override) are the complete
  set currently in use.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of the 20 classes across the four families (4 classes × 5
  diamonds) have updated docstrings that name their diamond role and parents.
- **SC-002**: A new contributor can identify a class's position in the diamond
  hierarchy within 30 seconds by reading its docstring alone.
- **SC-003**: The MRO test suite covers all 5 diamond hierarchies and passes
  on the current codebase with zero failures.
- **SC-004**: Intentionally reordering parents of any one mutable concrete
  class causes at least one MRO test to fail.
- **SC-005**: All pre-existing unit tests continue to pass after this work
  package is complete (zero regressions).
