# Genetic Code Relationship Networks

GC's are connected to other GC's by up to 3 relationship networks. The problem network, the PGC network and the ancestor network. All GC's except codons have ancestors and by definition they are one step away from thier parents and two from thier siblings, more so from thier half siblings and so on. They are also, more distantly, related to GC's created 

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