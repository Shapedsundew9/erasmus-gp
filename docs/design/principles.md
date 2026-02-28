# Software Design Principles

Currently a collection of Software Design Principles

## Abstraction and Isolation

Erasmus GP has a roadmap of function & optimisation to be implemented. To enable work to start with the most basic function and expand later the objects passed around are abstract, interfaces assumed asynchronous and functions as stateless as possible.

The general inheritance of EGP classes is shown below.

```mermaid
%%{init: { 'theme': 'dark', 'themeVariables': { 'lineColor': '#6c7a89', 'textColor': '#edf2f4', 'mainBkg': '#2b2d42', 'primaryBorderColor': '#4a4e69' }}}%%
block-beta
    %% Base/Default (Dark Slate)
    classDef default fill:#2b2d42,stroke:#4a4e69,stroke-width:2px,color:#edf2f4
    classDef dataBlue fill:#3a506b,stroke:#5c6b73,stroke-width:2px,color:#ffffff
    classDef dataTeal fill:#3b5e60,stroke:#5b7a7c,stroke-width:2px,color:#ffffff
    classDef dataPlum fill:#4a3b52,stroke:#685b70,stroke-width:2px,color:#ffffff
    classDef dataNavy fill:#2c3e50,stroke:#4a5c6e,stroke-width:2px,color:#ffffff

    columns 5
    A["Base"]:::dataBlue
    B["Container"]:::dataNavy
    C["Mixin"]:::dataTeal
    D["ABC"]:::dataPlum
```

From left to right:

- **Base** classes provide highest priority (method resolution order) members and methods. It is used to provide mixin methods that override any Container class definitions.
- **Container** classes are either builtin containers or from collections.abc e.g. dict, list, MutableMapping etc.
- **Mixin** classes provide methods that are built from primitive methods. Mixin classes are often defined with a Protocol class to support type checking.
- **ABC** abstract base class defines the required methods of the class.

## Logging

Any and all assumptions are coded into API's as assertions that can be enabled with the logging level.
Logging level *VERIFY* performs basic value and type checking.
Logging level *CONSISTENCY* does a more thorough check that all data in scope is self consistent.

## JSON and Dictionaries

Erasmus GP uses data in human readable JSON format where ever practical. This encourages the use of basic types and python dictionaries as viable object base classes.

## Security

1. All data at rest is digitially signed.
1. All data in transit is encrypted between authenticated points.
1. All data read from rest is verified before any use e.g. verify expectations before unzipping.
