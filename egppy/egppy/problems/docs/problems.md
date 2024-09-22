# Problems

A problem in Erasmus is defined by input data, expected output data for the input data and a fitness function. The fitness function calculates a score between 0.0 and 1.0 for an individual GC that was tasked with producing the expected output from the input data. Because Erasmus generates executable code that could, in theory, be manipulated to have adverse effects the input data, expected output and fitness function are defined by a problem definition hash. A change to any component (even one that does not change the fitness score) results in a different problem hash.

## Verified problems

TBD

## Related Problems: Problem Sets

If problem A is related to problem B then population A is related to population B. In the trivial case the fitness function of B may just be a more efficient version of the fitness function of A with no functional differences. The same is true if population A is related to population B and fitness function B is related to fitness function C then population A (or sub-GC’s there of) could be useful to fitness function C and should be considered as a candidate to seed or breed in population C.

A consequence of these relationships is that GC A may have a valid fitness score for problem A, problem B and problem C and this is in fact what happens with PGCs where the problem is the degree of separation of the PGC mutated from the solution GC's, the PGC level.

A problem set is the definition of the relationship between two problems, problem sets or a combination there of making it a binary tree with problem leaves.

## The Problem Tree

The problem (binary) tree is universal. Whilst problem leaves and problem set nodes are immutable, having a fixed hash defined by the ordered hashes of the left and right adjoining nodes. The left node always being the node with the numerically unsigned highest hash value and the node hash being the SHA256 of the concatenation of left:right adjoining node hashes.
Each problem or problem set has a weight equal to the number of GCs that have that problem set.

```mermaid
flowchart
    E(("Entropy"))
    E --> S(("Sense & React"))
    S --> D(("Gradient detection"))
    S --> M(("Memory & Time"))
    S --> I(("Internal State"))
    S --> P(("Prediction"))
    D --> GM(("Gradient & Memory"))
    D --> GI(("Gradient & Intenal State"))
    D --> GP(("Gradient & Prediction"))
…   P --> L
```
