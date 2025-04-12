# GC Insertion

Insertion of a GC into another GC falls into one of three categories:

- **Stacking**.Stacking one GC on top of the other and wrapping it in a new resultant GC.
- **Wrapping**. The graph of a GC has its IO interface replaced with that of an Empty GC.
- **Restructuring**: A Resultant GC and a Fetal GC will be required.

## Limitations

There are limitations as to which GC's may be stacked, wrapped or restructured. This is determined by the type of graph they have.

| Graph Type | Stack | Wrap | Restructure |
|------------|:-----:|:----:|:-----------:|
| Standard | X | X | X|
| Conditional | X | - | - |
| Codon | X | - | - |
| Empty | - | - | - |

- **X** = allowed
- **-** = _not_ allowed

## Definitions

| Term | Definition |
|------|------------|
| RGC  | Resultant GC. The GC product of the insertion operation |
| TGC  | Target GC. The GC to be inserted into. |
| IGC  | Inerstion GC. The GC inserted into TGC to make RGC. |
| FGC  | The fetal GC. A secondary GC created as part of the insertion. |
| xGC[y] | A specific row where x is one of RTIF and y is a row letter. |
| xGC[yc] | Used in an I or O row definition. x & y defined as above. 'c' identifies that only connected endpoints of the original row are part of the interface. See section below. |
| xGC[y] + wGC[z] | Used in an I or O row deinition. x & y defined as above. w & z defined the same as x & y. Interface row is the concatenation, in order, of the specified rows. |
| `#001000` | Background color for the RGC.|
| `#604000` | Background color for a row created from an existing interface. |
| `#300000` | Background color for new row definition. |
| `#000000` | Background color for unchanged row or interface. |

In any insertion event TGC and IGC are not modified RGC and any FGC are new GC's with copies of TGC & IGC data as specified in the following sections.

### xGC[yc] Interface Definition

The xGC[yc] interface is critical to stabilization of of Connection Graphs. Consider an unstable graph where there is an unconnected GCA destination end point because row I does not have a matching type. To fix this situation a GC must be inserted above row A that has the missing source end point type (Case 4 defined below). To give the maximum likihood of stability and the minimum distruption for the resultant RGC and FGC the following needs to happen:

- The low index FGC outputs (row O) must be the same as TGC[GCA]
- The the connections in TGC to GCA destinations must persist to GCA in FGC
- Any TGC[I] end points that match IGC destination must be passed in to FGC

In this way existing connections from the original TGC are guaranteed and IGC has the maximum opportunity to resolve the original instability without creating a new instability (with somewhat careful selection of IGC the risks collapse a great deal if not entirely).

NB: IGC[O] is appended to TGC[GCA] source endpoints to make FGC[O] to maximise the exposure of IGC outputs.

## Stacking

There are 2 stacking cases: Stack and Inverse Stack. Stacking cases are symmetrical TGC:IGC or (inverse) IGC:TGC.

### Case 0: Stack

```mermaid
%% Insertion Case 0: Stack
flowchart TB
    I["IGC[I]"]
    subgraph RGC
        direction RL
        GCA["A: IGC"]
        GCB["B: TGC"]
    end
    O["TGC[O]"]
    I --> RGC --> O

classDef newGC fill:#010,stroke:#333,stroke-width:4px
classDef newRow fill:#010,stroke:#333,stroke-width:1px
classDef modified fill:#640,stroke:#333,stroke-width:1px
classDef unchanged fill:#000,stroke:#333,stroke-width:1px

class RGC newGC
class GCA modified
class GCB modified
```

### Case 1: Inverse Stack

```mermaid
%% Insertion Case 1: Inverse Stack
flowchart TB
    I["TGC[I]"]
    subgraph RGC
        direction RL
        GCA["A: TGC"]
        GCB["B: IGC"]
    end
    O["IGC[O]"]
    I --> RGC --> O

classDef newGC fill:#010,stroke:#333,stroke-width:4px
classDef newRow fill:#010,stroke:#333,stroke-width:1px
classDef modified fill:#640,stroke:#333,stroke-width:1px
classDef unchanged fill:#000,stroke:#333,stroke-width:1px

class RGC newGC
class GCA modified
class GCB modified
```

## Wrapping

There is only one wrapping case. An Empty TGC can wrap the graph of a Standard IGC by replacing its input and output interface with its own.

### Case 2

```mermaid
%% Insertion Case 2: Wrap
flowchart TB
    I["TGC[I]"]
    subgraph RGC
        direction RL
        GCA["A: IGC[A]"]
        GCB["B: IGC[B]"]
    end
    O["TGC[O]"]
    I --> RGC --> O

classDef newGC fill:#010,stroke:#333,stroke-width:4px
classDef newRow fill:#010,stroke:#333,stroke-width:1px
classDef modified fill:#640,stroke:#333,stroke-width:1px
classDef unchanged fill:#000,stroke:#333,stroke-width:1px

class RGC newGC
class GCA modified
class GCB modified
```

## Restructuring

### Case 3

Insert IGC above A

```mermaid
%% Insertion Case 3
flowchart TB
    I1["TGC[I]"]
    subgraph RGC
        direction RL
        GCA1["A: FGC"]
        GCB1["B: TGC[B]"]
    end
    O1["TGC[O]"]
    I1 --> RGC --> O1

    I2["TGC[Ac]"]
    subgraph FGC
        direction RL
        GCA2["A: IGC"]
        GCB2["B: TGC[A]"]
    end
    O2["TGC[A] + IGC[O]"]
    I2 --> FGC --> O2

classDef newGC fill:#010,stroke:#333,stroke-width:4px
classDef newRow fill:#300,stroke:#333,stroke-width:1px
classDef modified fill:#640,stroke:#333,stroke-width:1px
classDef unchanged fill:#000,stroke:#333,stroke-width:1px

class RGC newGC
class GCB1 unchanged
class GCA1 newRow
class FGC newGC
class GCA2 modified
class GCB2 modified
class I1 unchanged
class I2 newRow
class O1 unchanged
class O2 newRow
```

### Case 4

Insert IGC above B

```mermaid
%% Insertion Case 4
flowchart TB
    I1["TGC[I]"]
    subgraph RGC
        direction RL
        GCA1["A: FGC"]
        GCB1["B: TGC[B]"]
    end
    O1["TGC[O]"]
    I1 --> RGC --> O1

    I2["TGC[Ac]"]
    subgraph FGC
        direction RL
        GCA2["A: TGC[A]"]
        GCB2["B: IGC"]
    end
    O2["TGC[A] + IGC[O]"]
    I2 --> FGC --> O2

classDef newGC fill:#010,stroke:#333,stroke-width:4px
classDef newRow fill:#300,stroke:#333,stroke-width:1px
classDef modified fill:#640,stroke:#333,stroke-width:1px
classDef unchanged fill:#000,stroke:#333,stroke-width:1px

class RGC newGC
class GCB1 unchanged
class GCA1 newRow
class FGC newGC
class GCA2 modified
class GCB2 modified
class I1 unchanged
class I2 newRow
class O1 unchanged
class O2 newRow
```

### Case 5

Insert IGC above O

```mermaid
%% Insertion Case 5
flowchart TB
    I1["TGC[I]"]
    subgraph RGC
        direction RL
        GCA1["A: TGC[A]"]
        GCB1["B: FGC"]
    end
    O1["TGC[O]"]
    I1 --> RGC --> O1

    I2["TGC[Bc]"]
    subgraph FGC
        direction RL
        GCA2["A: TGC[B]"]
        GCB2["B: IGC"]
    end
    O2["TGC[B] + IGC[O]"]
    I2 --> FGC --> O2

classDef newGC fill:#010,stroke:#333,stroke-width:4px
classDef newRow fill:#300,stroke:#333,stroke-width:1px
classDef modified fill:#640,stroke:#333,stroke-width:1px
classDef unchanged fill:#000,stroke:#333,stroke-width:1px

class RGC newGC
class GCA1 unchanged
class GCB1 newRow
class FGC newGC
class GCA2 modified
class GCB2 modified
class I1 unchanged
class I2 newRow
class O1 unchanged
class O2 newRow
```
