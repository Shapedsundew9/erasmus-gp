# Design Document: Bootstrap Mutations Work Package

## Overview

Erasmus GP is a meta-genetic programming system where the operators of evolution (mutations and selectors) are themselves evolved genetic codes. This document defines the implementation of "Bootstrap Mutations"—functional primitives that operate on the Connection Graph (`CGraph`)—and the "Connection Processes" that govern their structural logic.

## Goals

1.**Complete existing mutations**: `Create`, `Wrap`, `Insert`, `Crossover`.
2.**Implement missing mutations**: `Rewire`, `Delete`, `Split`, `Iterate`.
3.**Implement structural optimization**: `Unused Parameter Removal`, `Dead Code Elimination`.
4.**Implement Connection Processes**: Integrate the prioritized connection logic defined in `connection_processes.md`.

## Connection Processes

Connection Processes define how interfaces are wired during or after a structural mutation. There are four distinct processes:

### 1. Create (Empty GC Filling)

Used when populating an `EMPTY` graph with sub-GCs.

- **Primary Step**: For each destination interface (`Ad`, `Bd`, `Od`), a compatible **Primary Connection** is mandatory if feasible.
- **Force Primary**: Inherent to this process.

### 2. Wrap

Used when encapsulating GCs (Stack, Harmony cases).

- **Logic**: Follows specific rules in `insertion.md`.
- **Primary Step**: **None**. Wrap mutations do not use the primary connection logic; they preserve or define connections based on the wrapping case.

### 3. Insertion

Used when inserting an `IGC` into a `TGC`.

- **Primary Step**: Prioritizes routing the target GC's existing flow through the new `IGC`.
- **Force Primary**: If no primary connection exists for the `IGC` input or the interfaces it serves as a source for, existing connections are severed and re-routed to primary sources.

### 4. Crossover

Used when replacing a sub-GC.

- **Logic**: Attempts to map old connections to the new interface by position/index.
- **Primary Step**: Inherits and executes the **Insertion** connection process after the initial positional mapping.

## Primary Sources & "Force Primary"

Primary sources are preferred routes that encourage idiomatic graph structures (e.g., `Is -> Ad -> Bd -> Od`).

| Destination Interface | Primary Source Interface |
| :--- | :--- |
| **Ad** (GCA Input) | **Is** (GC Input) |
| **Bd** (GCB Input) | **As** (GCA Output) |
| **Od** (GC Output) | **Bs** (GCB Output) |

The **Primary Step** (used in Create, Insertion, and Crossover) always employs **Force Primary** logic: it prioritizes establishing these connections, even if it requires severing existing non-primary connections.

## Implementation Strategy

### 1. Functional Mutations (Internal Library)

Mutations are internal library functions that return an `EGCode`. They are responsible for structural changes and executing the relevant **Connection Process**, but they **do not** perform stabilization.

```python
def mutation_name(rtctxt: RuntimeContext, target: GCABC, *args, **kwargs) -> EGCode:
    # 1. Structural change (e.g., set gca/gcb, change graph_type)
    # 2. Execute Connection Process (e.g., _insertion_connection_process)
    # 3. Return EGCode (potentially unstable)
```

### 2. Chaining & Stabilization

Bootstrap mutations can be chained together (e.g., by a Selector GC) to form complex aggregate mutations.

- **Mutation Step**: Each step returns a mutable `EGCode`.
- **Stabilization Step**: Only when the entire aggregate process is complete does the system invoke `stabilization.sfss()` to resolve any remaining Steady State Exceptions (SSEs) and produce a final `GGCode`.

## Optimization Mutations

Focused on **Structural Improvements**:

- **Unused Parameter Removal**: Pruning endpoints in the `I` row with no outgoing references.
- **Dead Code Elimination**: Pruning unreachable sub-graphs via static connectivity analysis.

## Verification Plan

1.**Unit Tests**: Located in `tests/test_egppy/test_physics/`.
2.**Process Validation**: Verify that the "Primary Step" correctly severs/re-routes connections in Insertion/Crossover cases.
3.**Stability Check**: Ensure that chained mutations eventually result in stable `GGCodes` after a final `sfss()` call.
