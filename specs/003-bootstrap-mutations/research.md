# Research: Bootstrap Mutations Implementation

## Findings

### Existing Mutations
- `Create`: Located in `egppy/physics/create.py`. Currently a stub returning the input `EGCode`.
- `Wrap`: Located in `egppy/physics/wrap.py`. Implements `STACK`, `ISTACK`, `WRAP`, `IWRAP`, `HARMONY`. Uses `_wrap_connection_process` (stub).
- `Insert`: Located in `egppy/physics/insert.py`. Implements `ABOVE_A`, `ABOVE_B`, `ABOVE_O`. Uses `_insert_connection_process` (stub).
- `Crossover`: Located in `egppy/physics/crossover.py`. Currently a stub.

### Missing Mutations
- `Rewire`: Not yet implemented.
- `Delete`: Not yet implemented.
- `Split`: Not yet implemented.
- `Iterate`: Not yet implemented.

### Connection Processes
- The logic for connection processes is defined in `docs/design/connection_processes.md`.
- There are four processes: `Create`, `Wrap`, `Insertion`, `Crossover`.
- All processes use "Primary Sources" and "Force Primary" logic.
- Primary sources are:
    - `Ad` ← `Is`
    - `Bd` ← `As`
    - `Od` ← `Bs`

### Optimization Mutations
- `Unused Parameter Removal`: Needs implementation.
- `Dead Code Elimination`: Needs implementation.

### CGraph and EGCode
- `CGraph` is mutable; `FrozenCGraph` is immutable.
- `EGCode` is a mutable dictionary-like object wrapping a `CGraph`.
- `stabilization.sfss()` performs the final stabilization.

## Decisions

### 1. Implementation Location
- Create a new sub-package `egppy.physics.mutations` for all mutation primitives.
- Existing `create.py`, `wrap.py`, `insert.py`, `crossover.py` will be moved or integrated into this sub-package.
- Connection processes will be implemented in `egppy/physics/processes.py`.

### 2. Connection Process Logic
- Implement a central helper for "Primary Connection" logic that can be shared across processes.
- Ensure "Force Primary" correctly severs existing connections as per `Insertion` process requirements.

### 3. Structural Optimization
- Implement DCE using a reachability analysis (bottom-up from `Od`).
- Implement Parameter Removal by checking for endpoints in `Is` with no outgoing connections.

### 4. Atomicity
- All mutation functions will receive an `EGCode`, but as per `FR-010`, they must ensure atomicity. Since `EGCode` is mutable, we will use `.copy()` or `new_egc()` to work on a fresh instance if needed, or rely on the fact that `EGCode` itself is often a "work-in-progress" object. However, for public-facing mutation APIs, a deep copy of the `CGraph` is mandatory.

## Alternatives Considered

- **In-place vs Copy**: In-place modification is faster but riskier. Given the "transactional" requirement, a copy-on-write approach for the `CGraph` is the chosen path.
- **DCE Algorithm**: Considered top-down vs bottom-up. Bottom-up (from `Od`) is more direct for finding "dead" code that doesn't contribute to the output.
