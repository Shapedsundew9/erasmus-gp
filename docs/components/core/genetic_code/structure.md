# Genetic Code Logical Structure

A genetic code, GC, is a recursively embedded structure. A GC has an input interface, I, and an output interface, O as well as none or two embedded sub-GCs that are connected together as a graph. The Connection Graph is described in [graph.md](graph.md). A GC with no sub-GCs is called a codon or an empty GC. Codons represent functional primitives.

```mermaid
%%{init: { 'theme': 'dark', 'themeVariables': { 'lineColor': '#6c7a89', 'textColor': '#edf2f4', 'mainBkg': '#2b2d42', 'primaryBorderColor': '#4a4e69' }}}%%
flowchart TB
    %% Base/Default (Dark Slate)
    classDef default fill:#2b2d42,stroke:#4a4e69,stroke-width:2px,color:#edf2f4
    classDef dataPurple fill:#594a5c,stroke:#7b687f,stroke-width:2px,color:#ffffff
    classDef zonePrimary fill:#1f2130,stroke:#3a3e59,stroke-width:2px,stroke-dasharray: 5 5

    subgraph Codon_GC [Codon GC]
        direction TB
        C1[Codon]:::dataPurple
    end
    class Codon_GC zonePrimary
```

Any Empty GC is just an interface definition and represents no function.

```mermaid
%%{init: { 'theme': 'dark', 'themeVariables': { 'lineColor': '#6c7a89', 'textColor': '#edf2f4', 'mainBkg': '#2b2d42', 'primaryBorderColor': '#4a4e69' }}}%%
flowchart TB
    %% Base/Default (Dark Slate)
    classDef default fill:#2b2d42,stroke:#4a4e69,stroke-width:2px,color:#edf2f4
    classDef zonePrimary fill:#1f2130,stroke:#3a3e59,stroke-width:2px,stroke-dasharray: 5 5

    subgraph Empty_GC [Empty GC]
        direction TB
    end
    class Empty_GC zonePrimary
```

Most GC's are Standard or Conditional which have the same logical structure of 2 sub-GCs identified as A and B. The diagram below shows a GC with GC A and GC B both of which are codons in this case but may be a mixture of any type of GC except an Empty GC.

```mermaid
%%{init: { 'theme': 'dark', 'themeVariables': { 'lineColor': '#6c7a89', 'textColor': '#edf2f4', 'mainBkg': '#2b2d42', 'primaryBorderColor': '#4a4e69' }}}%%
flowchart TB
    %% Base/Default (Dark Slate)
    classDef default fill:#2b2d42,stroke:#4a4e69,stroke-width:2px,color:#edf2f4
    classDef dataNavy fill:#2c3e50,stroke:#4a5c6e,stroke-width:2px,color:#ffffff
    classDef zonePrimary fill:#1f2130,stroke:#3a3e59,stroke-width:2px,stroke-dasharray: 5 5

    subgraph GC_Node [GC]
        direction TB
        subgraph Codon_A [Codon A]
        end
        subgraph Codon_B [Codon B]
        end
    end
    class GC_Node zonePrimary
    class Codon_A zonePrimary
    class Codon_B zonePrimary
```

GCs can be infinitely embedded. The diagram below shows a GC with a depth of 5 with the maximum possible number of codons (leaves) which is 32.

```mermaid
%%{init: { 'theme': 'dark', 'themeVariables': { 'lineColor': '#6c7a89', 'textColor': '#edf2f4', 'mainBkg': '#2b2d42', 'primaryBorderColor': '#4a4e69' }}}%%
flowchart TB
    %% Base/Default (Dark Slate)
    classDef default fill:#2b2d42,stroke:#4a4e69,stroke-width:2px,color:#edf2f4
    classDef zonePrimary fill:#1f2130,stroke:#3a3e59,stroke-width:2px,stroke-dasharray: 5 5

    subgraph Top_Level_GC [Top Level GC]
        direction TB
        subgraph A
            direction TB
            subgraph AA
                direction TB
                subgraph AAA
                    direction TB
                    subgraph AAAA
                        direction TB
                    end
                    subgraph AAAB
                        direction TB
                    end
                end
                subgraph AAB
                    direction TB
                    subgraph AABA
                        direction TB
                    end
                    subgraph AABB
                        direction TB
                    end
                end
            end
            subgraph AB
                direction TB
                subgraph ABA
                    direction TB
                    subgraph ABAA
                        direction TB
                    end
                    subgraph ABAB
                        direction TB
                    end
                end
                subgraph ABB
                    direction TB
                    subgraph ABBA
                        direction TB
                    end
                    subgraph ABBB
                        direction TB
                    end
                end
            end
        end
        subgraph B
            direction TB
            subgraph BA
                direction TB
                subgraph BAA
                    direction TB
                    subgraph BAAA
                        direction TB
                    end
                    subgraph BAAB
                        direction TB
                    end
                end
                subgraph BAB
                    direction TB
                    subgraph BABA
                        direction TB
                    end
                    subgraph BABB
                        direction TB
                    end
                end
            end
            subgraph BB
                direction TB
                subgraph BBA
                    direction TB
                    subgraph BBAA
                        direction TB
                    end
                    subgraph BBAB
                        direction TB
                    end
                end
                subgraph BBB
                    direction TB
                    subgraph BBBA
                        direction TB
                    end
                    subgraph BBBB
                        direction TB
                    end
                end
            end
        end
    end
    class Top_Level_GC zonePrimary
```

The next chart shows a GC of depth 4 with the minimum possible number of codons = 5.

```mermaid
%%{init: { 'theme': 'dark', 'themeVariables': { 'lineColor': '#6c7a89', 'textColor': '#edf2f4', 'mainBkg': '#2b2d42', 'primaryBorderColor': '#4a4e69' }}}%%
flowchart TB
    %% Base/Default (Dark Slate)
    classDef default fill:#2b2d42,stroke:#4a4e69,stroke-width:2px,color:#edf2f4
    classDef dataNavy fill:#2c3e50,stroke:#4a5c6e,stroke-width:2px,color:#ffffff
    classDef dataPurple fill:#594a5c,stroke:#7b687f,stroke-width:2px,color:#ffffff

    GC(("GC")):::dataNavy
    GC --> A(("A")):::dataNavy
    GC --> B(("B")):::dataPurple
    A --> AA(("AA")):::dataNavy
    A --> AB(("AB")):::dataPurple
    AA --> AAA(("AAA")):::dataNavy
    AA --> AAB(("AAB")):::dataPurple
    AAA --> AAAA(("AAAA")):::dataPurple
    AAA --> AAAB(("AAAB")):::dataPurple
```

Since codons are the minimum functional unit, which is typically a single operation or line of code, we can state that a GC of depth _n_ has - _n_ < lines of code <= 2ⁿ

```mermaid
%%{init: { 'theme': 'dark', 'themeVariables': { 'lineColor': '#6c7a89', 'textColor': '#edf2f4', 'mainBkg': '#2b2d42', 'primaryBorderColor': '#4a4e69' }}}%%
flowchart TD
    %% Base/Default (Dark Slate)
    classDef default fill:#2b2d42,stroke:#4a4e69,stroke-width:2px,color:#edf2f4
    classDef dataNavy fill:#2c3e50,stroke:#4a5c6e,stroke-width:2px,color:#ffffff
    classDef dataPurple fill:#594a5c,stroke:#7b687f,stroke-width:2px,color:#ffffff

    GC(("GC")):::dataNavy
    GC --> A:::dataNavy
    GC --> B:::dataNavy
    A --> AA:::dataNavy
    A --> AB:::dataNavy
    AA --> AAA:::dataNavy
    AA --> AAB:::dataNavy
    AAA --> AAAA:::dataPurple
    AAA --> AAAB:::dataPurple

    AAB --> AABA:::dataPurple
    AAB --> AABB:::dataPurple

    AB --> ABA:::dataNavy
    AB --> ABB:::dataNavy
    ABA --> ABAA:::dataPurple
    ABA --> ABAB:::dataPurple

    ABB --> ABBA:::dataPurple
    ABB --> ABBB:::dataPurple

    B --> BA:::dataNavy
    B --> BB:::dataNavy
    BA --> BAA:::dataNavy
    BA --> BAB:::dataNavy
    BAA --> BAAA:::dataPurple
    BAA --> BAAB:::dataPurple

    BAB --> BABA:::dataPurple
    BAB --> BABB:::dataPurple

    BB --> BBA:::dataNavy
    BB --> BBB:::dataNavy
    BBA --> BBAA:::dataPurple
    BBA --> BBAB:::dataPurple

    BBB --> BBBA:::dataPurple
    BBB --> BBBB:::dataPurple
```
