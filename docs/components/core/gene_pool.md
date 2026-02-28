# Gene Pool Design

The Gene Pool provides the storage and retrieval layer for Genetic Codes (GCs)
within the Erasmus GP system.

## Overview

The Gene Pool is accessed through the `GenePoolInterface` abstract base class,
which defines the standard API for storing, retrieving, and managing GCs.
Concrete implementations include in-memory caches and PostgreSQL-backed
persistent stores.

## Architecture

```mermaid
%%{init: { 'theme': 'dark', 'themeVariables': { 'lineColor': '#6c7a89', 'textColor': '#edf2f4', 'mainBkg': '#2b2d42', 'primaryBorderColor': '#4a4e69' }}}%%
graph TD
    %% Base/Default (Dark Slate)
    classDef default fill:#2b2d42,stroke:#4a4e69,stroke-width:2px,color:#edf2f4
    classDef dataTeal fill:#3b5e60,stroke:#5b7a7c,stroke-width:2px,color:#ffffff
    classDef dataPlum fill:#4a3b52,stroke:#685b70,stroke-width:2px,color:#ffffff
    classDef dataNavy fill:#2c3e50,stroke:#4a5c6e,stroke-width:2px,color:#ffffff

    A[GenePoolInterface ABC]:::dataNavy --> B[GenePoolCache]:::dataNavy
    A --> C[GenePoolDB]:::dataPlum
    B --> D[In-Memory Storage]:::dataTeal
    C --> E[PostgreSQL]:::dataPlum
```

## Key Components

- **GenePoolInterface**: ABC defining `get`, `put`, `delete`, and query operations.
- **GenePoolCache**: In-memory implementation for fast local access.
- **GenePoolDB**: Persistent implementation backed by PostgreSQL via `egpdb`.
