"""Local Database Configuration."""

from egpdb.configuration import DatabaseConfig
from egpcommon.common import EGP_PROFILE, EGP_DEV_PROFILE


# If the EGP_PROFILE is set to DEV we use the postgres service rather than the local postgres
HOST: str = "postgres" if EGP_PROFILE == EGP_DEV_PROFILE else "localhost"

# The local postgres database configuration
LOCAL_DB_CONFIG = DatabaseConfig(host=HOST, port=5432, dbname="egp_local_db")
