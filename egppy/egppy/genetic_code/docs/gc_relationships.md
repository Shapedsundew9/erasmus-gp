# Genetic Code Relationship Networks

GCs are connected to other GCs by up to 3 relationship networks: the problem network, the PGC network, and the ancestor network. All GCs except codons have ancestors, and by definition they are one step away from their parents and two from their siblings, more so from their half siblings and so on. They are also, more distantly, related to GCs created by their descendants.

```mermaid
---
title: Genetic Code Relationship Networks
---

flowchart
    GC(("GC")) --> P["Problems"]:::blue
    P --> GC0(("GCs")):::blue
    GC --> PGC["PGC"]:::red
    PGC --> GC1(("GCs")):::red
    GC --> AN["Ancestors"]:::green
    AN --> GC2(("GCs")):::green
    classDef red fill:#882222,stroke:#333,stroke-width:1px
    classDef green fill:#228822,stroke:#333,stroke-width:1px
    classDef blue fill:#222288,stroke:#333,stroke-width:1px
```
