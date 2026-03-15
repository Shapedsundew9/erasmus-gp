# Data Model: Diamond Inheritance Documentation & MRO Safety Tests

## Overview

This feature is documentation/test focused. The model defines conceptual entities
that govern how class hierarchy knowledge is represented and verified.

## Entities

### 1. InheritanceFamily

- Description: Logical grouping of related classes participating in one or more diamonds.
- Fields:
  - `name` (str): Family identifier (`CGraph`, `Interface`, `EndPoint`, `EPRef`).
  - `module_group` (list[str]): Source module paths for the family.
  - `diamond_count` (int): Number of diamonds in family.
- Relationships:
  - Has many `DiamondHierarchy`.

### 2. DiamondHierarchy

- Description: One concrete frozen/mutable inheritance diamond that must keep a stable MRO.
- Fields:
  - `name` (str): Hierarchy name (`CGraph`, `Interface`, `EndPoint`, `EPRef`, `EPRefs`).
  - `frozen_abc` (str): Abstract frozen parent type.
  - `frozen_concrete` (str): Frozen concrete implementation.
  - `mutable_abc` (str): Mutable abstract interface.
  - `mutable_concrete` (str): Mutable implementation class.
  - `shared_grandparent` (str): Shared parent in diamond (typically frozen ABC).
  - `expected_mro` (list[str]): Canonical linearized class order.
- Relationships:
  - Belongs to one `InheritanceFamily`.
  - Referenced by one or more `MROContractTest` cases.

### 3. ClassDocstringContract

- Description: Required structure for class-level hierarchy documentation.
- Fields:
  - `class_name` (str)
  - `role` (enum): `frozen_abc | frozen_concrete | mutable_abc | mutable_concrete`
  - `direct_parents` (list[str])
  - `shared_grandparent` (str)
  - `ordering_rationale` (str): Why parent order is intentional.
- Relationships:
  - One contract entry per class in each `DiamondHierarchy`.

### 4. MROContractTest

- Description: Executable unittest assertion set for hierarchy invariants.
- Fields:
  - `test_name` (str)
  - `target_class` (str)
  - `expected_mro` (list[str])
  - `subclass_positive` (list[tuple[str, str]]): `(child, parent)` assertions expected True.
  - `subclass_negative` (list[tuple[str, str]]): `(child, parent)` assertions expected False.
  - `failure_message_template` (str): Includes expected and actual sequences.
- Relationships:
  - Validates one `DiamondHierarchy`.

## Validation Rules

- Family coverage must include exactly 4 families and 5 diamonds total.
- Every diamond must have all four class roles populated.
- `expected_mro` must start with mutable concrete class and end with `object`.
- Every covered class must have a `ClassDocstringContract` entry.
- Every diamond must have at least one exact-MRO test and one subclass-contract test.

## State Transitions

### Hierarchy Documentation State

- `undocumented` -> `documented` when class docstring includes all contract fields.
- `documented` -> `verified` when corresponding MRO tests pass.

### Regression Protection State

- `verified` -> `failed` when parent order or base set changes and test mismatch occurs.
- `failed` -> `verified` when hierarchy is corrected and tests pass.
