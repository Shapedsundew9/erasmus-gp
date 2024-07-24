# GC Graphs

A Genetic Code graph defines how values from the GC input are passed to sub-GC's and outputs from sub-GC's
(and directly from the input) are connected to the GC's outputs. There are 4 types of GC Graph.

| Type | Comments |
|------|------------|
| Standard | Connects two sub-GC's together to make a new GC. This is by far the most common type.|
| Conditional | Chooses an execution path through one of the sub-GCs based on an input boolean. |
| Codon | Defines an interface & represents a primitive operator such addition or a constant. Has no sub-GC's. |
| Empty | Defines an interface. Has no sub-GCs and generates no code. Used to seed problems. |

## Row Requirements

Note that both GCA and GCB are present or neither are present. This simplifies the rules for insertion.

| Type | I | F | A | B | O | P |
|------|---|---| ---|---|---|---|
| Standard | X | - | X | X | X | - |
| Conditional | X | X | X | X | X | X |
| Codon | X | - | - | - | X | - |
| Empty | X | - | - | - | X | - |

- **X** = Must be present i.e. have at least 1 endpoint.
- **-** = Must _not_ be present

## Connectivity Requirements

Codons and Empty graphs have no connections only Input and Output row definitions i.e. an IO interface definition. Standard and Conditional graphs have connections between row interfaces but not all combinations are permitted. In the matrix below the source of the connection is the column label and the destination of the connection is the row label.

| Dst | I | F | A | B | O | P |
|------|---|---|---|---|---|---|
|  I  | - | - | - | - | - | - |
| F | <u>C</u> | - | - | - | - | - |
|  A  | <u>SC</u> | - |  - | - | - | - |
|  B  | S<u>C</u> | - | S | - | - | - |
|  O  | SC | - | S<u>C</u> | <u>S</u> | - | - |
|  P  | C | - | - | <u>C</u> | - | - |

- **S** = Allowed in a Standard graph
- **C** = Allowed in a Conditional graph
- **-** = Not allowed in any case
- **<u>X</u>** = Required connection

Note that the required connections are a consequence of the rule that an interface must have at least 1 endpoint and all destination endpoints must be connected to a source. In all of these cases only one row is capable of connecting to the other and so the connection must exist.

Flow charts of the allowed connectivity standard and conditional graphs are below.

- Solid arrow links are required.
- Dashed arrow links are allowed.

### Standard Connectivity Graph

```mermaid
%% Standard GC
flowchart TB
    I["[I]nputs"]
    A["GC[A]"]
    B["GC[B]"]
    O["[O]utputs"]
    A -.-> O
    I --> A -.-> B --> O
    I -.-> B
    I -.-> O
    
    
classDef Icd fill:#999,stroke:#333,stroke-width:1px
classDef Acd fill:#900,stroke:#333,stroke-width:1px
classDef Bcd fill:#009,stroke:#333,stroke-width:1px
classDef Ocd fill:#000,stroke:#333,stroke-width:1px

class I Icd
class A Acd
class B Bcd
class O Ocd
```

### Conditional Connectivity Graph

```mermaid
%% Conditional GC
flowchart TB
    I["[I]nputs"]
    F["i[F]"]
    A["GC[A]"]
    B["GC[B]"]
    O["[O]utputs"]
    P["Out[P]uts"]
    I --> F
    I --> A --> O
    B --> P
    I --> B
    I -.-> O
    I -.-> P
    
classDef Icd fill:#999,stroke:#333,stroke-width:1px
classDef Acd fill:#900,stroke:#333,stroke-width:1px
classDef Bcd fill:#009,stroke:#333,stroke-width:1px
classDef Ocd fill:#000,stroke:#333,stroke-width:1px
classDef Pcd fill:#099,stroke:#333,stroke-width:1px

class I Icd
class A Acd
class B Bcd
class O Ocd
class P Pcd
```

### Codon & Empty Connectivity Graphs

There are no connections.

```mermaid
%% Codon & Empty GC
flowchart LR
    I["[I]nputs"]
    O["[O]utputs"]
    
classDef Icd fill:#999,stroke:#333,stroke-width:1px
classDef Ocd fill:#000,stroke:#333,stroke-width:1px

class I Icd
class O Ocd
```

## JSON Format

TO DO: Explain more
In row U the connections are stored in alphabetical order, then index order. This is specified for reproducablility.

## Rows, Interfaces & Connections

An interface is an array of endpoints with 0 to 256 elements each defining the endpoint type.
A Genetic Code has two interfaces, the input and the output interface. When viewed from within the
GC Graph the input interface is a source interface i.e. it is a source of connections
to other rows, and the output interface a destination interface. Row A and row B represent the input
and output interfaces to GCA and GCB reprectively. Within the graph though GCA's input interface is
a destination and its output a source.

### Source Interfaces

Source interface endpoints may have 0, 1 or many connections to destination interface endpoints (but
only one connection to the same destination endpoint).

### Destination Interfaces

All destination interface endpoints must be connected to one (and only one) source interface endpoint.
