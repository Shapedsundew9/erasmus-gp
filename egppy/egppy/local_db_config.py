"""Local Database Configuration."""

from egpdb.configuration import DatabaseConfig


# The local postgres database configuration
LOCAL_DB_CONFIG = DatabaseConfig(host="localhost", port=5432, dbname="egp_local_db")
