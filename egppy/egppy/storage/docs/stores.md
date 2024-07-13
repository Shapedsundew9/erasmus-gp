# Genetic Code Storage

The evolution process needs to be fast and scalable. Erasmus GP generates huge numbers of GCs and the balance between accessibility, speed of access and genetic mixing must be considered.

```mermaid
---
title: GC Storage
---
flowchart TB
    subgraph LOCAL["Local Python Process"]
        L["Logic"]
        A["fast_cache(CacheABC)"]
        subgraph CACHE["genetic_code_cache(CacheABC)"]
            B["compact_cache(CacheABC)"]
            C["remote_cache_client(CacheABC)"]
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
    L <--> B
    A --> B
    B <--> C
    C <--> D
    D <--> E
    E <--> F
    F <--> G
    G <--> H
```

## Stores

Stores are all derived from the Abstract Base Class *StoreABC* which provide a dictionary like interface for storing *StorableObj*s in a data structure aka store e.g. database, file or compact memory store. Store's exist to implement the EGP runtime object verification and consistency philosophy and provide a common interface to data storage technologies (and thier space/performance/remoteness tradeoffs). Stores are typically tightly bound to the storable objects they store.

Stores work with storable objects modified() method to efficiently store only those fields that have been modified. For the store is is not mandatory to use the method but it is required
for the storable object to implement it (even if it returns a constant tuple of all the fields). In addition storable objects are required to provide a method to convert the object to JSON compatible builtin python types and be initialised by the same object structure i.e. type(self)(self.to_json()) == self shall be True for StorableObjABC types.

## Caches

Caches are all derived from the Abstract Base Class *CacheABC* which provides a dictionary like interface plus a few other cache like methods. CacheABC is derived from StoreABC. A cache is a store that and pushes and pulls *CacheableObjABC* types to/from a next level store or cache. There are two different implementation behaviors of caches determined by the configuration.

| Behavior | ABC | max_items | purge_count | Description |
|-------|:------------:|:----:|:-------------:|---------|
| Dirty Cache | CacheABC | 0 | 0 | Fast access with limitless space requiring manual purging of items to the next_level. No items can be pulled from the next_level into the cache. |
| Cache | CacheABC | >= 1 | >= 1 | Quite fast. If the cache has max_items in it and a new object is added it will first push purge_count items to the next_level. Items that have been purged or initially exists in the next_level will be pulled in automatically if accessed via the cache interface. |

Caches cache *CacheableObjABC* types. Because the object cached is a container there is no way for the CacheABC to know if the object it is caching has been accessed or changed without some sort of expensive checking or comparison or hashing. CacheableObjABC's have methods provided to explicitly and implicitly track access and set dirty/clean state that can be introspected by CacheABC's. CacheableObjABC's may include other CacheableObjABC's using the same methods to roll up state.

## Implementations

\* A fast cache is a Dirty Cache, like a temporary store with some convinient configuration to push data to the next level. It cannot pull data from the next level (see one way arrow between the fast_cache and the compact_cache in the top level store flow diagram). In order to use all the optimized builtin dict methods without wrappers, a FastCache does not track access order or dirty state and has no size limit. It is intended as a "work area" for evolution.

## Class Hierarchy

```mermaid
---
title: Storage & Cache Class Diagram
---
classDiagram
    MutableMapping <|-- StoreABC
    StoreABC <|-- NullStore
    StoreABC <|-- JSONFileStore
    StoreABC <|-- CacheABC
    CacheABC <|-- DictCache
    CacheABC <|-- UserDictCache
```

```mermaid
---
title: Storable & Cacheable Object Class Diagram
---
classDiagram
    ABC <|-- StorableObjABC
    StorableObjABC <|-- CacheableObjABC
    dict <|-- CacheableDirtyDict
    CacheableObjABC <|-- CacheableDirtyDict
    CacheableObjABC <|-- CacheableDirtyList
    list <|-- CacheableDirtyList
    CacheableDirtyDict <|-- CacheableDict
    CacheableDirtyList <|-- CacheableList
```

```mermaid
---
title: Storable & Cacheable Object Class Diagram
---
classDiagram
    ABC <|-- StorableObjABC
    StorableObjABC <|-- CacheableObjABC
    MutableSequence <|-- InterfaceABC
    CacheableObjABC <|-- InterfaceABC
    CacheableObjABC <|-- GCABC
    MutableMapping <|-- GCABC
    GCABC <|-- DirtyDictBaseGC
    dict <|--  DirtyDictBaseGC
    UserDict <|-- DictBase
    GCABC <|-- DictBase
    DictBase <|-- DictBaseGC
    DirtyDictBaseGC <|-- DirtyDictUGC
    DictBaseGC <|-- DictUGC
    DirtyDictBaseGC <|-- DirtyDictEGC
    DictBaseGC <|-- DictEGC
```

```mermaid
---
title: Cache Class Diagram
---
classDiagram
    MutableMapping <|-- StoreABC
    StoreIllegal <|-- CacheABC
    StoreABC <|-- CacheABC
    CacheIllegal <|-- dict_likeCache
    dict_like <|-- dict_likeCache
    CacheABC <|-- dict_likeCache
    CacheBase <|-- dict_likeCache
```