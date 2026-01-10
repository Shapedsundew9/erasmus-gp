import psycopg2
from psycopg2 import sql
from psycopg2.extras import Json

try:
    l = sql.Literal({"a": 1})
    print("Literal created")
    # We can't call as_string without connection easily, but we can check if it requires one
    pass
except Exception as e:
    print(f"Error creating literal: {e}")

try:
    l = sql.Literal(Json({"a": 1}))
    print("Literal with Json wrapper created")
except Exception as e:
    print(f"Error creating literal with Json: {e}")

# Check if we can register json
from psycopg2.extras import register_default_json

# register_default_json(conn) # needs conn
print("Imports successful")
