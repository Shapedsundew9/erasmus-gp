# Mutation

Mutations evolve in the same way any problem solution evolves in Erasmus GP. The primitive mutations are described below and come in two catagories: Functional and Optimisation.

## Functional Mutuation Primitives

Functional mutations are intended (though may not) modify the behaviour of the targeted GC.

Mutations GCs may take either EGCodes or GGCodes as inputs and return EGCodes Which may or may not be stable.  EGCodes may then be further mutated or can be converted to a GGCode through a stabilization mutation, of which there are two varieties, the `connect_all` version, in which all destination endpoints are randomly connected and if possible a (stable) GGCode is created, otherwise an exception is raised and the mutation fails, or a `stabilize` mutation that allows a steady state exception to try and repair unconnected destination endpoints within the EGCode connection graph. This mutation is much more likely to succeed, but may also still fail.  

|          **Name**         |                                                      **Description**                                                     |
|:--------------------------|:-------------------------------------------------------------------------------------------------------------------------|
| Swap Connections          | Identify compatible connections within a graph (or nearby GC's) to swap.                                                 |
| Dupe Src Connection       | Reuse a source endpoint to replace another endpoint connection.                                                          |
| Harmony                   |                                                                                                                          |
| Perfect Stack             |                                                                                                                          |
| Stack                     |                                                                                                                          |
| Insert                    |                                                                                                                          |
| Swap                      |                                                                                                                          |
| Delete                    |                                                                                                                          |
| Split                     | If-then-else                                                                                                             |
| Bypass                    | If-then                                                                                                                  |
| Iterate                   | For loop                                                                                                                 |
|                           |                                                                                                                          |
|                           |                                                                                                                          |
|                           |                                                                                                                          |

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
