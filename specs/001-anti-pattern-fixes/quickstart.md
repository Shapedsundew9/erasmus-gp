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

- No `super-init-not-called` / `non-parent-init-called` suppression comments remain in WP4
  targets.
- Mutable genetic-code classes are non-hashable by contract.
- No mutable-hash call sites remain after audit.
- `GGCDict` runtime immutability flag and two-step setup are removed.
- Full test suite passes with no regressions.
