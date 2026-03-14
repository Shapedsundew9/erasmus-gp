# EGP Database Manager - Architecture

## Top Level

```mermaid
%%{init: { 'theme': 'dark', 'themeVariables': { 'lineColor': '#6c7a89', 'textColor': '#edf2f4', 'mainBkg': '#2b2d42', 'primaryBorderColor': '#4a4e69' }}}%%
flowchart TD
    %% Base/Default (Dark Slate)
    classDef default fill:#2b2d42,stroke:#4a4e69,stroke-width:2px,color:#edf2f4
    classDef dataBlue fill:#3a506b,stroke:#5c6b73,stroke-width:2px,color:#ffffff
    classDef dataTeal fill:#3b5e60,stroke:#5b7a7c,stroke-width:2px,color:#ffffff
    classDef dataPlum fill:#4a3b52,stroke:#685b70,stroke-width:2px,color:#ffffff
    classDef dataOlive fill:#525c42,stroke:#6f7a5d,stroke-width:2px,color:#ffffff
    classDef dataNavy fill:#2c3e50,stroke:#4a5c6e,stroke-width:2px,color:#ffffff

    db1[(Postgres GP/GL DB)]:::dataPlum
    db2[(Postgres Archive DB)]:::dataPlum
    dbm1["EGP DB Manager"]:::dataNavy
    bu1[/"Archive Files"/]:::dataOlive

    db1 <-->|Implemented| dbm1
    dbm1 <-.->|Planned| db2
    dbm1 <-.->|Planned| bu1
```

The EGP DB Manager is an independent process (container) that manages a PostgreSQL database for a storage role in EGP. The storage role (Local, Gene Pool, Genomic Library, Archive) is defined by the `DBManagerConfig` upon creation via the `TableTypes` enum.

### Current Implementation

The DB Manager currently supports:

- **Configuration** — `DBManagerConfig` with validated properties for databases, managed table type, upstream references, and archive database name. Configurations are loaded from signed JSON files.
- **Table Creation** — Three tables are created during initialization:
  - **Genetic Code Table** — Schema derived from `GGC_KVT` with encode/decode conversions for `cgraph`, `properties`, and signature fields.
  - **Meta Table** — Stores `created` (timestamp) and `creator` (UUID) records.
  - **Sources Table** — Tracks source file provenance: `source_path`, `creator_uuid`, `timestamp`, `file_hash`, `signature`, `algorithm`.
- **CLI Entry Point** — `main.py` with argument parsing for config file, default config, gallery display.

### Planned Features (Not Yet Implemented)

The following are design goals, not yet reflected in code:

- Syncing the DB back to higher layer databases (micro-biome → biome etc.).
- Pulling data from higher layer databases (biome → micro-biome etc.).
- DB backup and restore.
- DB migration (e.g. from one version to another).
- Archive process (purging low-value GC data to archive DB / files).
- REST API, analytics, and health monitoring.
- Universal Archive file management.

## Configuration

The `DBManagerConfig` class (`configuration.py`) provides validated configuration with the following properties:

| Property | Type | Default | Description |
| --- | --- | --- | --- |
| `name` | `str` | `"DBManagerConfig"` | User-defined name (1–64 chars). |
| `databases` | `dict[str, DatabaseConfig]` | `{"erasmus_db": DatabaseConfig()}` | Database server definitions. |
| `managed_db` | `str` | `"erasmus_db"` | Key into `databases` for the managed DB. |
| `managed_type` | `TableTypes` | `POOL` | Table type: LOCAL, POOL, LIBRARY, or ARCHIVE. |
| `upstream_dbs` | `list[str]` | `[]` | Keys into `databases` for upstream DBs. |
| `upstream_type` | `TableTypes` | `LIBRARY` | Table type for upstream databases. |
| `upstream_url` | `str \| None` | `None` | Optional URL for remote DB file download. |
| `archive_db` | `str` | `"erasmus_archive_db"` | Archive database name. |

Cross-field validation in `verify()` ensures `managed_db` and all `upstream_dbs` entries exist as keys in `databases`.

## Initialization

The current initialization flow:

```mermaid
%%{init: { 'theme': 'dark', 'themeVariables': { 'lineColor': '#6c7a89', 'textColor': '#edf2f4', 'mainBkg': '#2b2d42', 'primaryBorderColor': '#4a4e69' }}}%%
flowchart TD
    %% Base/Default (Dark Slate)
    classDef default fill:#2b2d42,stroke:#4a4e69,stroke-width:2px,color:#edf2f4
    classDef dataTeal fill:#3b5e60,stroke:#5b7a7c,stroke-width:2px,color:#ffffff
    classDef dataNavy fill:#2c3e50,stroke:#4a5c6e,stroke-width:2px,color:#ffffff
    classDef dataGold fill:#6e6246,stroke:#8f8160,stroke-width:2px,color:#ffffff

    init1[Parse CLI Arguments]:::dataTeal
    init2{Config file provided?}:::dataGold
    init3[Load signed JSON config]:::dataTeal
    init4[Use default config]:::dataTeal
    init5[Create DBManager]:::dataNavy
    init6[Create GC Table]:::dataNavy
    init7[Create Meta Table]:::dataNavy
    init8[Create Sources Table]:::dataNavy
    init9[Insert initial meta record]:::dataTeal
    init10[Log completion]:::dataTeal

    init1 --> init2
    init2 -->|Yes| init3
    init2 -->|No| init4
    init3 --> init5
    init4 --> init5
    init5 --> init6
    init5 --> init7
    init5 --> init8
    init7 --> init9
    init9 --> init10
```

## Module Structure

```mermaid
%%{init: { 'theme': 'dark', 'themeVariables': { 'lineColor': '#6c7a89', 'textColor': '#edf2f4', 'mainBkg': '#2b2d42', 'primaryBorderColor': '#4a4e69' }}}%%
classDiagram
    %% Base/Default (Dark Slate)
    classDef default fill:#2b2d42,stroke:#4a4e69,stroke-width:2px,color:#edf2f4
    classDef dataNavy fill:#2c3e50,stroke:#4a5c6e,stroke-width:2px,color:#ffffff
    classDef dataPlum fill:#4a3b52,stroke:#685b70,stroke-width:2px,color:#ffffff

    class DBManagerConfig {
        +name: str
        +databases: dict
        +managed_db: str
        +managed_type: TableTypes
        +upstream_dbs: list
        +upstream_type: TableTypes
        +upstream_url: str | None
        +archive_db: str
        +dump_config()
        +load_config(config_file)
        +to_json()
        +verify()
    }

    class DBManager {
        +config: DBManagerConfig
        +managed_gc_table: Table
        +managed_gc_meta_table: Table
        +managed_sources_table: Table
        +create_managed_table()
        +create_managed_meta_table()
        +create_managed_sources_table()
        +operations()
        +prepare_schemas()
    }

    class TableTypes {
        <<enumeration>>
        LOCAL
        POOL
        LIBRARY
        ARCHIVE
    }

    DBManager --> DBManagerConfig
    DBManagerConfig --> TableTypes
    DBManagerConfig --|> Validator
    DBManagerConfig --|> DictTypeAccessor
    DBManagerConfig --|> CommonObj

    class DBManagerConfig dataNavy
    class DBManager dataNavy
    class TableTypes dataPlum
```

## Database Auxiliary Tables

Besides the GC's in the main database table, the DBM creates and manages auxiliary data tables.

### Meta Table (Implemented)

| Column | DB Type | Description |
| --- | --- | --- |
| `created` | `TIMESTAMP` | When the database was created. |
| `creator` | `UUID` | UUID of the creator. |

### Sources Table (Implemented)

| Column | DB Type | Description |
| --- | --- | --- |
| `source_path` | `VARCHAR` | Path to the source file. |
| `creator_uuid` | `VARCHAR` | UUID of the source creator. |
| `timestamp` | `VARCHAR` | Timestamp of the source. |
| `file_hash` | `VARCHAR` | Hash of the source file. |
| `signature` | `VARCHAR` | Cryptographic signature. |
| `algorithm` | `VARCHAR` | Signing algorithm used. |

### Planned Auxiliary Tables

The following are design goals for future implementation:

- **DB Metadata** — UUID, version, migration history, host list, archive/sync info.
- **Timeseries Analytics** — DB size, archived/updated/synced GC counts, fitness distributions.
