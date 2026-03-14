# Tasks: Anti-Pattern Fixes for Genetic Code Class Hierarchy (WP4-WP6)

**Input**: Design documents from `/specs/001-anti-pattern-fixes/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/genetic-code-mutability-contract.md, quickstart.md

**Tests**: New unit tests are required by the specification (FR-012).

**Organization**: Tasks are grouped by user story to keep each story independently verifiable.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Ensure local baseline and deterministic test environment before refactors

- [X] T001 Verify baseline test environment and required data artifacts using `.venv/bin/python egpcommon/egpcommon/manage_github_data.py download` in `egpcommon/egpcommon/manage_github_data.py`
- [X] T002 Run baseline suite `python -m unittest discover -s tests` and record failures to compare regressions in `tests/`
- [X] T003 [P] Capture current mutable-hash and GGCDict call-site inventory using search over `egppy/**/*.py`, `egpdb/**/*.py`, `egpdbmgr/**/*.py`, and `tests/**/*.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared scaffolding required by all user stories

**CRITICAL**: No user-story implementation begins until these tasks complete.

- [X] T004 Add shared constructor/hash behavior regression tests scaffold in `tests/test_egppy/test_genetic_code/test_mutability_contract.py`
- [X] T005 [P] Add shared GGCDict construction/mutation regression tests scaffold in `tests/test_egppy/test_genetic_code/test_ggc_dict.py`
- [X] T006 Define helper fixtures/builders for mutable/frozen sample objects in `tests/test_egppy/test_genetic_code/__init__.py`
- [X] T007 [P] Add targeted test-discovery pattern command notes for this feature in `specs/001-anti-pattern-fixes/quickstart.md` (FR-015 governance documentation compliance)

**Checkpoint**: Foundation ready. User story implementation can proceed.

---

## Phase 3: User Story 1 - Predictable Object Construction (Priority: P1) 🎯 MVP

**Goal**: Remove suppressed parent initialization anti-pattern and preserve frozen/mutable semantics

**Independent Test**: Construct `CGraph`, `Interface`, `EndPoint`, and `EPRefs`; verify full init path behavior and hash setup invariants.

### Tests for User Story 1

- [X] T008 [P] [US1] Add constructor chain behavior tests for `CGraph` and `FrozenCGraph` in `tests/test_egppy/test_genetic_code/test_c_graph.py`
- [X] T009 [P] [US1] Add constructor chain behavior tests for `Interface` and `FrozenInterface` in `tests/test_egppy/test_genetic_code/test_interface.py`
- [X] T010 [P] [US1] Add constructor chain behavior tests for `EndPoint` and `FrozenEndPoint` in `tests/test_egppy/test_genetic_code/test_endpoint.py`
- [X] T011 [P] [US1] Add constructor chain behavior tests for `EPRef`/`EPRefs` and frozen counterparts in `tests/test_egppy/test_genetic_code/test_ep_ref.py`

### Implementation for User Story 1

- [X] T012 [US1] Refactor frozen c-graph initialization to split attribute setup from hash caching in `egppy/egppy/genetic_code/frozen_c_graph.py`
- [X] T013 [US1] Update mutable c-graph to call `super().__init__()` and remove init-bypass disables in `egppy/egppy/genetic_code/c_graph.py`
- [X] T014 [US1] Refactor frozen interface initialization to split attribute setup from hash caching in `egppy/egppy/genetic_code/frozen_interface.py`
- [X] T015 [US1] Update mutable interface to call `super().__init__()` and remove init-bypass disables in `egppy/egppy/genetic_code/interface.py`
- [X] T016 [US1] Refactor frozen endpoint initialization to split attribute setup from hash caching in `egppy/egppy/genetic_code/frozen_endpoint.py`
- [X] T017 [US1] Update mutable endpoint to call `super().__init__()` and remove init-bypass disables in `egppy/egppy/genetic_code/endpoint.py`
- [X] T018 [US1] Refactor frozen ep-ref initialization to split attribute setup from hash caching in `egppy/egppy/genetic_code/frozen_ep_ref.py`
- [X] T019 [US1] Update mutable ep-ref and ep-refs to call `super().__init__()` and remove init-bypass disables in `egppy/egppy/genetic_code/ep_ref.py`

**Checkpoint**: User Story 1 is independently testable and passes its targeted tests.

- [X] T043 [US1] Run full regression suite `python -m unittest discover -s tests` immediately after WP4 completion to satisfy per-work-package regression gating (FR-011)

---

## Phase 4: User Story 2 - Non-Hashable Mutable Objects (Priority: P2)

**Goal**: Enforce `__hash__ = None` on mutable contracts and remove mutable hashing usage

**Independent Test**: `hash()` on mutable instances raises `TypeError`; frozen hashes remain stable; mutable-hash call-site audit is clean.

### Tests for User Story 2

- [X] T020 [P] [US2] Add mutable hash `TypeError` tests for graph/interface/endpoint/ref classes in `tests/test_egppy/test_genetic_code/test_mutability_contract.py`
- [X] T021 [P] [US2] Add frozen hash stability regression tests in `tests/test_egppy/test_genetic_code/test_mutability_contract.py`
- [X] T022 [P] [US2] Add EGCDict mutable-hash prohibition tests in `tests/test_egppy/test_genetic_code/test_egc_dict.py`

### Implementation for User Story 2

- [X] T023 [US2] Set mutable hash contract (`__hash__ = None`) in c-graph ABC hierarchy in `egppy/egppy/genetic_code/c_graph_abc.py`
- [X] T024 [US2] Set mutable hash contract (`__hash__ = None`) in interface ABC hierarchy in `egppy/egppy/genetic_code/interface_abc.py`
- [X] T025 [US2] Set mutable hash contract (`__hash__ = None`) in endpoint ABC hierarchy in `egppy/egppy/genetic_code/endpoint_abc.py`
- [X] T026 [US2] Set mutable hash contract (`__hash__ = None`) in ep-ref ABC hierarchy in `egppy/egppy/genetic_code/ep_ref_abc.py`
- [X] T027 [US2] Remove mutable `__hash__` implementations and adjust behavior in `egppy/egppy/genetic_code/c_graph.py`, `egppy/egppy/genetic_code/interface.py`, `egppy/egppy/genetic_code/endpoint.py`, and `egppy/egppy/genetic_code/ep_ref.py`
- [X] T028 [US2] Remove/replace mutable hashing behavior in `EGCDict` in `egppy/egppy/genetic_code/egc_dict.py`
- [X] T029 [US2] Refactor mutable-hash call sites discovered in `egppy/**/*.py` to frozen/canonical hash pathways
- [X] T030 [US2] Refactor mutable-hash call sites discovered in `egpdb/**/*.py` and `egpdbmgr/**/*.py` to frozen/canonical hash pathways
- [X] T031 [US2] Update tests that hash mutable objects to new contract-compliant behavior in `tests/**/*.py`

**Checkpoint**: User Story 2 is independently testable and all mutable hash usage is eliminated.

- [X] T044 [US2] Run full regression suite `python -m unittest discover -s tests` immediately after WP5 completion to satisfy per-work-package regression gating (FR-011)

---

## Phase 5: User Story 3 - Atomic Immutable GGCDict Construction (Priority: P3)

**Goal**: Replace runtime immutability-flag lifecycle with immutable-by-construction `GGCDict`

**Independent Test**: Construct `GGCDict` in one step from kwargs or `EGCDict` builder; mutation methods raise `TypeError`; no `set_members()` flow remains.

### Tests for User Story 3

- [X] T032 [P] [US3] Add GGCDict one-step construction tests (kwargs and EGCDict builder) in `tests/test_egppy/test_genetic_code/test_ggc_dict.py`
- [X] T033 [P] [US3] Add GGCDict immutability mutation-failure tests in `tests/test_egppy/test_genetic_code/test_ggc_dict.py`
- [X] T034 [P] [US3] Add regression test proving no runtime `"immutable"` key lifecycle in `tests/test_egppy/test_genetic_code/test_ggc_dict.py`

### Implementation for User Story 3

- [X] T035 [US3] Refactor GGCDict constructor to immutable-by-construction and remove `set_members()` flow in `egppy/egppy/genetic_code/ggc_dict.py`
- [X] T036 [US3] Align EGCDict builder interoperability for GGCDict input validation in `egppy/egppy/genetic_code/egc_dict.py`
- [X] T037 [US3] Migrate GGCDict creation call sites from two-step flow in `egppy/**/*.py`
- [X] T038 [US3] Migrate GGCDict creation call sites from two-step flow in `egpdb/**/*.py` and `egpdbmgr/**/*.py`
- [X] T039 [US3] Migrate GGCDict creation call sites in `tests/**/*.py` and adjust expectations for `TypeError`

**Checkpoint**: User Story 3 is independently testable and legacy GGCDict runtime-flag behavior is removed.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification and documentation consistency across stories

- [X] T040 [P] Run focused genetic-code test suite for changed modules in `tests/test_egppy/test_genetic_code/`
- [X] T041 Run full regression suite `python -m unittest discover -s tests` from repository root in `tests/`
- [X] T042 [P] Update design docs to reflect final implementation deltas in `specs/001-anti-pattern-fixes/plan.md`, `specs/001-anti-pattern-fixes/research.md`, and `specs/001-anti-pattern-fixes/quickstart.md` (FR-015 governance documentation compliance)
- [X] T045 [P] Create and link the deferred WP7 follow-up work item in `docs/design/remaining_work_packages.md` and cross-reference it in `specs/001-anti-pattern-fixes/spec.md` (FR-014, FR-015)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: Starts immediately.
- **Phase 2 (Foundational)**: Depends on Phase 1 and blocks all user-story work.
- **Phase 3 (US1 / WP4)**: Depends on Phase 2.
- **Phase 4 (US2 / WP5)**: Depends on Phase 3 (per required WP order).
- **Phase 5 (US3 / WP6)**: Depends on Phase 4 (per required WP order).
- **Phase 6 (Polish)**: Depends on completion of US1-US3.
- **Regression gates**: T043 must pass before starting Phase 4; T044 must pass before starting Phase 5; T041 is the final post-WP6 full regression gate.

### User Story Dependencies

- **US1 (P1)**: Independent after foundational tasks; no dependency on other stories.
- **US2 (P2)**: Depends on US1 completion because WP5 follows WP4.
- **US3 (P3)**: Depends on US2 completion because WP6 follows WP5.

### Within Each User Story

- Tests first (write/adjust, confirm behavior gaps), then implementation, then migration fixes.
- ABC contracts before concrete implementations for hash behavior.
- Core class refactors before downstream call-site migrations.

### Parallel Opportunities

- Setup: T003 can run alongside T001/T002.
- Foundational: T005 and T007 parallelize with T004/T006.
- US1 tests: T008-T011 parallel.
- US2 tests: T020-T022 parallel.
- US3 tests: T032-T034 parallel.
- Polish: T040, T042, and T045 can run in parallel after implementation completes.

---

## Parallel Example: User Story 1

```bash
# Run US1 constructor test authoring in parallel:
T008, T009, T010, T011

# Then run frozen refactors in sequence with paired mutable updates:
T012 -> T013
T014 -> T015
T016 -> T017
T018 -> T019
```

## Parallel Example: User Story 2

```bash
# Parallel test work:
T020, T021, T022

# Parallel ABC contract updates:
T023, T024, T025, T026
```

## Parallel Example: User Story 3

```bash
# Parallel test work:
T032, T033, T034

# Migration updates by surface:
T037 (egppy) and T038 (egpdb/egpdbmgr) can run in parallel after T035/T036
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phases 1-2.
2. Deliver Phase 3 (US1 / WP4).
3. Validate constructor chain and hash-setup behavior with US1 tests.
4. Stop for review before expanding to hash-contract changes.

### Incremental Delivery

1. Deliver US1 (constructor correctness).
2. Deliver US2 (non-hashable mutable contracts + call-site cleanup).
3. Deliver US3 (GGCDict immutable construction).
4. Finish with cross-cutting regression runs and docs updates.

### Parallel Team Strategy

1. Shared work: Setup + Foundational.
2. During each story phase:
   - Engineer A: tests
   - Engineer B: core class/ABC changes
   - Engineer C: downstream migration call sites
3. Merge story-by-story in required WP order.

---

## Notes

- `[P]` indicates tasks that can be executed in parallel without file conflicts.
- `[USx]` labels trace each task back to a single user story.
- WP7 remains intentionally out of scope for this task list.
