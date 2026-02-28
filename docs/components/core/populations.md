# Populations

A population of individuals work to solve a problem. An individual may be a member of more than one population and/or may provide a solution to more than one problem.

A population in Erasmus refers to a fixed number of active GC's (individuals) evaluated by a fitness function of a problem. A population is identified  by an unsigned integer >1 and a problem definition hash (git hash).

## Implementation Design

```mermaid
%%{init: { 'theme': 'dark', 'themeVariables': { 'lineColor': '#6c7a89', 'textColor': '#edf2f4', 'mainBkg': '#2b2d42', 'primaryBorderColor': '#4a4e69' }}}%%
flowchart TB
    %% Base/Default (Dark Slate)
    classDef default fill:#2b2d42,stroke:#4a4e69,stroke-width:2px,color:#edf2f4
    classDef dataTeal fill:#3b5e60,stroke:#5b7a7c,stroke-width:2px,color:#ffffff
    classDef dataGold fill:#6e6246,stroke:#8f8160,stroke-width:2px,color:#ffffff
    classDef dataOlive fill:#525c42,stroke:#6f7a5d,stroke-width:2px,color:#ffffff

    s[START]:::dataOlive
    b1[*Create population table]:::dataTeal
    b2[*Create metrics table]:::dataTeal
    b3{Name exists in DB?}:::dataGold
    b4[Validate config]:::dataTeal
    b5[Pull config from DB]:::dataTeal
    b6[Pull & validate assets]:::dataTeal
    b7{Name exists in DB?}:::dataGold
    b8[Create config in DB]:::dataTeal
    b9[Import fitness & survivability]:::dataTeal
    e[EXIT]:::dataOlive

    s -.-> b1 --> b2 --> b3 -- Yes --> b5 --> b6 --> b7 -- Yes --> b9 -.-> e
    b3 -- No --> b4 --> b5
    b7 -- No --> b8 --> b9
```
