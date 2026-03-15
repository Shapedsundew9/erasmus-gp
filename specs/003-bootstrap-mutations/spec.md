# Feature Specification: Bootstrap Mutations Implementation

**Feature Branch**: `003-bootstrap-mutations`  
**Created**: 2026-03-15  
**Status**: Draft  
**Input**: User description: "Implement the design in /workspaces/erasmus-gp/docs/design/bootstrap_mutations.md"

## Clarifications

### Session 2026-03-15
- Q: Performance targets for mutation primitives? → A: Favor structural correctness over speed.
- Q: Behavior when graph size limits are exceeded? → A: Raise exception and abort mutation.
- Q: Mutation logging detail level? → A: Log type/target/status; detailed topology at DEBUG.
- Q: Concurrency strategy for graph mutations? → A: Mutations operate on a deep copy (copy-on-write).
- Q: Interface type compatibility verification? → A: Mutation MUST verify compatibility before connecting.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Full Set of Mutation Primitives (Priority: P1)

As a researcher using Erasmus GP, I want a complete set of basic mutation operators so that the evolution process can effectively explore the structural search space of programs.

**Why this priority**: These are the foundational building blocks of the entire genetic programming system. Without these, evolution cannot proceed.

**Independent Test**: Each mutation primitive can be invoked individually on a target graph, and the resulting structure can be verified to match the expected topological change.

**Acceptance Scenarios**:

1. **Given** an empty graph, **When** the `Create` mutation is applied, **Then** a new valid graph structure is populated with initial sub-GCs and primary connections.
2. **Given** an existing graph, **When** the `Delete` mutation is applied to a sub-GC, **Then** the sub-GC is removed and any dangling connections are handled according to the connection processes.
3. **Given** two parent graphs, **When** the `Crossover` mutation is applied, **Then** a new offspring graph is produced combining elements of both parents with correct positional mapping.

---

### User Story 2 - Idiomatic Wiring via Connection Processes (Priority: P1)

As a researcher, I want structural mutations to automatically apply "Connection Processes" and the "Primary Step" so that evolved programs naturally gravitate towards functional and idiomatic architectures (e.g., input -> sub-GC A -> sub-GC B -> output).

**Why this priority**: Random wiring often leads to non-functional programs. Intelligent wiring logic significantly increases the "density" of viable offspring in the search space.

**Independent Test**: Perform an `Insertion` mutation and verify that "Force Primary" logic correctly severs existing non-primary connections and establishes the preferred routes defined in the design document.

**Acceptance Scenarios**:

1. **Given** an insertion of sub-GC `IGC` into `TGC`, **When** the `Insertion` process is executed, **Then** the system prioritizes routing `TGC`'s existing flow through the new `IGC`.
2. **Given** a `Create` process, **When** destination interfaces are being wired, **Then** "Force Primary" ensures `Is -> Ad`, `As -> Bd`, and `Bs -> Od` connections are established if feasible.

---

### User Story 3 - Structural Optimization (Priority: P2)

As a researcher, I want the system to automatically prune dead code and unused parameters so that evolved genetic codes remain efficient and easier to analyze.

**Why this priority**: Evolution often produces "bloat". Pruning this bloat improves system performance and makes the resulting programs more understandable.

**Independent Test**: Run a "Dead Code Elimination" pass on a graph with unreachable sub-graphs and verify that the resulting graph is strictly smaller and functionally equivalent.

**Acceptance Scenarios**:

1. **Given** a graph with an endpoint in the `I` row that has no outgoing references, **When** "Unused Parameter Removal" is applied, **Then** that endpoint is removed.
2. **Given** a graph with sub-graphs that cannot reach the output, **When** "Dead Code Elimination" is applied, **Then** those unreachable nodes are removed.

---

### Edge Cases

- **Graph Disconnection**: How does the system handle mutations that result in a completely disconnected graph (no path from input to output)?
- **Circular Dependencies**: Mutations must not introduce circular dependencies that violate the Directed Acyclic Graph (DAG) nature of the `CGraph`.
- **Empty Mutation**: Handling cases where a mutation is requested but no valid change can be made (e.g., deleting a node from a graph that only has one node required for structural integrity).
- **Interface Mismatch**: Mutation primitives MUST verify interface type compatibility and raise an exception if an incompatible connection is attempted.
- **Size Limit Exceeded**: If a mutation causes the graph to exceed the maximum size limit, an exception is raised and the graph remains in its pre-mutation state.

---

### Assumptions

- **Stable Stabilization**: It is assumed that `stabilization.sfss()` is robust enough to resolve any Steady State Exceptions (SSEs) introduced by valid structural mutations.
- **DAG Constraint**: The `CGraph` is and must remain a Directed Acyclic Graph which is validated with its `verify()` and `consistency()` methods as per `epgcommon.egp_log` defined levels.
- **Valid Initial State**: Mutations are always applied to a structurally valid (though potentially unstable) `EGCode` or `GGCode`.
- **Transactional Mutations**: Each mutation is treated as an atomic operation that operates on a deep copy; if the mutation fails (e.g., type mismatch or size limit), the original graph remains unchanged.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Implement the following mutation primitives as internal library functions: `Create`, `Wrap`, `Insert`, `Crossover`, `Rewire`, `Delete`, `Split`, `Iterate`.
- **FR-002**: Implement the four "Connection Processes" (`Create`, `Wrap`, `Insertion`, `Crossover`) to govern wiring logic during mutations.
- **FR-003**: Implement the "Primary Step" with "Force Primary" logic, mapping specific destination interfaces to their primary source interfaces as defined in the design doc.
- **FR-004**: Implement "Unused Parameter Removal" to prune endpoints in the `I` row with no outgoing references.
- **FR-005**: Implement "Dead Code Elimination" using static connectivity analysis to prune unreachable sub-graphs.
- **FR-006**: Mutation functions MUST return an `EGCode` (potentially unstable) and MUST NOT perform final stabilization themselves.
- **FR-007**: Ensure mutations can be chained together, with final stabilization deferred until the end of the aggregate process.
- **FR-008**: System MUST enforce a maximum graph size limit (as defined in system configuration) and raise an exception if a mutation would exceed it.
- **FR-009**: System MUST log mutation type, target ID, and success/failure; detailed topology changes MUST be logged at the `DEBUG` level.
- **FR-010**: Mutation primitives MUST operate on a deep copy of the `CGraph` to ensure atomicity and structural safety.
- **FR-011**: System MUST verify interface type compatibility before establishing any connection during a mutation; incompatible attempts MUST raise an exception.

### Non-Functional Requirements

- **NFR-001**: Prioritize structural correctness and topological integrity over execution speed during mutation operations.
- **NFR-002**: Adhere to the project's custom logging levels and debug patterns for mutation events.

### Key Entities *(include if feature involves data)*

- **Connection Graph (CGraph)**: The underlying structural representation of a genetic code, consisting of sub-GCs and their interface connections.
- **EGCode (Evolved Genetic Code)**: A mutable representation of a genetic code that may contain Steady State Exceptions (SSEs) during the mutation process.
- **GGCode (GPool Genetic Code)**: A final, stabilized, and validated genetic code suitable for storage in the gene pool.
- **Mutation Primitive**: A functional unit that performs a specific structural transformation on a `CGraph`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of mutation primitives (8/8) pass unit tests verifying correct structural transformation of the `CGraph`.
- **SC-002**: "Primary Step" establishes the mandatory connections (if feasible) in 100% of `Create`, `Insertion`, and `Crossover` test cases.
- **SC-003**: "Dead Code Elimination" identifies and removes 100% of unreachable nodes in benchmark test graphs.
- **SC-004**: Chained mutation sequences result in a valid `GGCode` after a single call to `stabilization.sfss()` in 100% of verified test scenarios.
