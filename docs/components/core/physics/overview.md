# EGP Physics

Erasmus GP can be thought of as an artificial universe in which artificial life or artificial intelligence is theoretically possible (but by no means a forgone conclusion). Our universe is derived from, to the extent that we know of, the fundamental laws & elements of its physics like the 2nd law of thermodynamics, quarks and leptons etc. Stars, planets, oceans, life and intelligence all derive from those fundamental elements to satisfy the laws. The Erasmus universe works on the same principles just with a different set of fundamental elements and laws with the aim of expressing in similar ways.

- Types
- Genetic Codes
- Selectors
- Physical Genetic Codes

## Types

Types are python objects such as *int*, *str* and *float*, compound containers like *list[list[str]]* and also EGP specific classes like *GGC* and *Selector* (more on these below). EGP is strongly typed in that GC's interfaces are statically defined, the type of the output is set when the GC is created.

## Genetic Codes

The simplest form of a genetic code is a codon. Codons operate on instances of types to produce instances of types (the produced instances may be the same instances, different instances of the same types or instances of different types altogether). In reality they are python functions that (may) take parameter objects, perform some sort of operation with them or on them and (may) return objects. Codons are atomic and immutable and can be connected together into more complex Genetic Codes, GC's, which are just more complex python functions. As with functions, GC's can call other GC's in a tree structure until a codon (terminal/leaf node) is called. Genetic Codes can opertate on genetic codes, to stick them together in various ways for example, to extend, mutate or trim them. Genetic Codes is where all the action is at in EGP.

### GC Classes: EGCode vs GGCode

Throughout the physics and mutation processes, a Genetic Code exists as one of two distinct classes (often abbreviated to EGC or GGC):

- **EGCode (Embryonic Genetic Code)**: A mutable, active evolution subset of a genetic code. When a GC is actively undergoing mutation, structural changes, or stabilization, it is represented as an EGCode. It cannot be executed directly because its internal connection graph may have broken or unconnected endpoints. `EGCDict` is the analogous underlying dictionary representation.
- **GGCode (General Genetic Code)**: A stable, immutable, and executable genetic code. Once an EGCode has been successfully stabilized and all its endpoints are connected, it is converted into a GGCode and deposited into the Gene Pool for execution or future selection. `GGCDict` is the underlying immutable dictionary containing cryptographic signatures. Note that just because a GGC is structurally stable does not mean it is runtime stable.

## Selectors

Whilst the Erasmus universe can be intuitive it can also be very alien; there is no direct analogy to space, entropy, gravity etc. In our universe chemicals react when they are bought together by physical processes into close enough proximity with the right energetic conditions. Inside an information universe there is no concept of space, there is related information and unrelated information but none of it is near or far from each other in any other fundamentally meaningful way. Its a bit like how you are viewing this document, it is meaningless how far away you physically are from where this file is physically stored. There are no natural forces, like gravity, pulling matter together in a well where it may react, or processes of decay that determine what chemicals are likely to be locally in abundance. Defining arbitary laws for how information comes together is likely not to work and combining everything with a single random law will be slow. It is the role of selectors in EGP to define with what probability types and operations come together to 'react' and make something new.

Selectors are a type of GC that choose genetic codes from the environment, most commonly the local Gene Pool, to pass to other genetic codes which have some purpose for them. There is no constraint on the 'why' or 'what' a selector may be doing, selectors may select other selectors for example.

For more details see [Selection](./selection.md)

## Physical Genetic Codes

Physical Genetic Codes or PGCs are genetic codes that create new genetic codes. Whether the PGC takes parameters or another genetic code as input or just randomly generates a genetic code the requirement to be a PGC is only that a new embryonic genetic code, EGC, is output.

## Bootstrap Mutuations

Mutations evolve in the same way any problem solution (genetic code) evolves in Erasmus GP, however, the process needs bootstrapping. Erasmus defines a set
of functional mutations that start the evolution process and evolve themselves. By definition a mutation is a PGC.

Functional mutations are intended (though may not) modify the behaviour of the targeted GC.

Mutations GCs may take either EGCodes or GGCodes as inputs and return EGCodes Which may or may not be stable. EGCodes may then be further mutated or can be converted to a GGCode through a stabilization process which makes them executable (though not necessarily error free).  

| Name | Description |
| :--- | :--- |
| Create | Create a new GC from an empty CGraph. |
| Rewire | Swap, shuffle, reuse connections in the CGraph. |
| Wrap | Stack, pair (harmony) genetic codes into a new GC. |
| Insert | Insert a GC into the target GC's graph. See [Insertion](./insertion.md). |
| Crossover | Swap a sub-GC with another sub-GC with the same or similar interface. |
| Delete | Remove a sub-GC or codon from the target graph, rerouting or exposing its connections for stabilization. |
| Split | Introduce an if-then or if-then-else conditional branching structure into the GC. |
| Iterate | Wrap a sub-GC within a loop structure. |

## Optimization Bootstrap Mutations

Optimization mutations are intended to reduce the code size of a targeted GC or increase its runtime performance. Optimisation mutation GC's are neatly evolable in that the "optimization problem" can be stated generically: For all the use cases of this GC replace it with a better performing one.

| Name | Description |
| :--- | :--- |
| Dead Code Elimination | Identify GC sub-structures that will never be run and stub them off or remove the conditional. |
| Collapse constants | Find GC structures with constant inputs and deterministic processing. Execute them and replace the code with the result. |
| Arithmetic simplification | Identify arithmetically deterministic code and apply symbolic regression to simplify the expression. |
| Unused parameter removal | Remove parameters that are unsed by the GC. |
| Code rearrangement | Move code that is only made use of on one side of a conditional into the conditional. |
