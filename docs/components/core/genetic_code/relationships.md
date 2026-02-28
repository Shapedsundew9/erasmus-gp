# Genetic Code Relationship Networks

GCs are connected to other GCs by up to 3 relationship networks: the problem network, the PGC network, and the ancestor network. All GCs except codons have ancestors, and by definition they are one step away from their parents and two from their siblings, more so from their half siblings and so on. They are also, more distantly, related to GCs created by their descendants.

```mermaid
%%{init: { 'theme': 'dark', 'themeVariables': { 'lineColor': '#6c7a89', 'textColor': '#edf2f4', 'mainBkg': '#2b2d42', 'primaryBorderColor': '#4a4e69' }}}%%
flowchart
    %% Base/Default (Dark Slate)
    classDef default fill:#2b2d42,stroke:#4a4e69,stroke-width:2px,color:#edf2f4
    classDef dataBlue fill:#3a506b,stroke:#5c6b73,stroke-width:2px,color:#ffffff
    classDef dataGreen fill:#425c52,stroke:#5d7a6f,stroke-width:2px,color:#ffffff
    classDef dataGold fill:#6e6246,stroke:#8f8160,stroke-width:2px,color:#ffffff
    classDef dataNavy fill:#2c3e50,stroke:#4a5c6e,stroke-width:2px,color:#ffffff

    GC(("GC")):::dataNavy --> P["Problems"]:::dataBlue
    P --> GC0(("GCs")):::dataBlue
    GC --> PGC["PGC"]:::dataGold
    PGC --> GC1(("GCs")):::dataGold
    GC --> AN["Ancestors"]:::dataGreen
    AN --> GC2(("GCs")):::dataGreen
```
