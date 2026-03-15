# Contract: Diamond Documentation and MRO Regression Safety

## Purpose

Define the acceptance contract for WP7 Option C artifacts:

- Hierarchy documentation in class docstrings
- Architecture reference document
- Deterministic MRO regression tests

## Scope

Applies to five diamond hierarchies in `egppy/egppy/genetic_code/`:

1. `CGraph`
2. `Interface`
3. `EndPoint`
4. `EPRef`
5. `EPRefs`

Grouped as four families (`CGraph`, `Interface`, `EndPoint`, `EPRef/EPRefs`).

## Documentation Contract

For each class in each hierarchy (`Frozen*ABC`, `Frozen*`, `*ABC`, `*`):

- MUST include class-level Google-style docstring.
- MUST state hierarchy role: frozen ABC, frozen concrete, mutable ABC, or mutable concrete.
- MUST list direct parent classes in declared order.
- MUST identify shared grandparent in the diamond.
- MUST explain why parent ordering is intentional for MRO-safe dispatch.

## Architecture Document Contract

File: `docs/components/worker/diamond_inheritance.md`

- MUST include one diagram per family and clearly identify 5 diamonds total.
- MUST include full MRO sequences for each diamond.
- MUST describe init patterns:
  - optional-args-with-early-return
  - separated-hash-computation
  - template-method-with-override
- MUST include contributor guidance for adding a new frozen/mutable pair.

## Test Contract

File: `tests/test_egppy/test_genetic_code/test_mro_diamond.py`

- MUST assert exact `__mro__` sequences for all 5 diamonds.
- MUST assert positive subclass relationships:
  - mutable concrete is subclass of frozen ABC
  - mutable concrete is subclass of mutable ABC
- MUST assert negative subclass relationships:
  - frozen concrete is not subclass of mutable ABC
- MUST provide deterministic failure messages that include:
  - target class name
  - expected MRO sequence
  - actual MRO sequence

## Compatibility Contract

- MUST preserve runtime behavior of production classes.
- MUST execute and pass the following validation commands:
  - `python -m unittest tests/test_egppy/test_genetic_code/test_mro_diamond.py`
  - `python -m unittest tests/test_egppy/test_genetic_code/test_mutability_contract.py`
  - `python -m unittest discover -s tests`
- MUST avoid API/import path changes outside documentation/test additions.
