# Data Model: Anti-Pattern Fixes (WP4-WP6)

## Entity: Frozen Genetic Code Object

- Represents: Immutable canonical genetic-code structure with stable pre-computed hash.
- Implementations in scope:
  - `FrozenCGraph`
  - `FrozenInterface`
  - `FrozenEndPoint`
  - `FrozenEPRef` / `FrozenEPRefs`
- Key fields (conceptual): graph/interface/endpoint/ref structural attributes + `_hash` cache.
- Validation rules:
  - Constructor input verification remains strict.
  - Consistency checks remain unchanged from existing behavior.
- State transitions:
  - `Constructing` -> `Initialized` -> `Hash Cached` -> `Immutable Use`

## Entity: Mutable Genetic Code Object

- Represents: Editable working genetic-code structure used during construction/transformation.
- Implementations in scope:
  - `CGraph`
  - `Interface`
  - `EndPoint`
  - `EPRef` / `EPRefs`
  - `EGCDict`
- Key fields (conceptual): same structure as frozen peers but mutable containers and no hash
  contract.
- Validation rules:
  - Constructor and mutation methods preserve existing verify/consistency invariants.
- Hash contract:
  - `__hash__ = None` via mutable ABC hierarchy.
  - Any direct `hash(mutable_obj)` must raise `TypeError`.
- State transitions:
  - `Constructing` <-> `Mutating` -> `Converted/Projected to Frozen` (for hashable use)

## Entity: GGCDict (Persisted Immutable Genetic Code Record)

- Represents: Final immutable persisted genetic-code dictionary structure.
- Construction model:
  - Single-step `__init__` from keyword fields or completed `EGCDict` builder.
  - No runtime `"immutable"` key.
  - No `set_members()` lifecycle.
- Validation rules:
  - Constructor validates required keys and structural constraints at creation time.
- Mutation rules:
  - `__setitem__`, `update`, and equivalent mutators must raise `TypeError`.
- State transitions:
  - `Input Validation` -> `Constructed Immutable` -> `Persisted/Hashed Use`

## Relationship Model

- Mutable <-> Frozen relationship:
  - Mutable entities are working forms.
  - Frozen entities are canonical hashable forms.
- `GGCDict` depends on `EGCDict` as builder input (optional pathway), but resulting
  `GGCDict` is immutable and independent from subsequent builder mutations.
- Cross-package consumers (`egpdb`, `egpdbmgr`, `egpseed`) must treat mutable objects as
  non-hashable and use frozen/canonical objects when hash identity is required.
