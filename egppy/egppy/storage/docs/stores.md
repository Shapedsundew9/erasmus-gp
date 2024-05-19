# Genetic Code Storage

The evolution process needs to be fast and scalable. Erasmus GP generates huge numbers of GCs and the balance between accessibility, speed of access and genetic mixing must be considered.


```mermaid
---
title: GC Storage
---
flowchart TB
    subgraph LOCAL["Local Python Process"]
        L["Logic"]
        subgraph CACHE["GeneticCodeCache(CacheABC)"]
            A["FastCache(CacheABC)"]
            B["CompactCache(CacheABC)"]
            C["RemoteCacheClient(CacheABC)"]
        end
    end
    subgraph REMOTE["GC Cache Chart"]
        D[Remote Cache]
        E[DB REST Client]
    end
    subgraph DB["Database Chart"]
        F[DB REST API]
        G[Postgresql]
        H[DB REST Client]
    end
    L <--> A
    A <--> B
    B <--> C
    C <--> D
    D <--> E
    E <--> F
    F <--> G
    G <--> H
```
