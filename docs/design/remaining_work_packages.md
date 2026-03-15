# Remaining Work Packages: Class Hierarchy Anti-Patterns

This document describes work packages WP4–WP7 for resolving class hierarchy
anti-patterns in Erasmus GP. WP1–WP3 have been completed on sub-branches off
`container-type-expansion`.

| WP | Status | Branch |
|----|--------|--------|
| WP1 — ABC Method De-duplication | **Merged** | `wp1-abc-method-dedup` |
| WP2 — CommonObj/CommonObjABC Unification | **Complete (unmerged)** | `wp2-commonobj-unification` |
| WP3 — GCABC Protocol Conformance | **Complete (unmerged)** | `wp3-gcabc-protocol` |
| WP4 — Suppressed `super().__init__()` | **Complete (unmerged)** | `001-anti-pattern-fixes` |
| WP5 — Hashable Mutable Objects | **Complete (unmerged)** | `001-anti-pattern-fixes` |
| WP6 — Runtime Immutability Flag | **Complete (unmerged)** | `001-anti-pattern-fixes` |
| WP7 — Diamond Inheritance Simplification | Not started | — |

---

## Global Constraints

These constraints apply to **every** work package.

1. **Baseline tests must pass.** Run `python -m unittest discover -s tests`
   from `/workspaces/erasmus-gp/` with the `.venv` activated. Do **not** use
   `pytest` (it miscounts failures).
2. **Data files must exist.** Before running tests, ensure
   `egppy/egppy/data/codons.json`, `types_def.json`, and their `.sig` files
   are present. If not, run:

   ```bash
   .venv/bin/python egpcommon/egpcommon/manage_github_data.py download
   ```

3. **No unrelated changes.** Each WP must touch only the files and patterns
   described. Formatter-only changes (black, isort) are acceptable.
4. **New tests required.** Every change must have unit tests confirming the
   new behaviour. Tests go under `tests/test_egppy/` mirroring the source
   structure (e.g. `tests/test_egppy/test_genetic_code/test_c_graph.py`).

---

## WP4 — Suppressed `super().__init__()` Calls

### Problem

Four mutable concrete classes explicitly bypass `super().__init__()` and
instead call `CommonObj.__init__(self)` directly, suppressing the frozen
parent's initialisation logic with pylint `super-init-not-called` disables:

| Class | File | Line | Bypassed Parent |
|-------|------|------|-----------------|
| `CGraph` | `egppy/genetic_code/c_graph.py` | ~54 | `FrozenCGraph.__init__` |
| `Interface` | `egppy/genetic_code/interface.py` | ~84 | `FrozenInterface.__init__` |
| `EndPoint` | `egppy/genetic_code/endpoint.py` | ~72 | `FrozenEndPoint.__init__` |
| `EPRefs` | `egppy/genetic_code/ep_ref.py` | ~31 | `FrozenEPRefs.__init__` |

Each of these classes duplicates setup logic that the frozen parent already
performs (e.g. attribute initialisation, hash pre-computation), and then
overrides or ignores parts of it.

### Root Cause

The frozen `__init__` pre-computes a hash and stores it in `_hash`, which is
inappropriate for a mutable instance whose hash will change after mutation.
Because calling `super().__init__()` would pre-compute an invalid hash, the
mutable child skips it entirely and manually re-initialises attributes.

### Goal

Refactor frozen `__init__` so that the common attribute setup is separated from
hash pre-computation. This allows mutable children to call `super().__init__()`
normally while opting out of hash caching.

### Implementation Plan

1. **Extract a `_init_attrs(...)` helper** (or similar) in each frozen class
   that sets up all attributes _except_ `_hash`. Have the frozen `__init__`
   call `_init_attrs()` followed by hash computation.
2. **In mutable `__init__`**, call `super().__init__()` which now correctly
   initialises attributes via `_init_attrs()`. Override or skip the hash
   caching step (mutable classes compute hash dynamically anyway).
3. **Remove all `# pylint: disable=super-init-not-called`** and
   `# pylint: disable=non-parent-init-called` comments.
4. **Verify** that frozen classes still pre-compute hashes, and mutable classes
   still compute hashes dynamically.

### Files to Modify

| File | Change |
|------|--------|
| `egppy/genetic_code/frozen_c_graph.py` | Extract `_init_attrs`, restructure `__init__` |
| `egppy/genetic_code/c_graph.py` | Call `super().__init__()`, remove pylint disables |
| `egppy/genetic_code/frozen_interface.py` | Extract `_init_attrs`, restructure `__init__` |
| `egppy/genetic_code/interface.py` | Call `super().__init__()`, remove pylint disables |
| `egppy/genetic_code/frozen_endpoint.py` | Extract `_init_attrs`, restructure `__init__` |
| `egppy/genetic_code/endpoint.py` | Call `super().__init__()`, remove pylint disables |
| `egppy/genetic_code/frozen_ep_ref.py` | Extract `_init_attrs`, restructure `__init__` |
| `egppy/genetic_code/ep_ref.py` | Call `super().__init__()`, remove pylint disables |

### Test Strategy

- Verify `super().__init__()` is called (no pylint disables remain).
- Verify frozen instances still have pre-computed `_hash` after construction.
- Verify mutable instances still compute `__hash__()` dynamically.
- Verify all attributes are correctly initialised in both frozen and mutable
  instances after construction.

### Dependencies

- **Depends on WP2** (CommonObj inherits CommonObjABC — merged or on branch).
- No dependency on WP3.

### Risks

- The frozen `__init__` may perform validation that the mutable class doesn't
  want (e.g. type-checking inputs as tuples vs. lists). Must ensure
  `_init_attrs` accepts the mutable forms where applicable.
- `FrozenCGraph.__init__` constructs `FrozenInterface` objects from its inputs;
  `CGraph.__init__` needs `Interface` objects. The helper must be flexible
  enough or the mutable class must override the relevant part.

---

## WP5 — Hashable Mutable Objects

### Problem

Six mutable classes define `__hash__()` despite being mutable, violating
Python's guideline that mutable objects should not be hashable (since their
hash changes after mutation, breaking dict/set invariants):

| Class | File | Hash Impl | Mutation Methods |
|-------|------|-----------|-----------------|
| `CGraph` | `c_graph.py:118` | Hash of interfaces | `__setitem__`, `connect_all`, `disconnect_all` |
| `Interface` | `interface.py:251` | `hash(tuple(hash(ep) for ep in self.endpoints))` | `append`, `extend`, `insert`, `__setitem__`, `__delitem__` |
| `EndPoint` | `endpoint.py:119` | `hash((row, idx, cls, typ, refs))` | `connect`, `clr_refs`, `ref_shift`, `set_ref` |
| `EPRef` | `ep_ref.py:15` | `hash((row, idx))` | Inherited, limited |
| `EPRefs` | `ep_ref.py:46` | `hash(tuple(self._refs))` | `append`, `insert`, `__setitem__`, `__delitem__`, `clear` |
| `EGCDict` | `egc_dict.py:160` | XOR of gca, gcb, cgraph hashes | `__setitem__` via CacheableDict |

### Root Cause

The frozen ABCs inherit `Hashable` (e.g. `FrozenEndPointABC(CommonObjABC,
Hashable)`), and the mutable ABCs extend the frozen ABCs. The mutable concrete
classes therefore inherit the `Hashable` contract but can mutate their state,
causing hash values to change after construction.

### Why Hashing Exists on Mutables

In the Erasmus GP evolutionary loop, mutable genetic code structures are built
up and then **hashed for de-duplication and lookup** before being persisted.
The hash is computed at a snapshot point when the object is considered
"complete". This is a deliberate design trade-off, not an accident.

### Goal

Make the hashing contract explicit and safe. Two possible approaches (decide
during implementation based on codebase impact):

**Option A — Snapshot Hashing (Preferred)**

Keep `__hash__` on mutable classes but make it opt-in and explicit. Add a
`freeze()` or `snapshot_hash()` method that captures the hash at a point in
time, and have `__hash__` return that captured value. Raise `TypeError` if
`__hash__` is called before `freeze()`.

**Option B — Remove `__hash__` from Mutables**

Set `__hash__ = None` on all mutable ABCs (`CGraphABC`, `InterfaceABC`,
`EndPointABC`, `EPRefABC`, `EPRefsABC`). Provide explicit `compute_hash()`
methods for de-duplication use cases that return an `int` without making the
object act as a dict key.

### Implementation Notes

- **Option A** is lower-risk because existing call sites that use
  `hash(mutable_obj)` will continue to work after calling `freeze()`.
- **Option B** is cleaner from a Python perspective but requires auditing
  every call site that hashes a mutable object.
- Whichever option is chosen, `FrozenCGraph`, `FrozenInterface`,
  `FrozenEndPoint`, `FrozenEPRef`, and `FrozenEPRefs` keep their
  pre-computed `__hash__` unchanged.

### Files to Modify

| File | Change |
|------|--------|
| `egppy/genetic_code/c_graph_abc.py` | Add hash contract to mutable ABC |
| `egppy/genetic_code/c_graph.py` | Implement chosen hash strategy |
| `egppy/genetic_code/interface_abc.py` | Add hash contract to mutable ABC |
| `egppy/genetic_code/interface.py` | Implement chosen hash strategy |
| `egppy/genetic_code/endpoint_abc.py` | Add hash contract to mutable ABC |
| `egppy/genetic_code/endpoint.py` | Implement chosen hash strategy |
| `egppy/genetic_code/ep_ref_abc.py` | Add hash contract to mutable ABCs |
| `egppy/genetic_code/ep_ref.py` | Implement chosen hash strategy |
| `egppy/genetic_code/egc_dict.py` | Implement chosen hash strategy |

### Files to Audit for Hash Usage

Search for `hash(` calls on mutable instances across the codebase. Key areas:

- `egppy/gene_pool/` — gene pool lookups
- `egppy/genetic_code/` — de-duplication logic
- `egppy/storage/` — cache key computation
- `egppy/physics/` — evolved code execution

### Test Strategy

- Verify frozen objects remain hashable and stable across mutations (they
  should not be mutable).
- Verify mutable objects either: (A) raise `TypeError` on `hash()` before
  `freeze()` and return stable hash after, or (B) raise `TypeError` on
  `hash()` always.
- Verify `compute_hash()` / `snapshot_hash()` returns the expected value.
- Verify existing de-duplication and lookup logic still works.

### Dependencies

- **Should follow WP4** (init refactoring may affect hash computation setup).
- Independent of WP6.

### Risks

- High impact: many call sites may use `hash()` on mutable objects. Must audit
  comprehensively before choosing an approach.
- May require changes in `egpdb` and `egpdbmgr` if they hash mutable GC
  objects.

---

## WP6 — Runtime Immutability Flag (GGCDict)

### Problem

`GGCDict` (Genomic Genetic Code Dict) uses a runtime `"immutable"` flag stored
as a dictionary key to toggle mutability after construction:

```python
# ggc_dict.py
class GGCDict(EGCDict):
    def __setitem__(self, key, value):
        if self.get("immutable", False):
            raise RuntimeError("GGCDict is immutable")
        super().__setitem__(key, value)

    def set_members(self, ...):
        ...  # set all fields
        self["immutable"] = True  # lock after setup
```

This pattern violates the Hashable contract: the object is mutable during
construction, becomes "immutable" at runtime, and defines `__hash__` throughout.
Any use as a dict key or set member before `set_members()` completes is unsafe.

### Current Inheritance Chain

```text
CommonObjABC → StorableObjABC → CacheableObjABC → GCABC
                                                    ↓
MutableMapping + CacheableObjMixin + CommonObj → CacheableDict
                                                    ↓
                                                 EGCDict
                                                    ↓
                                                 GGCDict
```

### Goal

Replace the runtime immutability flag with a proper frozen/mutable pair pattern
that matches the rest of the codebase, or use a builder pattern where GGCDict
is constructed immutable from the start.

### Implementation Plan

**Option A — Builder Pattern (Preferred)**

1. Create a `GGCDictBuilder` (or use `EGCDict` directly as the mutable
   builder) that accumulates all fields.
2. `GGCDict` becomes a true frozen class: its `__init__` accepts a completed
   `EGCDict` or keyword arguments, validates, and stores all fields immutably.
3. `GGCDict.__setitem__` raises `TypeError` unconditionally (or is not
   defined at all if it inherits from a frozen base).
4. Remove the `"immutable"` key from the dictionary entirely.

**Option B — Flag Hardening**

1. Move the immutability check into `__init__` so `GGCDict` is always
   constructed immutable (all fields passed to `__init__`).
2. Replace the `"immutable"` dict key with a proper `__slots__`-based
   `_frozen: bool` attribute.
3. Guard `__setitem__`, `__delitem__`, and `update` against mutation when
   `_frozen` is `True`.

### Files to Modify

| File | Change |
|------|--------|
| `egppy/genetic_code/ggc_dict.py` | Rewrite to use builder or proper frozen pattern |
| `egppy/genetic_code/egc_dict.py` | May need adjustments to support builder |
| All files calling `GGCDict(...)` or `ggc.set_members(...)` | Update construction pattern |

### Files to Audit for `GGCDict` Usage

```bash
grep -rn "GGCDict\|ggc_dict\|set_members" egppy/ egpdb/ egpdbmgr/ tests/
```

### Test Strategy

- Verify `GGCDict` is immutable after construction (no `set_members` call
  needed).
- Verify `__hash__` is stable from construction.
- Verify `__setitem__` raises `TypeError` (not `RuntimeError`).
- Verify the `"immutable"` key no longer exists in the dict.
- Verify all existing tests that create `GGCDict` objects still pass with the
  new construction pattern.

### Dependencies

- **Depends on WP5** (hash strategy for mutable objects must be decided first,
  since GGCDict's hash behaviour depends on whether EGCDict is hashable).
- Independent of WP4.

### Risks

- `GGCDict` is used throughout the persistence layer (`egpdb`, `egpdbmgr`).
  The construction pattern change may have wide impact.
- The `set_members()` API is likely called from multiple places. Must find and
  update all call sites.

---

## WP7 — Diamond Inheritance Simplification

### Problem

The Frozen/Mutable concrete class pairs use a diamond inheritance pattern where
the mutable concrete class inherits from **both** the frozen concrete class and
the mutable ABC, which both share a common frozen ABC grandparent:

```text
        FrozenFooABC
       /            \
      /              \
FrozenFoo          FooABC
      \              /
       \            /
          Foo
```

This pattern exists in four class families:

| Mutable Class | Parents | Shared Grandparent |
|---------------|---------|-------------------|
| `CGraph` | `FrozenCGraph`, `CGraphABC` | `FrozenCGraphABC` |
| `Interface` | `CommonObj`, `FrozenInterface`, `InterfaceABC` | `FrozenInterfaceABC` |
| `EndPoint` | `FrozenEndPoint`, `EndPointABC` | `FrozenEndPointABC` |
| `EPRefs` | `FrozenEPRefs`, `EPRefsABC` | `FrozenEPRefsABC` |

### Why This Exists

The diamond arises because:

1. The mutable class needs the **implementation** from the frozen concrete class
   (attribute storage, `__slots__`, common methods).
2. The mutable class needs the **interface** from the mutable ABC (mutation
   method declarations).
3. Both the frozen concrete and mutable ABC inherit from the frozen ABC.

Python's MRO (C3 linearisation) handles this correctly — there is no runtime
error. However, it makes the hierarchy brittle and hard to understand.

### Why This Is Low Priority

Unlike WP4–WP6, this anti-pattern does **not** cause runtime bugs. Python's
MRO resolves the diamond correctly. The issue is purely about maintainability
and comprehensibility. This WP is therefore optional and may be deferred.

### Goal

Reduce the class explosion from 4 classes per concept (FrozenABC, FrozenConcrete,
MutableABC, MutableConcrete) to 3 or fewer where possible. The preferred
approach is to merge the frozen concrete class into the frozen ABC (making the
ABC non-abstract), or to use composition instead of inheritance for the
frozen→mutable relationship.

### Implementation Plan

**Option A — Merge Frozen Concrete into Frozen ABC**

For each family, if the frozen ABC has only one concrete implementation
(FrozenFoo), merge FrozenFoo's implementation into FrozenFooABC (making it
a concrete class that can still be subclassed). This eliminates one class per
family.

**Option B — Composition over Inheritance**

Instead of `Foo(FrozenFoo, FooABC)`, make `Foo(FooABC)` and have it hold a
`FrozenFoo` internally for delegation. This breaks the diamond but adds
delegation boilerplate.

**Option C — Leave as-is with Documentation**

Document the diamond pattern explicitly in docstrings and architecture docs.
Add MRO tests to prevent accidental breakage.

### Files to Modify (if Option A)

| File | Change |
|------|--------|
| `egppy/genetic_code/c_graph_abc.py` | Merge FrozenCGraph implementation |
| `egppy/genetic_code/frozen_c_graph.py` | Remove or repurpose |
| `egppy/genetic_code/interface_abc.py` | Merge FrozenInterface implementation |
| `egppy/genetic_code/frozen_interface.py` | Remove or repurpose |
| `egppy/genetic_code/endpoint_abc.py` | Merge FrozenEndPoint implementation |
| `egppy/genetic_code/frozen_endpoint.py` | Remove or repurpose |
| `egppy/genetic_code/ep_ref_abc.py` | Merge FrozenEPRef/FrozenEPRefs implementation |
| `egppy/genetic_code/frozen_ep_ref.py` | Remove or repurpose |
| All importing files | Update imports |

### Test Strategy

- Verify MRO is correct for all classes (`assert issubclass(Foo, FrozenFooABC)`).
- Verify all existing tests pass without modification (API unchanged).
- Verify frozen instances are still immutable.
- Verify mutable instances still have full mutation API.

### Dependencies

- **Should follow WP4, WP5, WP6.** Restructuring the diamond is easiest after
  init calls and hashing are cleaned up.
- This is the highest-risk, highest-reward WP and should be done last.

### Risks

- Large number of files affected (8+ source files, all their importers).
- May break `isinstance` checks if classes are merged.
- `__slots__` must be carefully managed when merging classes.
- Option A changes the semantic meaning of the ABC (no longer abstract).
- External packages (`egpdb`, `egpdbmgr`, `egpseed`) may import frozen classes
  directly — all must be audited.

---

## Suggested Execution Order

```text
WP4 (super().__init__) → WP5 (hashable mutables) → WP6 (GGCDict) → WP7 (diamond)
```

- **WP4 first**: Cleaning up init calls is foundational and enables WP5.
- **WP5 before WP6**: The hash strategy decision affects how GGCDict is
  redesigned.
- **WP7 last**: Structural simplification is safest after behavioral fixes.

Each WP should be implemented on its own sub-branch off `container-type-expansion`
and reviewed before merging.
