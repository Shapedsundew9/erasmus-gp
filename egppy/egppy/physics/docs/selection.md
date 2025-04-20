# GC Selection

The success of cross-over or insertion in creating a fit new GC is partly dependent on the selection of the GC's involved. One GC is always known, e.g.the member of the population chosen to evolve, selection of the other is done by 'selectors'. Selection is driven by 3 parameters:

- Constraints: These are hard limits on what can be selected. e.g. the GC must have a 'float' input.
- Scope: Where to look, e.g. in related GCs, in a 'store' like the gene pool or genomic library etc.
- Fitness: Bias selection by a suitability criteria e.g. abundance in the population, optional criteria

## Constraints


