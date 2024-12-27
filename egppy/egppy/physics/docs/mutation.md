# Mutation

Mutations evolve in the same way any problem solution evolves in Erasmus GP. The primitive mutations are described below and come in two catagories: Functional and Optimisation.

## Functional Mutuation Primitives

Functional mutations are intended (though may not) modify the behaviour of the targeted GC.

## Optimization Mutation Primitives

Optimization mutations are intended to reduce the code size of a targeted GC or increase its runtime performance. Optimisation mutation GC's are neatly evolable in that the "optimization problem" can be stated generically: For all the use cases of this GC replace it with a better performing one.

|          **Name**         |                                                      **Description**                                                     |
|:--------------------------|:-------------------------------------------------------------------------------------------------------------------------|
| Dead Code Elimination     | Identify GC sub-structures that will never be run and stub them off or remove the conditional.                           |
| Collapse constants        | Find GC structures with constant inputs and deterministic processing. Execute them and replace the code with the result. |
| Arithmetic simplification | Identify arithmetically deterministic code and apply symbolic regression to simplify the expression.                     |
| Unused parameter removal  | Remove parameters that are unsed by the GC.                                                                              |
| Code rearrangement        | Move code that is only made use of on one side of a conditional into the conditional.                                    |
|                           |                                                                                                                          |
|                           |                                                                                                                          |
|                           |                                                                                                                          |
|                           |                                                                                                                          |
|                           |                                                                                                                          |
|                           |                                                                                                                          |
|                           |                                                                                                                          |
|                           |                                                                                                                          |
|                           |                                                                                                                          |
|                           |                                                                                                                          |
|                           |                                                                                                                          |
|                           |                                                                                                                          |
|                           |                                                                                                                          |
|                           |                                                                                                                          |
