# Connection Graphs

A Genetic Code graph defines how values from the GC input are passed to sub-GC's and outputs from sub-GC's
(and directly from the input) are connected to the GC's outputs. There are 7 types of Connection Graph.

| Type | GC Type | Comments |
| :--- | :--- | :--- |
| **If-Then** | Ordinary | Conditional graph with a single execution path (GCA) chosen when condition is true. |
| **If-Then-Else** | Ordinary | Conditional graph with two execution paths (GCA/GCB) chosen based on condition. |
| **Empty** | Ordinary | Defines an interface. Has no sub-GCs and generates no code. Used to seed problems. |
| **For-Loop** | Ordinary | Loop graph that iterates over an iterable, executing GCA for each element. |
| **While-Loop** | Ordinary | Loop graph that executes GCA while a condition remains true. |
| **Standard** | Ordinary | Connects two sub-GC's together to make a new GC. This is by far the most common type. |
| **Primitive** | Codon, Meta | Simplified graph representing a primitive operator (e.g., addition, logical OR). Has no sub-GC's. |

## Row Requirements

All Connection Graphs may have either an input interface or an output interface or both but cannot have neither.
GC's with just inputs store data in memory, more persistent storage or send it to a peripheral. GC's that
just have an output interface are constants, read from memory, storage or peripherals.

### Row Definitions

* **I** = Input interface (source)
* **F** = Condition evaluation destination (for conditionals)
* **L** = Loop iterable destination (for loops) and loop object source
* **S** = Loop state destination (input) and source (output) - for both loop types
* **T** = Loop next-state destination - for both loop types
* **W** = While loop condition state destination (input) and source (output) - boolean only
* **X** = While loop next-condition destination - boolean only
* **A** = GCA input (destination) / GCA output (source)
* **B** = GCB input (destination) / GCB output (source)
* **O** = Output interface (destination)
* **P** = Alternate output interface (destination) - used when condition is false. (Not used for loops).
* **U** = Unconnected source endpoints (destination) - JSON format only

Note that row *P* only exists logically. It is the same interface as row O i.e. the functions return value (which is why it must have the same structure as row O), but the execution path to the physical return interface is different for row *O* and row *P* allowing conditional execution.

Similarly, rows *T* and *X* are semantically identical to *S* and *W* respectively, but serve as destination endpoints for loop body outputs while *S* and *W* serve as source endpoints providing state to the loop body. The implicit feedback connection from *Td→Ss* and *Xd→Ws* between iterations is handled in code generation, not the connection graph.

| Type | I | F | L | S | T | W | X | A | B | O | P | U |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **If-Then** | X | X | - | - | - | - | - | X | - | M | M | m |
| **If-Then-Else** | X | X | - | - | - | - | - | X | X | M | M | m |
| **Empty** | o | - | - | - | - | - | - | - | - | o | - | m |
| **For-Loop** | X | - | X | m | m | - | - | X | - | M | - | m |
| **While-Loop** | X | - | - | m | m | X | X | X | - | M | - | m |
| **Standard** | o | - | - | - | - | - | - | X | X | o | - | m |
| **Primitive** | o | - | - | - | - | - | - | X | - | o | - | - |

* **X** = Must be present i.e. have at least 1 endpoint for that row.
* **-** = Must *not* be present
* **o** = Must have at least 1 endpoint in the set of rows.
* **M** = May be present and must be the same on each row.
* **m** = May be present.

## Connectivity Requirements

Empty and Primitive graphs have limited connections. If-Then, If-Then-Else, For-Loop, While-Loop, and Standard graphs have connections between row interfaces but not all combinations are permitted. In the matrix below the source of the connection is the column label and the destination of the connection is the row label.

| Dst\Src | I | L | S | W | A | B |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **F** | IT,IE | - | - | - | - | - |
| **L** | FL | - | - | - | - | - |
| **S** | FL,WL | - | - | - | - | - |
| **T** | - | - | - | - | FL,WL | - |
| **W** | WL | - | - | - | - | - |
| **X** | - | - | - | - | WL | - |
| **A** | IT,IE,FL,WL,S,P | FL | FL,WL | WL | - | - |
| **B** | IE,S | - | - | - | S | - |
| **O** | IT,IE,FL,WL | - | - | - | IT,IE,FL,WL,S,P | S |
| **P** | IT,IE | - | - | - | - | IE |
| **U** | All | All | All | All | All | All |

**Legend:**
* **IT** = If-Then graph
* **IE** = If-Then-Else graph
* **FL** = For-Loop graph
* **WL** = While-Loop graph
* **S** = Standard graph
* **P** = Primitive graph
* **All** = All applicable graph types

---

## Execution Flows and Examples

Flow charts of the allowed connectivity for each graph type, alongside their logical Python implementations, are detailed below.

### 1. If-Then Connectivity Graph

```mermaid
%%{init: { 'theme': 'dark', 'themeVariables': { 'lineColor': '#6c7a89', 'textColor': '#edf2f4', 'mainBkg': '#2b2d42', 'primaryBorderColor': '#4a4e69' }}}%%
flowchart TB
    classDef dataTeal fill:#3b5e60,stroke:#5b7a7c,stroke-width:2px,color:#ffffff
    classDef dataGold fill:#6e6246,stroke:#8f8160,stroke-width:2px,color:#ffffff
    classDef dataOlive fill:#525c42,stroke:#6f7a5d,stroke-width:2px,color:#ffffff
    classDef dataNavy fill:#2c3e50,stroke:#4a5c6e,stroke-width:2px,color:#ffffff

    I["[I]nputs"]:::dataOlive
    F["i[F] condition"]:::dataGold
    A["GC[A]"]:::dataNavy
    O["[O]utputs"]:::dataTeal
    P["Out[P]uts (false path)"]:::dataTeal
    
    I --> F
    I --> A --> O
    I --> O
    I --> P
