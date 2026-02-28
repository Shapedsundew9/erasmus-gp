# GC Insertion

Insertion of a GC into another GC falls into one of three categories:

- **Stacking**.Stacking one GC on top of the other and wrapping it in a new resultant GC.
- **Wrapping**. The graph of a GC has its IO interface replaced with that of an Empty GC.
- **Restructuring**: A Resultant GC and a Fetal GC will be required.

## Limitations

There are limitations as to which GC's may be stacked, wrapped or restructured. This is determined by the type of graph they have.

| Graph Type | Stack | Wrap | Restructure |
| ------------ | :-----: | :----: | :-----------: |
| Standard | X | X | X |
| Conditional | X | X | X |
| Loop | X | X | X |
| Codon | X | X | - |
| Empty | - | - | - |

- **X** = allowed
- **-** = _not_ allowed

## Definitions

| Term | Definition |
| ------ | ------------ |
| RGC | Resultant GC. The GC product of the insertion operation |
| TGC | Target GC. The GC to be inserted into. |
| IGC | Inerstion GC. The GC inserted into TGC to make RGC. |
| FGC | The fetal GC. A secondary GC created as part of the insertion. |
| xGC[y] | A specific row where x is one of RTIF and y is a row letter. |
| xGC[yc] | Used in an I or O row definition. x & y defined as above. 'c' identifies the original target or insertion GC source or destination interface definition but the interface may be used as either in the resultant or fetal GC. |
| xGC[y] + wGC[z] | Used in an I or O row deinition. x & y defined as above. w & z defined the same as x & y. Interface row is the concatenation, in order, of the specified rows. |
| `#001000` | Background color for the RGC. |
| `#604000` | Background color for a row created from an existing interface. |
| `#300000` | Background color for new row definition. |
| `#000000` | Background color for unchanged row or interface. |

In any insertion event TGC and IGC are not modified RGC and any FGC are new GC's with copies of TGC & IGC data as specified in the following sections.

### Connectivity

When an insertion occurs the Principle of Least Exposure as applied which means that interfaces are preserved and no assumption is made about why the insertion occured nor what is to connect to the input interface of the IGC. In primordial evolution the reason will typically be stablisation and IGC will perfom some role in dealing with unconnected endpoints. The diagrams defining the insertion cases define what interfaces are exposed and only what connections are preserved (which may be through an interafce if an FGC is created). Further connectivity required for stabilisation or genetic code design is the responsibility of the calling function.

## Stacking

There are 2 stacking cases: Stack and Inverse Stack. Stacking cases are symmetrical TGC:IGC or (inverse) IGC:TGC.

### Case 0: Stack

```mermaid
%%{init: { 'theme': 'dark', 'themeVariables': { 'lineColor': '#6c7a89', 'textColor': '#edf2f4', 'mainBkg': '#2b2d42', 'primaryBorderColor': '#4a4e69' }}}%%
flowchart TB
    %% Base/Default (Dark Slate)
    classDef default fill:#2b2d42,stroke:#4a4e69,stroke-width:2px,color:#edf2f4
    classDef dataBlue fill:#3a506b,stroke:#5c6b73,stroke-width:2px,color:#ffffff
    classDef dataGreen fill:#425c52,stroke:#5d7a6f,stroke-width:2px,color:#ffffff
    classDef dataGold fill:#6e6246,stroke:#8f8160,stroke-width:2px,color:#ffffff
    classDef dataTeal fill:#3b5e60,stroke:#5b7a7c,stroke-width:2px,color:#ffffff
    classDef dataOlive fill:#525c42,stroke:#6f7a5d,stroke-width:2px,color:#ffffff
    classDef dataNavy fill:#2c3e50,stroke:#4a5c6e,stroke-width:2px,color:#ffffff
    classDef zonePrimary fill:#1f2130,stroke:#3a3e59,stroke-width:2px,stroke-dasharray: 5 5

    I["I: IGC[Is]"]:::dataOlive
    subgraph RGC
        direction RL
        GCA["A: IGC"]:::dataNavy
        GCB["B: TGC"]:::dataNavy
    end
    O["O: TGC[Od]"]:::dataOlive
    I --> RGC --> O

    class RGC zonePrimary
```

### Case 1: Inverse Stack

```mermaid
%%{init: { 'theme': 'dark', 'themeVariables': { 'lineColor': '#6c7a89', 'textColor': '#edf2f4', 'mainBkg': '#2b2d42', 'primaryBorderColor': '#4a4e69' }}}%%
flowchart TB
    %% Base/Default (Dark Slate)
    classDef default fill:#2b2d42,stroke:#4a4e69,stroke-width:2px,color:#edf2f4
    classDef dataBlue fill:#3a506b,stroke:#5c6b73,stroke-width:2px,color:#ffffff
    classDef dataGreen fill:#425c52,stroke:#5d7a6f,stroke-width:2px,color:#ffffff
    classDef dataGold fill:#6e6246,stroke:#8f8160,stroke-width:2px,color:#ffffff
    classDef dataTeal fill:#3b5e60,stroke:#5b7a7c,stroke-width:2px,color:#ffffff
    classDef dataOlive fill:#525c42,stroke:#6f7a5d,stroke-width:2px,color:#ffffff
    classDef dataNavy fill:#2c3e50,stroke:#4a5c6e,stroke-width:2px,color:#ffffff
    classDef zonePrimary fill:#1f2130,stroke:#3a3e59,stroke-width:2px,stroke-dasharray: 5 5

    I["I: TGC[Is]"]:::dataOlive
    subgraph RGC
        direction LR
        GCA["A: TGC"]:::dataNavy
        GCB["B: IGC"]:::dataNavy
    end
    O["O: IGC[Od]"]:::dataOlive
    I --> RGC --> O

    class RGC zonePrimary
```

## Wrapping

There is only one wrapping case. An Empty TGC can wrap the graph of a Standard IGC by replacing its input and output interface with its own.

### Case 2

```mermaid
%%{init: { 'theme': 'dark', 'themeVariables': { 'lineColor': '#6c7a89', 'textColor': '#edf2f4', 'mainBkg': '#2b2d42', 'primaryBorderColor': '#4a4e69' }}}%%
flowchart TB
    %% Base/Default (Dark Slate)
    classDef default fill:#2b2d42,stroke:#4a4e69,stroke-width:2px,color:#edf2f4
    classDef dataBlue fill:#3a506b,stroke:#5c6b73,stroke-width:2px,color:#ffffff
    classDef dataGreen fill:#425c52,stroke:#5d7a6f,stroke-width:2px,color:#ffffff
    classDef dataGold fill:#6e6246,stroke:#8f8160,stroke-width:2px,color:#ffffff
    classDef dataTeal fill:#3b5e60,stroke:#5b7a7c,stroke-width:2px,color:#ffffff
    classDef dataOlive fill:#525c42,stroke:#6f7a5d,stroke-width:2px,color:#ffffff
    classDef dataNavy fill:#2c3e50,stroke:#4a5c6e,stroke-width:2px,color:#ffffff
    classDef zonePrimary fill:#1f2130,stroke:#3a3e59,stroke-width:2px,stroke-dasharray: 5 5

    I["I: TGC[Is]"]:::dataOlive
    subgraph RGC
        direction TB
        GCA["A: IGC[A]"]:::dataNavy
        GCB["B: IGC[B]"]:::dataNavy
    end
    O["O: TGC[Od]"]:::dataOlive
    I --> RGC --> O
    GCA --Preserved--> GCB

    class RGC zonePrimary
```

## Restructuring

Restructuring GC's produces a resultant GC that is functionally identical to the target GC, including identical interfaces. However it does not guarantee a stable GC.

### Case 3

Insert IGC above A

```mermaid
%%{init: { 'theme': 'dark', 'themeVariables': { 'lineColor': '#6c7a89', 'textColor': '#edf2f4', 'mainBkg': '#2b2d42', 'primaryBorderColor': '#4a4e69' }}}%%
flowchart TB
    %% Base/Default (Dark Slate)
    classDef default fill:#2b2d42,stroke:#4a4e69,stroke-width:2px,color:#edf2f4
    classDef dataBlue fill:#3a506b,stroke:#5c6b73,stroke-width:2px,color:#ffffff
    classDef dataGreen fill:#425c52,stroke:#5d7a6f,stroke-width:2px,color:#ffffff
    classDef dataGold fill:#6e6246,stroke:#8f8160,stroke-width:2px,color:#ffffff
    classDef dataTeal fill:#3b5e60,stroke:#5b7a7c,stroke-width:2px,color:#ffffff
    classDef dataOlive fill:#525c42,stroke:#6f7a5d,stroke-width:2px,color:#ffffff
    classDef dataNavy fill:#2c3e50,stroke:#4a5c6e,stroke-width:2px,color:#ffffff
    classDef zonePrimary fill:#1f2130,stroke:#3a3e59,stroke-width:2px,stroke-dasharray: 5 5
    classDef zoneExternal fill:#221f2e,stroke:#4a3b52,stroke-width:2px,stroke-dasharray: 5 5

    I1["I: TGC[Is]"]:::dataOlive
    subgraph RGC
        direction RL
        GCA1["A: FGC"]:::dataNavy
        GCB1["B: TGC[B]"]:::dataNavy
    end
    O1["O: TGC[Od]"]:::dataOlive
    I1 --Preserved-->GCA1
    I1 --Preserved-->GCB1
    GCA1 --Preserved-->GCB1
    GCB1 --Preserved--> O1

    I2["I: TGC[Ad]"]:::dataOlive
    subgraph FGC
        direction RL
        GCA2["A: IGC"]:::dataGold
        GCB2["B: TGC[A]"]:::dataGold
    end
    O2["O: TGC[As]"]:::dataOlive
    I2 --Preserved--> GCB2
    GCB2 --Preserved--> O2

    class RGC zonePrimary
    class FGC zoneExternal
```

### Case 4

Insert IGC above B

```mermaid
%%{init: { 'theme': 'dark', 'themeVariables': { 'lineColor': '#6c7a89', 'textColor': '#edf2f4', 'mainBkg': '#2b2d42', 'primaryBorderColor': '#4a4e69' }}}%%
flowchart TB
    %% Base/Default (Dark Slate)
    classDef default fill:#2b2d42,stroke:#4a4e69,stroke-width:2px,color:#edf2f4
    classDef dataBlue fill:#3a506b,stroke:#5c6b73,stroke-width:2px,color:#ffffff
    classDef dataGreen fill:#425c52,stroke:#5d7a6f,stroke-width:2px,color:#ffffff
    classDef dataGold fill:#6e6246,stroke:#8f8160,stroke-width:2px,color:#ffffff
    classDef dataTeal fill:#3b5e60,stroke:#5b7a7c,stroke-width:2px,color:#ffffff
    classDef dataOlive fill:#525c42,stroke:#6f7a5d,stroke-width:2px,color:#ffffff
    classDef dataNavy fill:#2c3e50,stroke:#4a5c6e,stroke-width:2px,color:#ffffff
    classDef zonePrimary fill:#1f2130,stroke:#3a3e59,stroke-width:2px,stroke-dasharray: 5 5
    classDef zoneExternal fill:#221f2e,stroke:#4a3b52,stroke-width:2px,stroke-dasharray: 5 5

    I1["I: TGC[I]"]:::dataOlive
    subgraph RGC
        direction RL
        GCA1["A: TGC[A]"]:::dataNavy
        GCB1["B: FGC"]:::dataNavy
    end
    O1["O: TGC[O]"]:::dataOlive
    I1 --Preserved-->GCA1
    I1 --Preserved-->GCB1
    GCA1 --Preserved-->GCB1
    GCB1 --Preserved--> O1

    I2["I: TGC[Bd]"]:::dataOlive
    subgraph FGC
        direction RL
        GCA2["A: IGC"]:::dataGold
        GCB2["B: TGC[B]"]:::dataGold
    end
    O2["O: TGC[Bs]"]:::dataOlive
    I2 --Preserved--> GCB2
    GCB2 --Preserved--> O2

    class RGC zonePrimary
    class FGC zoneExternal
```

### Case 5

Insert IGC above O

```mermaid
%%{init: { 'theme': 'dark', 'themeVariables': { 'lineColor': '#6c7a89', 'textColor': '#edf2f4', 'mainBkg': '#2b2d42', 'primaryBorderColor': '#4a4e69' }}}%%
flowchart TB
    %% Base/Default (Dark Slate)
    classDef default fill:#2b2d42,stroke:#4a4e69,stroke-width:2px,color:#edf2f4
    classDef dataBlue fill:#3a506b,stroke:#5c6b73,stroke-width:2px,color:#ffffff
    classDef dataGreen fill:#425c52,stroke:#5d7a6f,stroke-width:2px,color:#ffffff
    classDef dataGold fill:#6e6246,stroke:#8f8160,stroke-width:2px,color:#ffffff
    classDef dataTeal fill:#3b5e60,stroke:#5b7a7c,stroke-width:2px,color:#ffffff
    classDef dataOlive fill:#525c42,stroke:#6f7a5d,stroke-width:2px,color:#ffffff
    classDef dataNavy fill:#2c3e50,stroke:#4a5c6e,stroke-width:2px,color:#ffffff
    classDef zonePrimary fill:#1f2130,stroke:#3a3e59,stroke-width:2px,stroke-dasharray: 5 5
    classDef zoneExternal fill:#221f2e,stroke:#4a3b52,stroke-width:2px,stroke-dasharray: 5 5

    I1["I: TGC[I]"]:::dataOlive
    subgraph RGC
        direction RL
        GCA1["A: TGC[A]"]:::dataNavy
        GCB1["B: FGC"]:::dataNavy
    end
    O1["O: TGC[O]"]:::dataOlive
    I1 --Preserved-->GCA1
    I1 --Preserved-->GCB1
    GCA1 --Preserved-->GCB1
    GCB1 --Preserved--> O1

    I2["I: TGC[Bd]"]:::dataOlive
    subgraph FGC
        direction RL
        GCA2["A: TGC[B]"]:::dataGold
        GCB2["B: IGC"]:::dataGold
    end
    O2["O: TGC[Bs]"]:::dataOlive
    I2 --Preserved--> GCA2
    GCA2 --Preserved--> O2

    class RGC zonePrimary
    class FGC zoneExternal
```
