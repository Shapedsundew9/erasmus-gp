# Quickstart: Bootstrap Mutations

This guide demonstrates how to use the new Bootstrap Mutations and Connection Processes in Erasmus GP.

## Prerequisites

- Access to a `RuntimeContext` and a `GenePoolInterface`.
- Valid `EGCode` or `GGCode` objects as targets for mutations.

## Applying a Mutation

All mutations are available via the `egppy.physics.mutations` module.

```python
from egppy.physics.mutations import insert, InsertionCase
from egppy.physics.stabilization import sfss

# 1. Perform a structural mutation (Insertion)
# This returns an unstable EGCode (copy-on-write)
rgc = insert(rtctxt, igc, tgc, case=InsertionCase.ABOVE_A)

# 2. (Optional) Chain more mutations
# rgc = rewire(rtctxt, rgc, ...)

# 3. Perform final stabilization
stable_gc = sfss(rtctxt, rgc)
```

## Running Optimizations

Optimizations can be run manually to prune dead code or unused parameters.

```python
from egppy.physics.optimization import dead_code_elimination, unused_parameter_removal

# Prune unreachable sub-graphs
optimized_gc = dead_code_elimination(rtctxt, rgc)

# Prune input endpoints with no outgoing connections
optimized_gc = unused_parameter_removal(rtctxt, optimized_gc)
```

## Connection Processes

The wiring logic is automatically handled by the mutation primitives using "Force Primary" rules.

- `Create`: Populates empty graphs with primary routes (`Is -> Ad`, `As -> Bd`, `Bs -> Od`).
- `Insertion`: Prioritizes routing through the newly inserted code.
- `Crossover`: Maps existing connections by position before applying insertion logic.
