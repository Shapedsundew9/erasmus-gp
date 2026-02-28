# Individuals

An individual is a single entity in the population. It is a solution to the problem that the genetic programming algorithm is trying to solve. The individual module contains the classes and functions that define the individual and its properties to the problem.

## Design

An individual is implemented as an instance of the `Genotype` class (a phenotype). Each phenotype holds:

- **signature**: The cryptographic signature of the underlying Genetic Code.
- **func**: The executable function compiled from the Genetic Code.
- **puid**: The population UID identifying which population this individual belongs to.
- **state**: A mutable `State` list tracking the phenotype's current state.
- **memory**: A mutable `State` list for dynamic experiences accumulated during execution.
- **energy**: An `int64` energy budget consumed during execution; the individual is "dead" when depleted.
- **fitness**: A `double` fitness score evaluated against the problem.
- **survivability**: A `double` survivability score influencing selection pressure.

The `StateABC` abstract class defines the list-like interface that both `state` and `memory` must satisfy.
