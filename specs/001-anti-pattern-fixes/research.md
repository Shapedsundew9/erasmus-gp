# Phase 0 Research: Anti-Pattern Fixes (WP4-WP6)

## Decision 1: Split frozen initialization into attribute setup + hash caching (WP4)

- Decision: Refactor each frozen class initializer to separate pure attribute initialization
  from hash pre-computation, then have mutable subclasses call `super().__init__()` without
  bypassing parent initialization.
- Rationale: Current mutable classes suppress `super().__init__()` due to frozen hash caching;
  splitting concerns removes the need for suppression comments and duplicated setup logic.
- Alternatives considered:
  - Keep direct `CommonObj.__init__` calls in mutables: rejected because it preserves brittle
    duplication and bypassed MRO behavior.
  - Duplicate frozen setup logic in each mutable class: rejected due to maintenance risk.
- **Implementation delta**: Used Template Method pattern rather than `_init_attrs()` helper.
  Frozen classes expose `_cache_hash()` (endpoint/interface/ep_ref) and `_init_graph()`
  (c_graph) that mutable subclasses override. Frozen `__init__` args made optional with early
  returns for MRO safety when called by mutable subclasses via `super().__init__()`.

## Decision 2: Mutable objects must be non-hashable (WP5)

- Decision: Set `__hash__ = None` on mutable genetic-code ABCs and enforce `TypeError` for
  any `hash(mutable_obj)` usage.
- Rationale: Python hash contract forbids mutable hash keys; this prevents dict/set invariant
  breakage by construction.
- Alternatives considered:
  - Snapshot/freeze hashing on mutable objects: rejected as an anti-pattern accommodation and
    source of lifecycle complexity.
  - Keep current mutable `__hash__`: rejected as correctness risk.
- **Implementation delta**: `__hash__ = None` required on both ABCs AND concrete mutable
  classes due to MRO ordering — frozen parent's `__hash__` appears earlier in MRO than the
  ABC's `None`. No `compute_hash()` methods were needed; codebase audit found zero legitimate
  mutable-hash call sites in `egppy`, `egpdb`, or `egpdbmgr`.

## Decision 3: Mandatory mutable-hash usage audit (WP5)

- Decision: Perform codebase audit for mutable hash usage and refactor call sites to either
  hash frozen equivalents or use explicit `compute_hash()` helper semantics where required.
- Rationale: Removing hashability can surface latent coupling; explicit migration avoids hidden
  runtime failures.
- Alternatives considered:
  - Best-effort audit only in `egppy`: rejected due to cross-package consumers (`egpdb`,
    `egpdbmgr`, potential external usage).
- **Implementation delta**: Audit completed across all packages. No mutable-hash call sites
  found in `egpdb` or `egpdbmgr`. Eight existing tests that hashed mutable objects were
  updated to assert `TypeError` instead.

## Decision 4: Builder-based immutable GGCDict construction (WP6)

- Decision: Remove runtime `"immutable"` dict flag and two-step `set_members()` flow.
  `GGCDict` is created fully-formed in `__init__` from keyword arguments or completed
  `EGCDict` builder input.
- Rationale: Immediate immutability guarantees stable behavior and removes runtime mode flags.
- Alternatives considered:
  - `_frozen` attribute hardening: rejected as transitional complexity that still models
    mutability lifecycle within the same object.
- **Implementation delta**: Used `_frozen` attribute hardening (Option B from
  remaining_work_packages.md) rather than full builder removal. `GGCDict.__init__` calls
  `super().__init__(gcabc)` (which runs `set_members()` internally for data setup) then sets
  `object.__setattr__(self, "_frozen", True)`. The `"immutable"` dict key is removed.
  `__setitem__` checks `getattr(self, "_frozen", False)` and raises `TypeError`. This was
  simpler than restructuring the entire `set_members()` pipeline and achieved the same
  immutability guarantee. `EGCDict` references were updated to use
  `getattr(gc, "_frozen", False)` instead of `gc.get("immutable", False)`.

## Decision 5: Defer WP7 hierarchy simplification

- Decision: Keep WP7 out of scope for this branch; track in separate follow-up item.
- Rationale: WP7 is maintainability-only and high blast radius; WP4-WP6 are correctness-priority
  fixes with clearer boundaries.
- Alternatives considered:
  - Include WP7 now: rejected due to risk concentration in a single branch.

## Operational Best Practices Applied

- Use `unittest` only (`python -m unittest discover -s tests`).
- Ensure signed data artifacts exist before test runs via
  `.venv/bin/python egpcommon/egpcommon/manage_github_data.py download`.
- Keep edits narrowly scoped to specified files and required call-site migrations.
- Preserve explicit imports, pyright compatibility, and black/isort formatting constraints.
