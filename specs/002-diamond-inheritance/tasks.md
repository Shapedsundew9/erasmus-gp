# Tasks: Diamond Inheritance Documentation & MRO Safety Tests

**Input**: Design documents from `/specs/002-diamond-inheritance/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are required for this feature because the specification explicitly requires a new MRO/subclass regression test module (`FR-004`, `FR-005`, `FR-006`).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., [US1], [US2])
- Every task includes exact file path(s)

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create initial artifacts and scaffolding for documentation and test work.

- [x] T001 Create architecture document stub with top-level sections in `docs/components/worker/diamond_inheritance.md`
- [x] T002 Create regression test module scaffold in `tests/test_egppy/test_genetic_code/test_mro_diamond.py`
- [x] T003 [P] Add feature-task cross-reference note in `specs/002-diamond-inheritance/contracts/mro-documentation-contract.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define shared baselines that all user stories depend on.

**⚠️ CRITICAL**: No user story work should begin until this phase is complete.

- [x] T004 Define canonical family/diamond inventory table (4 families, 5 diamonds, 20 classes) in `docs/components/worker/diamond_inheritance.md`
- [x] T005 Define shared class import map and expected-MRO fixture data in `tests/test_egppy/test_genetic_code/test_mro_diamond.py`
- [x] T006 Implement shared assertion helper that prints expected vs actual MRO clearly in `tests/test_egppy/test_genetic_code/test_mro_diamond.py`

**Checkpoint**: Foundation is ready; user story tasks can begin.

---

## Phase 3: User Story 1 - Developer Understands Class Hierarchy (Priority: P1) 🎯 MVP

**Goal**: Make hierarchy intent obvious from class docstrings and architecture overview documentation.

**Independent Test**: Review updated class docstrings plus architecture overview and verify each class role and parent chain is explicitly documented.

### Tests for User Story 1

- [x] T007 [US1] Add docstring coverage tests for hierarchy-role, parent metadata, and Google-style class-docstring requirements across all target classes in `tests/test_egppy/test_genetic_code/test_mro_diamond.py`

### Implementation for User Story 1

- [x] T008 [P] [US1] Update CGraph family class docstrings in `egppy/egppy/genetic_code/c_graph_abc.py`, `egppy/egppy/genetic_code/frozen_c_graph.py`, `egppy/egppy/genetic_code/c_graph.py`
- [x] T009 [P] [US1] Update Interface family class docstrings in `egppy/egppy/genetic_code/interface_abc.py`, `egppy/egppy/genetic_code/frozen_interface.py`, `egppy/egppy/genetic_code/interface.py`
- [x] T010 [P] [US1] Update EndPoint family class docstrings in `egppy/egppy/genetic_code/endpoint_abc.py`, `egppy/egppy/genetic_code/frozen_endpoint.py`, `egppy/egppy/genetic_code/endpoint.py`
- [x] T011 [P] [US1] Update EPRef/EPRefs family class docstrings in `egppy/egppy/genetic_code/ep_ref_abc.py`, `egppy/egppy/genetic_code/frozen_ep_ref.py`, `egppy/egppy/genetic_code/ep_ref.py`
- [x] T012 [US1] Write architecture overview, rationale, and family/diamond diagrams in `docs/components/worker/diamond_inheritance.md`

**Checkpoint**: User Story 1 is independently complete and reviewable.

---

## Phase 4: User Story 2 - MRO Regression Protection (Priority: P1)

**Goal**: Guarantee accidental parent-order changes are caught by exact-MRO tests.

**Independent Test**: Run only `test_mro_diamond.py`; exact-MRO tests pass on baseline and fail on deliberate parent-reorder mutation.

### Tests for User Story 2

- [x] T013 [US2] Add exact-MRO assertions for `CGraph` and `Interface` diamonds in `tests/test_egppy/test_genetic_code/test_mro_diamond.py`
- [x] T014 [US2] Add exact-MRO assertions for `EndPoint`, `EPRef`, and `EPRefs` diamonds in `tests/test_egppy/test_genetic_code/test_mro_diamond.py`
- [x] T015 [US2] Add failure-message assertions/format checks for expected-vs-actual MRO output in `tests/test_egppy/test_genetic_code/test_mro_diamond.py`

### Implementation for User Story 2

- [x] T016 [US2] Document full canonical MRO listings for all five diamonds in `docs/components/worker/diamond_inheritance.md`
- [x] T017 [US2] Add MRO-regression demonstration instructions (intentional reorder experiment and revert guidance) in `docs/components/worker/diamond_inheritance.md`

**Checkpoint**: User Story 2 is independently complete and executable.

---

## Phase 5: User Story 3 - Subclass Contract Verification (Priority: P2)

**Goal**: Preserve key subclass invariants used by runtime and persistence code.

**Independent Test**: Run only subclass-contract tests in `test_mro_diamond.py` and verify positive/negative `issubclass` expectations.

### Tests for User Story 3

- [x] T018 [US3] Add positive subclass-contract tests (`mutable concrete` is subclass of `frozen ABC` and `mutable ABC`) in `tests/test_egppy/test_genetic_code/test_mro_diamond.py`
- [x] T019 [US3] Add negative subclass-contract tests (`frozen concrete` is not subclass of `mutable ABC`) in `tests/test_egppy/test_genetic_code/test_mro_diamond.py`

### Implementation for User Story 3

- [x] T020 [US3] Document subclass-contract intent and risk notes for all families in `docs/components/worker/diamond_inheritance.md`

**Checkpoint**: User Story 3 is independently complete and executable.

---

## Phase 6: User Story 4 - Init Pattern Documentation (Priority: P2)

**Goal**: Document the three init patterns and contributor guidance for adding new class pairs safely.

**Independent Test**: Validate architecture document includes all three init patterns mapped to families and provides a contributor playbook.

### Tests for User Story 4

- [x] T021 [US4] Add architecture-doc content tests for required init-pattern sections in `tests/test_egppy/test_genetic_code/test_mro_diamond.py`

### Implementation for User Story 4

- [x] T022 [US4] Document optional-args-with-early-return, separated-hash-computation, and template-method-with-override patterns in `docs/components/worker/diamond_inheritance.md`
- [x] T023 [US4] Add contributor playbook for adding a new frozen/mutable pair in `docs/components/worker/diamond_inheritance.md`

**Checkpoint**: User Story 4 is independently complete and reviewable.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency checks and validation across all stories.

- [x] T024 [P] Align feature contract wording with finalized tests/docs in `specs/002-diamond-inheritance/contracts/mro-documentation-contract.md`
- [x] T025 [P] Update end-to-end validation commands and completion criteria in `specs/002-diamond-inheritance/quickstart.md`
- [x] T026 Run focused MRO regression tests in `tests/test_egppy/test_genetic_code/test_mro_diamond.py` using `python -m unittest tests/test_egppy/test_genetic_code/test_mro_diamond.py`
- [x] T027 Run existing mutability contract tests in `tests/test_egppy/test_genetic_code/test_mutability_contract.py` using `python -m unittest tests/test_egppy/test_genetic_code/test_mutability_contract.py`
- [x] T028 Run full baseline suite with `python -m unittest discover -s tests` and capture pass/fail summary in `specs/002-diamond-inheritance/quickstart.md`
- [x] T029 [P] Validate quickstart expected outcomes/commands remain accurate in `specs/002-diamond-inheritance/quickstart.md`
- [x] T030 [P] Record final requirement-quality review outcomes in `specs/002-diamond-inheritance/checklists/inheritance.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup completion; blocks all user stories.
- **User Stories (Phase 3-6)**: Depend on Foundational completion.
- **Polish (Phase 7)**: Depends on selected user stories being complete.

### User Story Dependencies

- **US1 (P1)**: Can start immediately after Phase 2; no dependency on other stories.
- **US2 (P1)**: Can start immediately after Phase 2; independent from US1 except shared fixtures.
- **US3 (P2)**: Can start immediately after Phase 2; no dependency on other stories.
- **US4 (P2)**: Can start immediately after Phase 2; no dependency on other stories.

### User Story Dependency Graph

```text
Foundational (Phase 2)
  |- US1 (Phase 3)
  |- US2 (Phase 4)
  |- US3 (Phase 5)
  `- US4 (Phase 6)
```

### Within Each User Story

- Test task(s) are created before implementation tasks in that story.
- Documentation/test artifacts must remain behavior-preserving for production code.
- Story checkpoint must pass before story is marked done.

### Parallel Opportunities

- `T003` can run in parallel with `T001`/`T002`.
- In US1, `T008`, `T009`, `T010`, and `T011` can run in parallel by family.
- In Polish, `T024`, `T025`, `T029`, and `T030` can run in parallel after test execution tasks.

---

## Parallel Example: User Story 1

```bash
# Parallel family-level docstring updates (different files):
Task: T008 in egppy/egppy/genetic_code/c_graph_abc.py, egppy/egppy/genetic_code/frozen_c_graph.py, egppy/egppy/genetic_code/c_graph.py
Task: T009 in egppy/egppy/genetic_code/interface_abc.py, egppy/egppy/genetic_code/frozen_interface.py, egppy/egppy/genetic_code/interface.py
Task: T010 in egppy/egppy/genetic_code/endpoint_abc.py, egppy/egppy/genetic_code/frozen_endpoint.py, egppy/egppy/genetic_code/endpoint.py
Task: T011 in egppy/egppy/genetic_code/ep_ref_abc.py, egppy/egppy/genetic_code/frozen_ep_ref.py, egppy/egppy/genetic_code/ep_ref.py
```

---

## Parallel Example: User Story 2

```bash
# No safe [P] tasks inside US2 because tasks share files.
# Parallelization option is cross-story after Phase 2:
Task: US2 sequence (T013-T017) by Developer A
Task: US1 sequence (T007-T012) by Developer B
```

---

## Parallel Example: User Story 3

```bash
# No safe [P] tasks inside US3 because tasks share files.
# Parallelization option is cross-story after Phase 2:
Task: US3 sequence (T018-T020) by Developer A
Task: US4 sequence (T021-T023) by Developer B
```

---

## Parallel Example: User Story 4

```bash
# No safe [P] tasks inside US4 because tasks share files.
# Parallelization option is cross-story after Phase 2:
Task: US4 sequence (T021-T023) by Developer A
Task: Polish tasks T024/T025/T029/T030 by Developer B when story outputs are ready
```

---

## Implementation Strategy

### MVP First (User Story 1)

1. Complete Phase 1 (Setup).
2. Complete Phase 2 (Foundational).
3. Complete Phase 3 (US1).
4. Validate US1 independently via docstring coverage tests and architecture review.

### Incremental Delivery

1. Deliver US1 (documentation clarity baseline).
2. Deliver US2 (exact-MRO regression safety).
3. Deliver US3 (subclass contract safety).
4. Deliver US4 (init-pattern guidance).
5. Finish with Phase 7 polish and full test run validation.

### Parallel Team Strategy

1. One developer owns shared test module scaffolding (Phase 1-2).
2. Family documentation tasks (US1) split by domain owner in parallel.
3. Test-hardening (US2/US3) and architecture deep-dive docs (US4) proceed in staggered overlap.

---

## Notes

- `[P]` tasks are safe to run in parallel because they target separate files or sections.
- Story labels (`[US1]` to `[US4]`) maintain traceability back to spec priorities.
- No task changes production runtime behavior; all work is documentation/tests only.
