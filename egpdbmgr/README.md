# egpdbmgr — Erasmus Genetic Programming — Database Manager

The `egpdbmgr` package manages EGP genetic code databases backed by PostgreSQL.

## Features

- **Configuration** — Validated `DBManagerConfig` loaded from signed JSON files, with cross-field verification.
- **Table Management** — Creates and manages genetic code, meta-data, and source tracking tables.
- **Schema Derivation** — Genetic code table schemas are derived from `GGC_KVT` with configurable table types (Local, Pool, Library, Archive).
- **CLI Entry Point** — Command-line interface for initialising the DB Manager with a configuration file.

## Installation

```shell
pip install egpdbmgr
```

## Usage

### Default Configuration

Generate a default configuration file:

```shell
python -m egpdbmgr.main -d
```

### Run with Configuration

```shell
python -m egpdbmgr.main -c config.json
```

### Run with Default Internal Configuration

```shell
python -m egpdbmgr.main -D
```

## Testing

```shell
python -m unittest discover tests
```

## License

See the [LICENSE](../LICENSE) file.
