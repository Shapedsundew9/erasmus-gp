# Connection Graphs

A Genetic Code graph defines how values from the GC input are passed to sub-GC's and outputs from sub-GC's
(and directly from the input) are connected to the GC's outputs. There are 7 types of Connection Graph.

| Type | GC Type | Comments |
|------|---------|----------|
| If-Then | Ordinary | Conditional graph with a single execution path (GCA) chosen when condition is true. |
| If-Then-Else | Ordinary | Conditional graph with two execution paths (GCA/GCB) chosen based on condition. |
| Empty | Ordinary | Defines an interface. Has no sub-GCs and generates no code. Used to seed problems. |
| For-Loop | Ordinary | Loop graph that iterates over an iterable, executing GCA for each element. |
| While-Loop | Ordinary | Loop graph that executes GCA while a condition remains true. |
| Standard | Ordinary | Connects two sub-GC's together to make a new GC. This is by far the most common type. |
| Primitive | Codon, Meta | Simplified graph representing a primitive operator (e.g., addition, logical OR). Has no sub-GC's. |

## Row Requirements

All Connection Graphs may have either an input interface or an output interface or both but cannot have neither.
GC's with just inputs store data in memory, more persistent storage or send it to a peripheral. GC's that
just have an output interface are constants, read from memory, storage or peripherals.

### Row Definitions

- **I** = Input interface (source)
- **F** = Condition evaluation destination (for conditionals)
- **L** = Loop iterable destination (for loops) and loop object source
- **S** = Loop state destination (input) and source (output) - for both loop types
- **T** = Loop next-state destination - for both loop types
- **W** = While loop condition state destination (input) and source (output) - boolean only
- **X** = While loop next-condition destination - boolean only
- **A** = GCA input (destination) / GCA output (source)
- **B** = GCB input (destination) / GCB output (source)
- **O** = Output interface (destination)
- **P** = Alternate output interface (destination) - used when condition is false or loop has zero iterations
- **U** = Unconnected source endpoints (destination) - JSON format only

Note that row _P_ only exists logically. It is the same interface as row O i.e. the functions return value (which is why it must have the same structure as row O), but the execution path to the physical return interface is different for row _O_ and row _P_ allowing conditional execution.

Similarly, rows _T_ and _X_ are semantically identical to _S_ and _W_ respectively, but serve as destination endpoints for loop body outputs while _S_ and _W_ serve as source endpoints providing state to the loop body. The implicit feedback connection from _Td→Ss_ and _Xd→Ws_ between iterations is handled in code generation, not the connection graph.

| Type | I | F | L | S | T | W | X | A | B | O | P | U |
|------|---|---|---|---|---|---|---|---|---|---|---|---|
| If-Then | X | X | - | - | - | - | - | X | - | M | M | m |
| If-Then-Else | X | X | - | - | - | - | - | X | X | M | M | m |
| Empty | o | - | - | - | - | - | - | - | - | o | - | m |
| For-Loop | X | - | X | m | m | - | - | X | - | M | M | m |
| While-Loop | X | - | - | m | m | X | X | X | - | M | M | m |
| Standard | o | - | - | - | - | - | - | X | X | o | - | m |
| Primitive | o | - | - | - | - | - | - | X | - | o | - | - |

- **X** = Must be present i.e. have at least 1 endpoint for that row.
- **-** = Must _not_ be present
- **o** = Must have at least 1 endpoint in the set of rows.
- **M** = May be present and must be the same on each row.

## Connectivity Requirements

Empty and Primitive graphs have limited connections. If-Then, If-Then-Else, For-Loop, While-Loop, and Standard graphs have connections between row interfaces but not all combinations are permitted. In the matrix below the source of the connection is the column label and the destination of the connection is the row label.

| Dst\Src | I | L | S | W | A | B |
|---------|---|---|---|---|---|---|
| F | IT,IE | - | - | - | - | - |
| L | FL | - | - | - | - | - |
| S | FL,WL | - | - | - | - | - |
| T | - | - | - | - | FL,WL | - |
| W | WL | - | - | - | - | - |
| X | - | - | - | - | WL | - |
| A | IT,IE,FL,WL,S,P | FL | FL,WL | WL | - | - |
| B | IE,S | - | - | - | S | - |
| O | IT,IE,FL,WL,S,P | - | - | - | IT,IE,FL,WL,S,P | S |
| P | IT,IE,FL,WL | - | - | - | - | IE |
| U | All | All | All | All | All | All |

**Legend:**

- **IT** = If-Then graph
- **IE** = If-Then-Else graph
- **FL** = For-Loop graph
- **WL** = While-Loop graph
- **S** = Standard graph
- **P** = Primitive graph
- **-** = Not allowed

Note that required connections are a consequence of the rule that an interface must have at least 1 endpoint and all destination endpoints must be connected to a source. In all of these cases only one row is capable of connecting to the other and so the connection must exist. Note that these rules do allow for a standard graph to have an A and B row that do not connect to each other. The GC is then functionaly equivilent to its sub-GC's. This arrangement is called a _harmony_.

Flow charts of the allowed connectivity for each graph type are below.

### If-Then Connectivity Graph

```mermaid
%% If-Then GC
flowchart TB
    I["[I]nputs"]
    F["i[F] condition"]
    A["GC[A]"]
    O["[O]utputs"]
    P["Out[P]uts (false path)"]
    I --> F
    I --> A --> O
    I --> O
    I --> P
    
classDef Icd fill:#888888,stroke:#333,stroke-width:1px
classDef Fcd fill:#aa6622,stroke:#333,stroke-width:1px
classDef Acd fill:#882222,stroke:#333,stroke-width:1px
classDef Ocd fill:#222222,stroke:#333,stroke-width:1px
classDef Pcd fill:#228888,stroke:#333,stroke-width:1px

class I Icd
class F Fcd
class A Acd
class O Ocd
class P Pcd
```

#### If-Then Execution Flow

```python
# Example: if x > 0: result = x * 2 else: result = 0

# Execution:
Is → Fd  # condition input (e.g., x > 0)
Is → Ad  # inputs to GCA (e.g., x)
Is → Pd  # pass-through for false path (e.g., 0)

if Fd evaluates to True:
    As → Od  # GCA output becomes final output (x * 2)
else:
    # P path is taken (return 0)
    Pd → return
```

### If-Then-Else Connectivity Graph

```mermaid
%% If-Then-Else GC
flowchart TB
    I["[I]nputs"]
    F["i[F] condition"]
    A["GC[A] (true)"]
    B["GC[B] (false)"]
    O["[O]utputs"]
    P["Out[P]uts (false path)"]
    I --> F
    I --> A --> O
    I --> B --> P
    I --> O
    I --> P
    
classDef Icd fill:#888888,stroke:#333,stroke-width:1px
classDef Fcd fill:#aa6622,stroke:#333,stroke-width:1px
classDef Acd fill:#882222,stroke:#333,stroke-width:1px
classDef Bcd fill:#222288,stroke:#333,stroke-width:1px
classDef Ocd fill:#222222,stroke:#333,stroke-width:1px
classDef Pcd fill:#228888,stroke:#333,stroke-width:1px

class I Icd
class F Fcd
class A Acd
class B Bcd
class O Ocd
class P Pcd
```

#### If-Then-Else Execution Flow

```python
# Example: if x > 0: result = x * 2 else: result = x * -1

# Execution:
Is → Fd  # condition input (e.g., x > 0)
Is → Ad  # inputs to GCA (e.g., x)
Is → Bd  # inputs to GCB (e.g., x)

if Fd evaluates to True:
    As → Od  # GCA output becomes final output (x * 2)
else:
    Bs → Pd  # GCB output becomes final output (x * -1)
    # Note: Pd maps to the same physical return as Od
```

### For-Loop Connectivity Graph

```mermaid
%% For-Loop GC
flowchart TB
    I["[I]nputs"]
    L["[L]oop iterable (dst) / object (src)"]
    S["[S]tate (dst) / [S]tate (src)"]
    T["[T] next-state (dst)"]
    A["GC[A] loop body"]
    O["[O]utputs"]
    P["Out[P]uts (zero iteration)"]
    I --> L
    I --> S
    L --> A
    S --> A
    A --> T
    A --> O
    T --> O
    T -.->|implicit feedback| S
    I --> O
    I --> P
    
classDef Icd fill:#888888,stroke:#333,stroke-width:1px
classDef Lcd fill:#228822,stroke:#333,stroke-width:1px
classDef Scd fill:#882288,stroke:#333,stroke-width:1px
classDef Tcd fill:#884488,stroke:#333,stroke-width:1px
classDef Acd fill:#882222,stroke:#333,stroke-width:1px
classDef Ocd fill:#222222,stroke:#333,stroke-width:1px
classDef Pcd fill:#228888,stroke:#333,stroke-width:1px

class I Icd
class L Lcd
class S Scd
class T Tcd
class A Acd
class O Ocd
class P Pcd
```

#### For-Loop Execution Flow

```python
# Example: for i in range(10): total = total + i
# (with initial total = 0, outputting both intermediate and final results)

# Iteration 1:
Is → Ld          # iterable input (range(10))
Is → Sd          # initial state (total = 0)
Ld → Ls          # first element (i = 0)
Ls → Ad          # loop variable to body
Ss → Ad          # current state to body (total = 0)
As → Td          # body outputs next state (total = 0)
[Td → Ss]        # implicit feedback (handled in code gen)

# Iteration 2:
Ls → Ad          # next element (i = 1)
Ss → Ad          # updated state from previous Td (total = 0)
As → Td          # body outputs next state (total = 1)
[Td → Ss]        # implicit feedback

# ... iterations 3-10 ...

# Final:
As → Od          # direct output
Td → Od          # final state output (total = 45)

# Zero iterations (empty iterable):
Is → Pd          # pass-through to output

# Note: As→Od allows immediate output of iteration results,
# while As→Td→[implicit]→Sd carries state across iterations.
```

### While-Loop Connectivity Graph

```mermaid
%% While-Loop GC
flowchart TB
    I["[I]nputs"]
    W["[W]hile condition (dst) / condition (src)"]
    X["[X] next-condition (dst)"]
    S["[S]tate (dst) / [S]tate (src)"]
    T["[T] next-state (dst)"]
    A["GC[A] loop body"]
    O["[O]utputs"]
    P["Out[P]uts (zero iteration)"]
    I --> W
    I --> S
    W --> A
    S --> A
    A --> X
    A --> T
    A --> O
    X --> O
    T --> O
    X -.->|implicit feedback| W
    T -.->|implicit feedback| S
    I --> O
    I --> P
    
classDef Icd fill:#888888,stroke:#333,stroke-width:1px
classDef Wcd fill:#888822,stroke:#333,stroke-width:1px
classDef Xcd fill:#888844,stroke:#333,stroke-width:1px
classDef Scd fill:#882288,stroke:#333,stroke-width:1px
classDef Tcd fill:#884488,stroke:#333,stroke-width:1px
classDef Acd fill:#882222,stroke:#333,stroke-width:1px
classDef Ocd fill:#222222,stroke:#333,stroke-width:1px
classDef Pcd fill:#228888,stroke:#333,stroke-width:1px

class I Icd
class W Wcd
class X Xcd
class S Scd
class T Tcd
class A Acd
class O Ocd
class P Pcd
```

#### While-Loop Execution Flow

```python
# Example: while count < 10: count = count + 1
# (with initial count = 0, demonstrating both state and condition tracking)

# Iteration 1:
Is → Wd          # initial condition value (count = 0)
Is → Sd          # initial state (if any additional state needed)
Wd → Ws          # condition becomes source
Ws → Ad          # condition to loop body (0 < 10 = True)
Ss → Ad          # state to loop body (if exists)
As → Xd          # body outputs next condition (count + 1 = 1)
As → Td          # body outputs next state (if exists)
[Xd → Ws]        # implicit feedback (handled in code gen)
[Td → Ss]        # implicit feedback (handled in code gen)

# Check condition:
if Ws evaluates to False: exit loop

# Iteration 2:
Wd → Ws          # updated condition (count = 1)
Ws → Ad          # condition to body (1 < 10 = True)
Ss → Ad          # state to body
As → Xd          # next condition (count = 2)
As → Td          # next state
[Xd → Ws]        # implicit feedback (handled in code gen)
[Td → Ss]        # implicit feedback (handled in code gen)

# ... iterations 3-10 ...

# Final iteration (count = 9):
Ws → Ad          # (9 < 10 = True)
As → Xd          # next condition (10)
[Xd → Ws]        # implicit feedback (handled in code gen)

# Loop exit (count = 10):
Ws evaluates to False (10 < 10 = False)
# Loop terminates
As → Od          # direct output

# Zero iterations (initial condition false):
Is → Pd          # pass-through to output

# Note: As→Od enables outputting intermediate results,
# As→Xd updates boolean condition, As→Td updates state.
# All three paths can coexist for complex loop logic.
```

### Standard Connectivity Graph

```mermaid
%% Standard GC
flowchart TB
    I["[I]nputs"]
    A["GC[A]"]
    B["GC[B]"]
    O["[O]utputs"]
    A --> O
    I --> A --> B --> O
    I --> B
    I --> O
    
classDef Icd fill:#888888,stroke:#333,stroke-width:1px
classDef Acd fill:#882222,stroke:#333,stroke-width:1px
classDef Bcd fill:#222288,stroke:#333,stroke-width:1px
classDef Ocd fill:#222222,stroke:#333,stroke-width:1px

class I Icd
class A Acd
class B Bcd
class O Ocd
```

#### Standard Execution Flow

```python
# Example: Simple computation with two sub-codons
# GCA computes intermediate values, GCB combines them

# Single execution:
Is → Ad          # inputs to GCA
Is → Bd          # inputs to GCB
Is → Od          # inputs can pass through to output
Ad → As          # GCA destination becomes source
As → Bd          # GCA results feed into GCB
As → Od          # GCA results can output directly
Bd → Bs          # GCB destination becomes source
Bs → Od          # GCB results to output

# Concrete example:
# GCA: compute x*2 and x*3
# GCB: add the two results
# Input: x=5

Is → Ad          # x=5 to GCA
As → Bd          # GCA results (10, 15) to GCB
Bs → Od          # GCB result (25) to output
# Output: 25
```

### Primitive Connectivity Graph

```mermaid
%% Primitive GC
flowchart TB
    I["[I]nputs"]
    A["GC[A] primitive operation"]
    O["[O]utputs"]
    I --> A --> O
    I --> O
    
classDef Icd fill:#888888,stroke:#333,stroke-width:1px
classDef Acd fill:#882222,stroke:#333,stroke-width:1px
classDef Ocd fill:#222222,stroke:#333,stroke-width:1px

class I Icd
class A Acd
class O Ocd
```

#### Primitive Execution Flow

```python
# Example: Single primitive operation (builtin function or operator)
# GCA is a primitive codon (e.g., add, multiply, len, etc.)

# Single execution:
Is → Ad          # inputs to primitive operation
Ad → As          # operation executes
As → Od          # result to output

# Concrete example:
# Primitive operation: add(x, y)
# Inputs: x=3, y=7

Is → Ad          # (3, 7) to add operation
As → Od          # result (10) to output
# Output: 10

# Note: Primitives are atomic operations with no sub-components
# They represent the leaf nodes in the genetic code tree
```

### Empty Connectivity Graph

```mermaid
%% Empty GC
flowchart LR
    I["[I]nputs"]
    O["[O]utputs"]
    
classDef Icd fill:#888888,stroke:#333,stroke-width:1px
classDef Ocd fill:#222222,stroke:#333,stroke-width:1px

class I Icd
class O Ocd
```

#### Empty Execution Flow

```python
# Example: Interface placeholder with no implementation
# Empty graphs define only input/output signatures

# No execution (no connections exist):
# Inputs are defined but never consumed
# Outputs are defined but never produced

# Use cases:
# 1. Interface definitions for future implementation
# 2. Type signatures without logic
# 3. Placeholder codons during evolution

# Note: Empty graphs cannot be executed
# They serve as structural placeholders in the gene pool
```

## Types

Types are represented by signed 32 bit integer unique identifiers and a unique name string of no more than 128 characters, for example 0x1, "bool" for the builtin python type bool (NB: 0x1 may not actually be the integer UID of the bool type). The integer UIDs are for efficient storage and look up and the strings for import names and generating code. Other data is associated with each type such as the bi-directional inheritence tree. An EGP type may be abstract in the programming sense that it is not completely defined and so cannot be instanciated.

### EGP Defined Types

There are several EGP defined types that can be considered pure abstract types and only exist as a root or low level node in the inheritance tree in order to support future type expansion or error conditions:

- **Any**: The standard 'typing' package 'Any' used to represent that an object may have any type.
- **EGPInvalid**: The invalid type. Used for error conditions and testing.
- **EGPNumber**: A base type that defines the numeric operators which can be inherited by all builtin python and custom numeric types.
- **EGPComplex**: Similar to number but for complex types.
- **EGPRational**: Similar to number but for rational types.
- **EGPReal**: Similar to number but for rational types.
- **EGPIntegral**: Similar to number but for rational types.

### Integer UID Format

The EP Type integer UID value Has the following format:

|    31    | 30:28 |  27:16   | 15:0 |
|:--------:|:-----:|:--------:|:----:|
| Reserved |  TT   | Reserved | XUID |

The Template Types bits, TT, define the number of templated types that need to be defined for the 65536 possible XUID types. TT has a value in the range 0 to 7. A 0 template types object is a scalar object like an _int_ or a _str_ that requires no other type to define it. Template types of 1 or more define various dimensions of containers e.g. a _list_ or _set_ only requires the definition of one template type (TT = 1) for a _list[str]_ or _set[object]_ (**NOTE:** The template type is the type of **all** of the elements hence a list or set etc. only can define one template type. A hetrogeneous container of elements is defined using a type such as _object_ or _Number_ which constrain the type). A dict is an example of a container that requires two template types to be defined e.g. _dict[str, float]_. The UID does not encode the template types directly, a global database maintains the UID to typed container mapping.

### UID Allocation

EGP permits an [infinite number of types](https://g.co/gemini/share/36d4f3b94521) i.e. a Septuple may be typed with Septuples that are not the same type as itself (inifinte recursion is not permitted) and so UID's are allocated on a globally atomic "first come first served" basis. By default all scalar (TT = 0) types plus base typed containers (e.g. "list[Any]", "dict[Hashable, Any]") permutation UIDs are defined for all containers with TT <= 2 and further types UID definitions for TT >= 1 e.g "list[int]" or "Triplet[list[Any], str, Complex]" are defined on demand from the problem definition.

### End Point Types

End Point Types, EPTs, are complete types defined by a sequence (usually a tuple) of types with the format. They are the full definition of a container type (TT > 0) type:

(type[0], \*template_type[1], ..., \*template_type[n])

where _n_ is the value of TT in the type[0] type UID. For scalar types type[0] == scalar_type UID_ and _n == 0_ i.e. _(scalar_type,)_ is the EPT for a scalar type. For container types the template types are EPTs defined in the order of the container definition which permits nested containers of almost arbitary depth to be supported (limited by the number of types that may be defined in an interface). For example:

- list[str]: (list_type, str_type, )
- dict[str, float]: (dict_type, str_type, float_type)
- dict[str, list[int]]: (dict_type, str_type, list_type, int_type)
- dict[tuple[int, ...], list[list[Any]]]: (dict_type, tuple_type, int_type, list_type, list_type, any_type)

NOTE: EPT's are an internal concept. The database storage (e.g. Gene Pool, Genomic Library) define types for ease of look up (SQL expression efficiency).

### End Points

End Points are parameters in a connection graph definition. They have a position, EGP type, row and 0, 1 or more references (connections to other endpoints) depending on their class: Source or destination. Destination endpoints must have 1 and only one reference (source that defines them) as they are input parameters to a GC function. Source endpoints may have 0 or more references as they are output parameters from a GC function. The function result may not be used or may be used in 1 or more places.

### Interfaces

An interface is a list or tuple like container of 0 or more End Points but with no more than a total of 256 types elements.

## JSON Format

TO DO: Explain more
In row U the connections are stored in alphabetical order, then index order. This is specified for reproducablility.

## Rows, Interfaces & Connections

A Genetic Code has two interfaces, the input and the output interface. When viewed from within the
Connection Graph the input interface is a source interface i.e. it is a source of connections
to other rows, and the output interface a destination interface. Row A and row B represent the input
and output interfaces to GCA and GCB reprectively. Within the graph though GCA's input interface is
a destination and its output a source.

### Source Interfaces

Source interface endpoints may have 0, 1 or many connections to destination interface endpoints (but
only one connection to the same destination endpoint).

### Destination Interfaces

All destination interface endpoints must be connected to one (and only one) source interface endpoint.
