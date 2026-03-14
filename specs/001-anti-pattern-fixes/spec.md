# Feature Specification: Anti-Pattern Fixes for Genetic Code Class Hierarchy (WP4–WP6)

**Feature Branch**: `001-anti-pattern-fixes`  
**Created**: 2026-03-14  
**Status**: Draft  
**Reference**: `docs/design/remaining_work_packages.md` (WP4-WP6 in scope, WP7 deferred)

## Clarifications

### Session 2026-03-14

- Q: After finalisation, should mutation be blocked or should the hash snapshot be silently invalidated? → A: Remove `__hash__` from mutable objects entirely (`__hash__ = None`). Any call sites that hash a mutable object are bugs and must be identified and fixed as part of the work package — no snapshot/finalisation mechanism is needed.
- Q: Should WP7 (Diamond Inheritance Simplification) be in scope for this branch? → A: Defer — remove WP7 from this branch and open a dedicated follow-up work item.
- Q: Which `GGCDict` immutability pattern should be used for WP6? → A: Builder pattern — `GGCDict.__init__` accepts all fields at once (from a completed `EGCDict` or keyword args); `EGCDict` is the mutable builder; `set_members()` is removed.
- Q: How should the WP2 dependency be handled on this branch? → A: WP2 is already merged and is part of the current baseline — no cherry-pick or branch dependency needed.

## Overview

The Erasmus GP codebase contains four categories of class-hierarchy anti-patterns in the
`egppy/genetic_code/` module. Three earlier work packages (WP1–WP3) have already been
completed. This feature resolves the four remaining anti-patterns to improve reliability,
correctness, and long-term maintainability of the framework.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Predictable Object Construction (Priority: P1)

**As a** framework developer building or testing genetic code objects,  
**I want** every concrete class to initialise itself through its full inheritance chain,  
**so that** no setup logic is silently skipped and objects are always in a valid state after construction.

**Why this priority**: Bypassed initialisation chains are the root cause of hidden bugs,
duplicated setup code, and suppressed static-analysis warnings. Fixing this unblocks the
remaining work packages and improves confidence in every part of the codebase that constructs
these objects.

**Independent Test**: Construct each affected class (`CGraph`, `Interface`, `EndPoint`,
`EPRefs`) and verify all attributes are correctly populated with no pylint-disable overrides
remaining in the affected files.

**Acceptance Scenarios**:

1. **Given** any of the four affected classes, **When** an instance is constructed,
   **Then** every parent `__init__` in the MRO is called exactly once and no attributes are
   left uninitialised.
2. **Given** a frozen concrete class, **When** an instance is constructed,
   **Then** a pre-computed hash is stored at construction time.
3. **Given** a mutable concrete class, **When** an instance is constructed,
   **Then** no pre-computed hash is stored; hashes are computed dynamically on demand.
4. **Given** the four affected source files, **When** static analysis is run,
   **Then** zero `super-init-not-called` or `non-parent-init-called` suppression comments
   remain.

---

### User Story 2 — Non-Hashable Mutable Objects (Priority: P2)

**As a** framework developer working with genetic code objects,  
**I want** mutable objects to be explicitly non-hashable,  
**so that** Python's own type system prevents mutable objects from ever being used as
dictionary keys or set members, eliminating an entire class of data-integrity bugs.

**Why this priority**: Mutable objects that define `__hash__` silently break dict and set
invariants when their state changes after insertion. The correct Python pattern is to set
`__hash__ = None` on mutable ABCs, making `TypeError` automatic and immediate on any
attempt to hash them. Any existing call sites that hash a mutable object are themselves bugs
that must be identified and fixed as part of this work package.

**Independent Test**: Attempt to call `hash()` on any mutable genetic code instance and
verify `TypeError` is raised. Confirm that a comprehensive codebase audit finds no
legitimate call sites that hash mutable objects.

**Acceptance Scenarios**:

1. **Given** any mutable genetic code object (`CGraph`, `Interface`, `EndPoint`, `EPRef`,
   `EPRefs`, `EGCDict`),
   **When** `hash()` is called on it,
   **Then** `TypeError` is raised immediately (enforced by `__hash__ = None` on the ABC).
2. **Given** a frozen genetic code object,
   **When** `hash()` is called,
   **Then** the pre-computed hash from construction is returned unchanged.
3. **Given** a codebase-wide audit of `hash(` call sites on genetic code objects,
   **When** the audit is complete,
   **Then** any site that hashes a mutable object is identified, flagged, and replaced with
   an explicit `compute_hash()` helper or refactored to use the frozen equivalent.
4. **Given** all existing unit tests after the audit fixes are applied,
   **When** tests are executed,
   **Then** all tests pass.

---

### User Story 3 — Atomic Immutable Construction of Persisted Genetic Code (Priority: P3)

**As a** framework developer persisting genetic code to the database,  
**I want** `GGCDict` objects to be fully immutable from the moment of construction,  
**so that** I never accidentally modify a record after it has been created, and its hash
is always stable from the first use.

**Why this priority**: The current `set_members()` / runtime-flag approach means a
`GGCDict` object passes through a mutable phase before becoming "frozen", making it unsafe
to use as a dict key or set member during that phase. Fixing this prevents subtle persistence
bugs.

**Independent Test**: Construct a `GGCDict` by passing all required fields directly to
`__init__` (using a completed `EGCDict` or keyword arguments). Verify that no `set_members()`
call is needed, that `__setitem__` raises `TypeError` immediately, and that `hash()` returns
a stable value from the first call.

**Acceptance Scenarios**:

1. **Given** a fully specified set of genetic code fields,
   **When** a `GGCDict` is constructed by passing all fields to `__init__`,
   **Then** the object is immediately immutable (no `set_members()` call required).
2. **Given** a constructed `GGCDict`,
   **When** any attempt is made to modify it via item assignment or update,
   **Then** a `TypeError` is raised.
3. **Given** a constructed `GGCDict`,
   **When** `hash()` is called,
   **Then** a stable integer is returned with no prior finalisation step required.
4. **Given** a caller that previously used `EGCDict` as a mutable builder before passing it
   to `GGCDict.__init__`,
   **When** the construction call is made,
   **Then** `GGCDict` validates the completed builder and stores all fields immutably.
5. **Given** the existing persistence layer,
   **When** all existing tests are run after `set_members()` call sites are migrated,
   **Then** all tests pass with the updated construction pattern.

---

### Edge Cases

- `FrozenCGraph.__init__` constructs `FrozenInterface` objects from its inputs, while
  `CGraph.__init__` needs `Interface` objects — the shared attribute-setup helper must
  accept both forms.
- External packages (`egpdb`, `egpdbmgr`, `egpseed`) may import and construct affected
  classes directly; all call sites must be audited before changes are merged.
- Tests must pass with the virtual environment activated and data files present
  (`codons.json`, `types_def.json`, and their `.sig` files).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: All four mutable concrete classes (`CGraph`, `Interface`, `EndPoint`, `EPRefs`)
  MUST invoke the full parent `__init__` chain during construction.
- **FR-002**: Attribute initialisation logic MUST be separated from hash pre-computation in
  all frozen concrete `__init__` methods so mutable subclasses can call `super().__init__()`
  safely.
- **FR-003**: All `# pylint: disable=super-init-not-called` and
  `# pylint: disable=non-parent-init-called` comments MUST be removed from the affected files.
- **FR-004**: All mutable genetic code ABCs (`CGraphABC`, `InterfaceABC`, `EndPointABC`,
  `EPRefABC`, `EPRefsABC`, and the mutable `EGCDict` base) MUST set `__hash__ = None`,
  making any attempt to hash a mutable instance raise `TypeError` automatically.
- **FR-005**: A codebase-wide audit MUST be performed to locate all `hash(` call sites on
  genetic code objects; any site that hashes a mutable object MUST be refactored or replaced
  with an explicit `compute_hash()` call on the frozen equivalent.
- **FR-006**: Frozen genetic code classes MUST continue to return their pre-computed hash
  unchanged.
- **FR-007**: `GGCDict` MUST accept all required genetic code fields in its `__init__`
  (via a completed `EGCDict` builder or keyword arguments) and be fully immutable from the
  moment of construction — no separate `set_members()` call is required or permitted.
- **FR-008**: `EGCDict` acts as the mutable builder; all call sites that previously used the
  two-step `EGCDict` → `set_members()` → `GGCDict` pattern MUST be updated to construct a
  complete `EGCDict` and pass it to `GGCDict.__init__` in a single step.
- **FR-009**: Any attempt to assign to or update a `GGCDict` after construction MUST raise
  `TypeError`.
- **FR-010**: The `"immutable"` runtime flag dictionary key MUST be removed from `GGCDict`.
- **FR-011**: All existing unit tests in `tests/` MUST continue to pass after each work
  package is applied.
- **FR-012**: New unit tests MUST be added for each work package confirming the new behaviour
  (correct initialisation, correct hash contract, correct immutability).
- **FR-013**: Each work package MUST be implemented and verified independently in the order
  WP4 → WP5 → WP6.
- **FR-014**: WP7 (Diamond Inheritance Simplification) is explicitly out of scope for this
  branch and MUST be tracked as a separate follow-up work item in project documentation.
- **FR-015**: Governance documentation artifacts for this feature MUST be kept current and
  traceable to the constitution quality gates, including updates to quickstart/design docs
  and recorded deferred follow-up work.

### Key Entities

- **FrozenConcrete** (`FrozenCGraph`, `FrozenInterface`, `FrozenEndPoint`, `FrozenEPRefs`):
  Immutable genetic code objects with pre-computed hashes; unchanged in behaviour after these
  work packages.
- **MutableConcrete** (`CGraph`, `Interface`, `EndPoint`, `EPRef`, `EPRefs`, `EGCDict`):
  Mutable genetic code objects that are explicitly non-hashable (`__hash__ = None` on their
  ABCs). Any code that needs a stable hash must use the frozen equivalent or an explicit
  `compute_hash()` helper.
- **GGCDict**: Persisted genetic code record; transitions from a two-phase (mutable then
  locked) design to a single-phase (constructed fully immutable) design.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All baseline unit tests pass after each work package is applied — zero test
  regressions.
- **SC-002**: Zero `super-init-not-called` or `non-parent-init-called` pylint-disable
  comments remain in the four affected mutable class files after WP4.
- **SC-003**: All six mutable genetic code classes raise `TypeError` on any `hash()` call
  after WP5, enforced by `__hash__ = None` on their ABCs and verified by dedicated unit
  tests. Zero call sites in the codebase hash a mutable object after the audit.
- **SC-004**: `GGCDict` construction requires a single call with all required fields — no
  two-step `set_members()` pattern remains anywhere in the codebase after WP6.
- **SC-005**: New unit tests achieve at least 90% branch coverage over the changed code paths
  in each work package.
- **SC-006**: No new pylint or pyright warnings are introduced by any work package.

## Out of Scope

- **WP7 — Diamond Inheritance Simplification**: The diamond inheritance pattern across
  `CGraph`, `Interface`, `EndPoint`, and `EPRefs` class families is a maintainability concern
  only — Python's MRO resolves it correctly at runtime. It is deferred to a dedicated
  follow-up branch to avoid compounding risk with WP4–WP6 changes.

## Assumptions

- WP2 (CommonObj/CommonObjABC Unification) is already merged and is part of the current
  baseline. No cherry-pick or branch dependency is required before starting WP4.
- Mutable ABCs will have `__hash__ = None` set explicitly (Option B in WP5). Any existing
  call sites that hash mutable objects are bugs; they will be identified by audit and fixed
  rather than accommodated by a snapshot/finalisation mechanism.
- WP7 (Diamond Inheritance Simplification) is deferred to a dedicated follow-up branch;
  it is explicitly out of scope for this branch.
- The `egpseed` private repository is treated as an external consumer that must not break;
  any breaking changes to public APIs in the affected classes require corresponding updates
  there.
