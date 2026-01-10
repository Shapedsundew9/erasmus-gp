import sys
from psycopg2 import sql
from psycopg2.extras import Json
from egpdb.database import db_connect, db_create, db_delete, register_default_json
from egpdb.configuration import TableConfig

# Define a config to connect
config = {
    "host": "postgres",
    "port": 5432,
    "user": "postgres",
    "password": "qlkjidfkoqwfbg",
    "maintenance_db": "postgres",
    "dbname": "debug_json_db",
    "retries": 3,
    "create_db": True,  # Needed?
    "wait_for_db": True,  # Needed?
}

try:
    print("Connecting...")
    # Create DB
    try:
        db_create("debug_json_db", config)
    except Exception:
        pass  # maybe exists

    conn = db_connect("debug_json_db", config)
    print("Connected.")

    # Test Literal with Json wrapper
    l = sql.Literal(Json({"a": 1}))
    print(f"Literal(Json): {l.as_string(conn)}")

    # Test Literal with dict (relying on register_adapter)
    try:
        l2 = sql.Literal({"b": 2})
        print(f"Literal(dict): {l2.as_string(conn)}")
    except Exception as e:
        print(f"Literal(dict) failed: {e}")

    # cleanup
    conn.close()
    # db_delete("debug_json_db", config)

except Exception as e:
    print(f"Failed: {e}")
