# Connection Graphs

A Genetic Code graph defines how values from the GC input are passed to sub-GC's and outputs from sub-GC's
(and directly from the input) are connected to the GC's outputs. There are 6 types of Connection Graph.

| Type | Comments |
|------|------------|
| Codon | Defines an interface & represents a primitive operator such addition or logical OR. Has no sub-GC's. |
| Conditional | Chooses an execution path through one of the sub-GCs based the inputs. |
| Empty | Defines an interface. Has no sub-GCs and generates no code. Used to seed problems. |
| Standard | Connects two sub-GC's together to make a new GC. This is by far the most common type.|

## Row Requirements

Note that both GCA and GCB are present or neither are present. This simplifies the rules for insertion.
All Connection Graphs may have either an input interface or an output interface or both but cannot have neither.
GC's with just inputs store data in memory, more presistant storage or send it to an output port. GC's that
just have an output interface are constants, read from memory, storage or input ports.

| Type | I | F | A | B | O | P |
|------|---|---| ---|---|---|---|
| Codon | o | - | - | - | o | - |
| Conditional | X | X | X | X | m | m |
| Empty | o | - | - | - | o | - |
| Standard | o | - | X | X | o | - |

- **X** = Must be present i.e. have at least 1 endpoint for that row.
- **-** = Must _not_ be present
- **o** = Must have at least 1 endpoint in the set of rows.
- **m** = May be present and must be the same on each row.

## Connectivity Requirements

Codons and Empty graphs have no connections only Input and Output row definitions i.e. an IO interface definition. Standard, Hardened and Conditional graphs have connections between row interfaces but not all combinations are permitted. In the matrix below the source of the connection is the column label and the destination of the connection is the row label.

| Dst | I | F | A | B | O | P |
|------|---|---|---|---|---|---|
|  I  | - | - | - | - | - | - |
| F | **C** | - | - | - | - | - |
|  A  | SC | - |  - | - | - | - |
|  B  | SC | - | S | - | - | - |
|  O  | SC | - | SC | S | - | - |
|  P  | C | - | - | C | - | - |

- S = Allowed in a Standard graph
- C = Allowed in a Conditional graph
- \- = Not allowed in any case
- **bold** = Required

Note that the required connections are a consequence of the rule that an interface must have at least 1 endpoint and all destination endpoints must be connected to a source. In all of these cases only one row is capable of connecting to the other and so the connection must exist.

Flow charts of the allowed connectivity standard and conditional graphs are below.

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
    I --> O
    I --> P
    
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

End Points are parameters in a connection graph definition. They have a position, EGP type, row and 0, 1 or more references (connections to other end points) depending on their class: Source or destination. Destination end points must have 1 and only one reference (source that defines them) as they are input parameters to a GC function. Source endpoints may have 0 or more references as they are output parameters from a GC function. The function result may not be used or may be used in 1 or more places.

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
