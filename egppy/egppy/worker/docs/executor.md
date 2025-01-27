# The Genetic Code Executor

- Creates the GC code to execute (including imports)
- Executes genetic codes and handles exceptions

## Writing GC Functions

GC functions are written to be between _limit/2_ and _limit_ functional lines in length where _limit_ is >= 4 and <= 2**15-1. The higher limit is pseudo arbitary (signed 16 bit max for efficient storage). In reality memory is the only limit but such large function sizes which may only differ by a few lines of code within them are ineffcient. The lower limit is to ensure at least 2 functional lines exist preventing a chain of functions calling just one function and the stack popping with no work being done. Sensible values of _limit_ trade off the overhead of function calling, readability and the stack depth. The default is 20 lines.

When a GC is written EGP breaks it down into sub-GC's as close to _limit_ as possible. The top level GC function may be < _limit/2_ lines long with a minimum of 2 lines when its GCA and GCB both are functions > _limit/2_ lines each. As evolution occurs what was a top level GC may get wrapped to be a sub-GC. If that, now sub, GC's executable was below the _limit/2_ minimum length then it will be assessed for merger in the top level GC and a new executable, not involving the existing one, may be created. The previous executable remains in the execution scope until the GC will no longer be used as an individual at which point it is deleted.

### Assessing a GC for Function Creation

Assessing a GC is done recursively (it is actaully implemented as a stack to allow for very deep GC's) using the following rules:

| # Lines      | Executable Exists | Operation       | Comments                                                                                                                                                              |
|:------------:|:-----------------:|:---------------:|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0            | True              | Error           | Having an executable but no lines is not possible.                                                                                                                    |
| < _limit/2_  | True              | Assess          | Was a "small" top level GC that can be merged into another.                                                                                                           |
| >= _limit/2_ | True              | Terminal        | Meets the criteria for a GC function. No need to analyse further.                                                                                                     |
| > _limit_    | True              | Error           | Should not be possible to have an executable with more than the limit number of lines.                                                                                |
| 0            | False             | Assess          | Has not been assessed yet.                                                                                                                                            |
| <= _limit_ | False             | Assess | Has previously been assessed and wrapped. Must be reassessed to build connection graph for incorpation in new executable. |
| > _limit_    | False             | Error           | This is a logic error is traversing the GC structure.                                                                                                                 |

### Dead Code

When travesing the GC graph it is not possible to determine what code will not be executed, "Dead Code". Only when the codon graph with all the connection are resolved is it possible to know the actual number of lines a function will take.

### Method

This is an overview of the implementation of the _write_gc_executable()_ function. The following is a key to the GC logical structure charts used:

```mermaid

flowchart TD

    GC(Non-codon GC):::blue
    Codon((Codon)):::green
    Unknown((Unknown)):::red
    text["Signature[:8]"]

classDef grey fill:#444444,stroke:#333333,stroke-width:2px
classDef red fill:#A74747,stroke:#996666,stroke-width:2px
classDef blue fill:#336699,stroke:#556688,stroke-width:2px
classDef green fill:#576457,stroke:#667766,stroke-width:2px
linkStyle default stroke:#AAAAAA,stroke-width:2px
```

#### Example GC Logical Structure

This GC will be used as the example of how a GC is analysed and the python exectuable functions it represented created.

```mermaid
flowchart TD
    0a5fccb4b(a5fccb4b):::blue
    a1bf45fa8d(bf45fa8d):::blue
    0a5fccb4b --> a1bf45fa8d
    b1bf45fa8d(bf45fa8d):::blue
    0a5fccb4b --> b1bf45fa8d
    a265722e39(65722e39):::blue
    a1bf45fa8d --> a265722e39
    b2b2f31c0a(b2f31c0a):::blue
    a1bf45fa8d --> b2b2f31c0a
    a365722e39(65722e39):::blue
    b1bf45fa8d --> a365722e39
    b3b2f31c0a(b2f31c0a):::blue
    b1bf45fa8d --> b3b2f31c0a
    a41da4f00a(1da4f00a):::blue
    a265722e39 --> a41da4f00a
    b41da4f00a(1da4f00a):::blue
    a265722e39 --> b41da4f00a
    a5ef8c752e((ef8c752e)):::red
    b2b2f31c0a --> a5ef8c752e
    b5e030d53c((e030d53c)):::green
    b2b2f31c0a --> b5e030d53c
    a61da4f00a(1da4f00a):::blue
    a365722e39 --> a61da4f00a
    b61da4f00a(1da4f00a):::blue
    a365722e39 --> b61da4f00a
    a7ef8c752e((ef8c752e)):::red
    b3b2f31c0a --> a7ef8c752e
    b7e030d53c((e030d53c)):::green
    b3b2f31c0a --> b7e030d53c
    a849dd8290((49dd8290)):::green
    a41da4f00a --> a849dd8290
    b8b2f31c0a(b2f31c0a):::blue
    a41da4f00a --> b8b2f31c0a
    a949dd8290((49dd8290)):::green
    b41da4f00a --> a949dd8290
    b9b2f31c0a(b2f31c0a):::blue
    b41da4f00a --> b9b2f31c0a
    a1149dd8290((49dd8290)):::green
    a61da4f00a --> a1149dd8290
    b11b2f31c0a(b2f31c0a):::blue
    a61da4f00a --> b11b2f31c0a
    a1249dd8290((49dd8290)):::green
    b61da4f00a --> a1249dd8290
    b12b2f31c0a(b2f31c0a):::blue
    b61da4f00a --> b12b2f31c0a
    a15ef8c752e((ef8c752e)):::red
    b8b2f31c0a --> a15ef8c752e
    b15e030d53c((e030d53c)):::green
    b8b2f31c0a --> b15e030d53c
    a17ef8c752e((ef8c752e)):::red
    b9b2f31c0a --> a17ef8c752e
    b17e030d53c((e030d53c)):::green
    b9b2f31c0a --> b17e030d53c
    a19ef8c752e((ef8c752e)):::red
    b11b2f31c0a --> a19ef8c752e
    b19e030d53c((e030d53c)):::green
    b11b2f31c0a --> b19e030d53c
    a21ef8c752e((ef8c752e)):::red
    b12b2f31c0a --> a21ef8c752e
    b21e030d53c((e030d53c)):::green
    b12b2f31c0a --> b21e030d53c
classDef grey fill:#444444,stroke:#333333,stroke-width:2px
classDef red fill:#A74747,stroke:#996666,stroke-width:2px
classDef blue fill:#336699,stroke:#556688,stroke-width:2px
classDef green fill:#576457,stroke:#667766,stroke-width:2px
linkStyle default stroke:#AAAAAA,stroke-width:2px
```

#### Creating the node graph

The node graph is a bidirectional graph of the GC logical structure using _GCNode_ objects as nodes created by the _node_graph()_ function. The node graph structure is an explicit GC logical graph in that GC nodes that are used in more than one place are duplicated rather than just referenced, as they are in the GC graph, so that a) a bidirectional graph can be created and b) nodes can have meta data added pursuant thier local environment in the graph. i.e. the node graph looks like the graph above. Note that "unknown" GC's (those that have a GCA and or GCB that is **not** in the cache) are permissable as long as they have an executable defined.

#### Determining line counts

As described in the opening section line counts drive what GC's become executable functions (which affects the line counts of other GC's). The line counts for each not are determined in the _line_count()_ function and the data added to the "num_lines" member of the _GCNode_ along with some analysis meta data. If the _limit_ was set to 4 for the GC logical structure above this is the node graph it would create:

```mermaid
flowchart TD
    uid0040("a5fccb4b<br>4 lines"):::blue
    subgraph uid0041sd[" "]
    uid0041("bf45fa8d<br>3 lines"):::blue
    subgraph uid0043sd[" "]
    uid0043("65722e39<br>4 lines"):::blue
    subgraph uid0047sd[" "]
    uid0047("1da4f00a<br>3 lines"):::blue
    uid004f(("49dd8290<br>1 lines")):::green
    uid0047 --> uid004f
    uid0050("b2f31c0a<br>2 lines"):::blue
    uid0047 --> uid0050
    uid0057(("ef8c752e<br>1 lines")):::green
    uid0050 --> uid0057
    uid0058(("e030d53c<br>1 lines")):::green
    uid0050 --> uid0058
    end
    uid0043 --> uid0047
    uid0048("1da4f00a<br>3 lines"):::blue
    uid0043 --> uid0048
    uid0051(("49dd8290<br>1 lines")):::green
    uid0048 --> uid0051
    uid0052("b2f31c0a<br>2 lines"):::blue
    uid0048 --> uid0052
    uid0059(("ef8c752e<br>1 lines")):::green
    uid0052 --> uid0059
    uid005a(("e030d53c<br>1 lines")):::green
    uid0052 --> uid005a
    end
    uid0041 --> uid0043
    uid0044("b2f31c0a<br>2 lines"):::blue
    uid0041 --> uid0044
    uid0049(("ef8c752e<br>1 lines")):::green
    uid0044 --> uid0049
    uid004a(("e030d53c<br>1 lines")):::green
    uid0044 --> uid004a
    end
    uid0040 --> uid0041
    uid0042("bf45fa8d<br>3 lines"):::blue
    uid0040 --> uid0042
    subgraph uid0045sd[" "]
    uid0045("65722e39<br>4 lines"):::blue
    subgraph uid004bsd[" "]
    uid004b("1da4f00a<br>3 lines"):::blue
    uid0053(("49dd8290<br>1 lines")):::green
    uid004b --> uid0053
    uid0054("b2f31c0a<br>2 lines"):::blue
    uid004b --> uid0054
    uid005b(("ef8c752e<br>1 lines")):::green
    uid0054 --> uid005b
    uid005c(("e030d53c<br>1 lines")):::green
    uid0054 --> uid005c
    end
    uid0045 --> uid004b
    uid004c("1da4f00a<br>3 lines"):::blue
    uid0045 --> uid004c
    uid0055(("49dd8290<br>1 lines")):::green
    uid004c --> uid0055
    uid0056("b2f31c0a<br>2 lines"):::blue
    uid004c --> uid0056
    uid005d(("ef8c752e<br>1 lines")):::green
    uid0056 --> uid005d
    uid005e(("e030d53c<br>1 lines")):::green
    uid0056 --> uid005e
    end
    uid0042 --> uid0045
    uid0046("b2f31c0a<br>2 lines"):::blue
    uid0042 --> uid0046
    uid004d(("ef8c752e<br>1 lines")):::green
    uid0046 --> uid004d
    uid004e(("e030d53c<br>1 lines")):::green
    uid0046 --> uid004e
classDef grey fill:#444444,stroke:#333333,stroke-width:2px
classDef red fill:#A74747,stroke:#996666,stroke-width:2px
classDef blue fill:#336699,stroke:#556688,stroke-width:2px
classDef green fill:#576457,stroke:#667766,stroke-width:2px
linkStyle default stroke:#AAAAAA,stroke-width:2px
```
