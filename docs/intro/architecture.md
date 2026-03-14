# Erasmus Genetic Programming - Architecture

## Top Level

TBD: K8s, Namespaces?

```mermaid
%%{init: { 'theme': 'dark', 'themeVariables': { 'lineColor': '#6c7a89', 'textColor': '#edf2f4', 'mainBkg': '#2b2d42', 'primaryBorderColor': '#4a4e69' }}}%%
flowchart TD
    %% Base/Default (Dark Slate)
    classDef default fill:#2b2d42,stroke:#4a4e69,stroke-width:2px,color:#edf2f4
    classDef dataBlue fill:#3a506b,stroke:#5c6b73,stroke-width:2px,color:#ffffff
    classDef dataTeal fill:#3b5e60,stroke:#5b7a7c,stroke-width:2px,color:#ffffff
    classDef dataPlum fill:#4a3b52,stroke:#685b70,stroke-width:2px,color:#ffffff
    classDef dataNavy fill:#2c3e50,stroke:#4a5c6e,stroke-width:2px,color:#ffffff
    classDef zoneExternal fill:#221f2e,stroke:#4a3b52,stroke-width:2px,stroke-dasharray: 5 5

    subgraph Cluster [System Infrastructure]
        direction TB
        wkr1[[Worker Pool]]:::dataNavy
        dbm1[("Gene Pool (DBM)")]:::dataPlum
        fe1[[Fitness Executor Pool]]:::dataTeal
    end

    subgraph Storage [Global Storage]
        direction TB
        dbm2[("Microbiome Genomic Library")]:::dataPlum
        dbm3[("Biosphere Genomic Library")]:::dataPlum
    end

    wkr1 <--> dbm1
    fe1 <-.-> wkr1
    dbm1 <--> dbm2
    dbm2 <--> dbm3

    class Cluster zonePrimary
    class Storage zoneExternal
```

The entry point to the system is a worker. Workers are independent containers, gathered in a pool and maintain no state. Workers *may* use an independent fitness executor to evaluate genetic codes but can also be configured to work on predefined problems locally. Typically local evaluation is only done when the overhead of using a remote fitness executor significantly slows down the system. Fitness executors are also arranged in a pool, are independent containers and also maintain no state.

Workers retrieve genetic codes from the Gene Pool which is a postgres database managed by an EGP DB Manager. Whilst a pool of workers may connect to many Gene Pools a worker must connect to exactly one as defined by its configuration. Gene Pools are intended to be performant and should be implemented local to workers with fast persistent storage. In the absense of a Microbiome Genomic Library the Gene Pool is populated with the default set of GC's shipped with the version of the EGP DB Manager installed.

The Gene Pool may connect to a Genomic Library as a source and store of GC's  --- NEED TO THINK ABOUT THIS: HOW DO WE STAY COHERENT?

## Startup

At least the worker pool and the Gene Pool must be started before any evolution can take place.

## Storage

The (crude) intent of storage scale design in Erasmus GP is to *be able to* manage up to:

- Worker 1st level cache: 1MB
- Worker 2nd level cache: 1GB
- Gene Pool: 1TB
- Gene Pool archive: 1PB
- Biome: 1PB

Obviously implementation details (such as storage medium capacity) will impose its own, and likely lower, limits.
