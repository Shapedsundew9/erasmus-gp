# GC Selection

The success of cross-over or insertion in creating a fit new GC is partly dependent on the selection of the GC's involved. One GC is always known, e.g. the member of the population chosen to evolve, selection of the other is done by 'selectors'. Selection is driven by 3 parameters:

- Constraints: These are hard limits on what can be selected. e.g. the GC must have a 'float' input.
- Scope: Where to look, e.g. in related GCs, in a 'store' like the gene pool or genomic library etc.
- Fitness: Bias selection by a suitability criteria e.g. abundance in the population, optional criteria

## Constraints

Constraints are structural or type-based requirements that a candidate GC must satisfy to be eligible for selection. If a GC does not meet the constraints, it is immediately discarded from the candidate pool. Common constraints include:
- **Type Constraints**: The candidate GC must accept a specific type as input or return a specific type as output to match an open endpoint.
- **Graph Constraints**: The candidate must be a specific kind of code (e.g., standard, conditional, loop) or be within a certain size/depth limit.

## Scope

Scope defines the search space for candidate GCs. Depending on the stabilization phase or the mutation operation, the scope can be narrow or broad:
- **Internal/Local Scope**: Reusing existing connections or searching within the immediate parent/child hierarchy of the current GC graph.
- **Microbiome/Biome Scope**: Searching within the local population or related evolutionary branches.
- **Global Scope**: Searching the entire global Gene Pool for a viable insertion candidate.

## Fitness

When multiple candidates satisfy the Constraints within the specified Scope, Fitness determines which candidate is chosen. Rather than a purely uniform random selection, fitness introduces evolutionary bias:
- **Abundance**: GCs that are highly abundant in the gene pool or local population are more likely to be selected.
- **Performance**: Candidates with a historical record of producing stable, high-fitness outcomes in prior generations may receive a higher probability weighting.
- **Complexity Penalty**: Simpler GCs might be favored over overly complex ones to prevent unchecked bloat.
