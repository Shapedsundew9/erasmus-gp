# Quickstart: Implement WP7 Option C

## Goal

Document the intentional diamond inheritance pattern and add deterministic MRO
regression tests without changing runtime behavior.

## Prerequisites

1. Activate virtual environment:

```bash
source /workspaces/erasmus-gp/.venv/bin/activate
```

2. Ensure codon/type data files exist (project baseline requirement):

```bash
python /workspaces/erasmus-gp/egpcommon/egpcommon/manage_github_data.py download
```

## Implementation Steps

1. Update class docstrings in these modules:
   - `egppy/egppy/genetic_code/c_graph_abc.py`
   - `egppy/egppy/genetic_code/frozen_c_graph.py`
   - `egppy/egppy/genetic_code/c_graph.py`
   - `egppy/egppy/genetic_code/interface_abc.py`
   - `egppy/egppy/genetic_code/frozen_interface.py`
   - `egppy/egppy/genetic_code/interface.py`
   - `egppy/egppy/genetic_code/endpoint_abc.py`
   - `egppy/egppy/genetic_code/frozen_endpoint.py`
   - `egppy/egppy/genetic_code/endpoint.py`
   - `egppy/egppy/genetic_code/ep_ref_abc.py`
   - `egppy/egppy/genetic_code/frozen_ep_ref.py`
   - `egppy/egppy/genetic_code/ep_ref.py`

2. Create architecture reference:
   - `docs/components/worker/diamond_inheritance.md`

3. Add MRO regression tests:
   - `tests/test_egppy/test_genetic_code/test_mro_diamond.py`

4. Keep existing mutability contract tests unchanged unless an assertion must
   be mirrored for consistency.

## Validation

1. Run focused tests:

```bash
python -m unittest tests/test_egppy/test_genetic_code/test_mro_diamond.py
```

2. Run relevant existing tests:

```bash
python -m unittest tests/test_egppy/test_genetic_code/test_mutability_contract.py
```

3. Run full baseline suite:

```bash
python -m unittest discover -s tests
```

## Completion Checklist

- All 5 diamonds have explicit MRO assertions.
- All covered classes have hierarchy-focused docstrings.
- Architecture doc includes diagrams, MRO listings, init pattern guidance.
- Full test suite passes with no behavioral regressions.
