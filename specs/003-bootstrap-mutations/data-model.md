# Data Model: Bootstrap Mutations

## Key Entities

### CGraph (Connection Graph)
- **Status**: Mutable during mutation, but must be valid Directed Acyclic Graph (DAG) for execution.
- **Components**: Endpoints, Interfaces, Connections.
- **Validation**:
    - `verify()`: Basic type and range checks on endpoints.
    - `consistency()`: Cross-field and structural validation (DAG, interface mapping, connection types).

### EGCode (Evolved Genetic Code)
- **Status**: Mutable, used as a temporary container during mutation.
- **Components**: `CGraph`, `GCA`, `GCB`, `Ancestors`, `Properties`.
- **States**:
    - `Unstable`: Contains unconnected destination endpoints.
    - `Stable`: All destination endpoints have exactly one connection.

### Mutation Primitive
- **Role**: Functional unit performing structural changes on `CGraph`.
- **Inputs**: `RuntimeContext`, `EGCode`, `*args`.
- **Outputs**: `EGCode` (modified or new).

### Connection Process
- **Role**: Logic defining how to wire interfaces after a mutation.
- **States**: `Create`, `Wrap`, `Insertion`, `Crossover`.

## State Transitions

### Mutation Cycle
1. **Input**: Stable or Unstable `EGCode`.
2. **Structural Modification**: Primitive (e.g., `Delete`) modifies `CGraph` structure.
3. **Connection Process**: `processes.py` logic applies idiomatic wiring.
4. **Output**: Unstable `EGCode` (ready for further mutation or stabilization).
5. **Stabilization**: `sfss()` converts Unstable `EGCode` to Stable `EGCode`.
6. **Persistence**: `GGCode` created from Stable `EGCode`.

## Validation Rules
- **DAG Integrity**: No mutation can result in a circular dependency.
- **Type Safety**: Connections must be "Compatible" or "Downcast" (at least during stabilization). Mutations should prioritize "Compatible".
- **Primary Connection Requirement**: For `Create`, `Insertion`, and `Crossover`, the primary connections MUST exist if feasible.
