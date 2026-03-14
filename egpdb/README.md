# egpdb — Erasmus GP Database

The `egpdb` package provides a layered PostgreSQL database interface for the Erasmus GP framework. It manages database connections with automatic retry/reconnection, table lifecycle (create, delete, wait), and CRUD operations with type conversion support.

## Modules

| Module | Description |
| --- | --- |
| `configuration.py` | Validated configuration classes: `DatabaseConfig`, `ColumnSchema`, `TableConfig` |
| `common.py` | Backoff generator and connection string builder |
| `database.py` | Connection pool management and SQL transaction execution with retry |
| `raw_table.py` | Table lifecycle and raw SQL operations (select, insert, update, upsert, delete) |
| `table.py` | Application-layer wrapper with encode/decode conversions and dict-based access |
| `row_iterators.py` | Iterator classes decoding cursor rows into tuples, namedtuples, dicts, or generators |

## Installation

```shell
pip install egpdb
```

## Usage

```python
from egpdb.configuration import DatabaseConfig, TableConfig, ColumnSchema
from egpdb.table import Table

config = TableConfig(
    database=DatabaseConfig(host="localhost", dbname="mydb", password="/path/to/password"),
    table="my_table",
    schema={
        "id": ColumnSchema(db_type="SERIAL", primary_key=True),
        "name": ColumnSchema(db_type="VARCHAR", nullable=True),
    },
    create_db=True,
    create_table=True,
)

table = Table(config)
table.insert([{"id": 1, "name": "Alice"}])
rows = list(table.select())
```

## Testing

Unit tests (no database required):

```shell
python -m unittest tests/test_egpdb/test_database_unit.py tests/test_egpdb/test_configuration.py tests/test_egpdb/test_connection_str.py
```

Integration tests (require a running PostgreSQL instance):

```shell
python -m unittest tests/test_egpdb/test_raw_table_integration.py tests/test_egpdb/test_table_integration.py
```

## Documentation

See [docs/database.md](docs/database.md) for architecture, configuration reference, and connection lifecycle details.

## License

The `egpdb` package is licensed under the [MIT License](https://opensource.org/licenses/MIT).
