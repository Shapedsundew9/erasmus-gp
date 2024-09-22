# Mutation

Mutation in the real world is random at the most fundamental level: Energy from somewhere; radiation, electricity, etc. excites an election on an atom which is part of a larger molocule, or nearby one, causing it to ionize and react with the nearest viable thing. A reaction has occured and something new is created. If that event occured in self replicating system then the new thing is a mutation. More often than not, in super sophisticated systems such as life, there are many mechanisms to repair, workaround or discard the mutated material. If there were not, replicating complex systems would not be possible because that stuff happens all the time, and most mutations break things, but this robustness is not inherant it is the product of evolution.

Erasmus tries to mimic the mechanism of mutation at this, the most fundamental level. Mutation of a GC is random. Any connection in a GC connection graph can be broken resulting in an unstable situation that its "physics" abhors and immediately stablizes with whatever is viable nearby. This is called a *steady state exception* or *SSE*.

# Steady State Execptions, SSEs

Steady state exceptions are analogous to the spontaneous creation of a vacuum in the real world or the long term existence of a free radical. Such things are not violations of physics but aberrations to the steady state of things. When a steady state exception occurs, such as an ‘incomplete graph’ exception, events occur immediately to remove the exception. For example, a mutation modifies a target and leaves it with no viable input connections. Such a GC is not valid; it cannot be instantiated to even run. It is like a broken chemical bond where a carbon atom sits at the end of a molecule, short of an electron, connected to nothing. Such a situation can only be transient in nature, something must occur to resource a steady state. In the Erasmus universe an ‘incomplete graph’ exception occurs and handlers go to work to repair the aberration.

The only steady state exception is a destination endpoint in a GC connection graph that is not connected. This is a function that is missing a parameter - which in python is a runtime error. Following the vacuum/free radical analogy the exception must be resolved by connection to a viable source in 'close proximity'. Viable source endpoints have the same type as the destination endpoint and are either sourced:
 - **Internally**: An endpoint in the top level GC or any sub-GC that can be connected to the destination without breaking any graph connection rules. Routing connections through output and input interfaces is permitted.
 - **Externally**: A source end point of an Insertion GC, iGC, from the Gene Pool. The viability of an iGC is a function of the stability of the insertion, the proximity of the GC and its abundance.

## Insertion Stability

Inserting an iGC will lead to another SSE as its destination endpoints will also require connecting. The stability of insertion is defined by the number and type of the available source endpoints relative to the destination endpoints. The more destination types not available as sources the less stable the resultant GC will be.

 ## Proximity

