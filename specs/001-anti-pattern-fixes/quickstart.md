# Quickstart: Implement WP4-WP6

## 1. Prepare environment

```bash
cd /workspaces/erasmus-gp
source .venv/bin/activate
.venv/bin/python egpcommon/egpcommon/manage_github_data.py download
```

## 2. Implement WP4 (super init refactor)

1. Update frozen classes (`frozen_c_graph.py`, `frozen_interface.py`,
   `frozen_endpoint.py`, `frozen_ep_ref.py`) to separate attribute setup from hash caching.
2. Update mutable classes (`c_graph.py`, `interface.py`, `endpoint.py`, `ep_ref.py`) to
   call `super().__init__()` and remove init-bypass pylint suppressions.
3. Add/adjust tests under `tests/test_egppy/test_genetic_code/` for constructor correctness
   and frozen-vs-mutable hash initialization behavior.

## 3. Implement WP5 (remove mutable hashability)

1. Update mutable ABC contracts (`c_graph_abc.py`, `interface_abc.py`, `endpoint_abc.py`,
   `ep_ref_abc.py`, plus mutable dict base as required) to enforce `__hash__ = None`.
2. Remove mutable `__hash__` implementations from concrete classes.
3. Audit call sites in:
   - `egppy/`
   - `egpdb/`
   - `egpdbmgr/`
   - `tests/`
4. Refactor any mutable-hash usage to frozen/canonical hash pathways.
5. Add tests ensuring `hash(mutable_obj)` raises `TypeError` and frozen objects remain hashable.

## 4. Implement WP6 (GGCDict builder + immutable construction)

1. Refactor `ggc_dict.py` to immutable single-step constructor.
2. Use `EGCDict` as builder input path for `GGCDict.__init__`.
3. Remove `set_members()` lifecycle and `"immutable"` dict key behavior.
4. Update all call sites constructing `GGCDict`.
5. Add tests verifying:
   - construction succeeds without `set_members()`
   - mutation raises `TypeError`
   - hash is stable and available from construction

## 5. Verification commands

```bash
cd /workspaces/erasmus-gp
source .venv/bin/activate
python -m unittest discover -s tests
```

Optional targeted runs during implementation:

```bash
python -m unittest discover -s tests -p "test_*genetic_code*.py"
```

## 6. Completion checklist

- [X] No `super-init-not-called` / `non-parent-init-called` suppression comments remain in WP4
  targets.
- [X] Mutable genetic-code classes are non-hashable by contract.
- [X] No mutable-hash call sites remain after audit.
- [X] `GGCDict` runtime immutability flag and two-step setup are removed.
- [X] Full test suite passes with no regressions.

## 7. Implementation results

| Metric | Value |
|--------|-------|
| Baseline tests | 1299 |
| After WP4 | 1308 (+9 constructor chain tests) |
| After WP5 | 1317 (+5 hash prohibition + 5 frozen stability - 2 removed) |
| After WP6 | 1322 (+5 GGCDict immutability tests) |
| Final regression | 1322 tests, all pass |

### Key implementation decisions

- **WP4**: Template Method pattern (`_cache_hash()`, `_init_graph()`) instead of `_init_attrs()` helper.
  Frozen `__init__` args made optional with early returns for MRO-safe `super()` calls.
- **WP5**: `__hash__ = None` on both ABCs and concrete mutable classes (MRO precedence requires both).
  Zero mutable-hash call sites found in `egpdb`/`egpdbmgr`.
- **WP6**: `_frozen` attribute hardening (Option B) rather than full builder pattern.
  `GGCDict.__init__` calls `super().__init__(gcabc)` then `object.__setattr__(self, "_frozen", True)`.
  `EGCDict` references updated from `gc.get("immutable", False)` to `getattr(gc, "_frozen", False)`.
