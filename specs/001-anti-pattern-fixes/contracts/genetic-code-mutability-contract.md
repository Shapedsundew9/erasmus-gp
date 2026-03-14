# Contract: Genetic Code Mutability and Hashing

## Scope

Defines behavioral contracts for genetic-code classes affected by WP4-WP6.

## Contract 1: Initialization Chain Integrity (WP4)

- Mutable classes MUST call `super().__init__()`.
- Frozen class initialization MUST separate:
  - attribute/materialized state initialization
  - hash cache computation
- Constructor outputs:
  - Frozen classes: initialized with cached hash.
  - Mutable classes: initialized without cached hash contract.

## Contract 2: Mutable Hash Behavior (WP5)

- Mutable genetic-code ABCs MUST define `__hash__ = None`.
- Calling `hash()` on mutable instances MUST raise `TypeError`.
- Frozen instances MUST remain hashable and stable.
- Any use case requiring hash identity from mutable workflow MUST transition through a
  frozen/canonical representation or explicit compute pathway.

## Contract 3: Hash Call-Site Migration (WP5)

- All code paths in `egppy`, `egpdb`, `egpdbmgr`, and tests MUST avoid hashing mutable
  instances.
- Migration acceptance:
  - no known mutable-hash call sites remain
  - unit tests cover failure mode (`TypeError`) and valid frozen hashing paths

## Contract 4: GGCDict Immutability (WP6)

- `GGCDict` MUST be fully immutable immediately after `__init__`.
- Constructor inputs:
  - full keyword arguments, or
  - completed `EGCDict` builder object.
- `GGCDict` MUST NOT use runtime `"immutable"` dictionary key.
- Mutation attempts (`__setitem__`, `update`, deletion where applicable) MUST raise `TypeError`.

## Backward Compatibility Rules

- Public behavior changes are intentional for mutable `hash()` and runtime GGCDict
  construction flow.
- Downstream packages importing these classes must follow updated contracts.
- Frozen class hashing semantics are preserved and considered compatibility anchors.
