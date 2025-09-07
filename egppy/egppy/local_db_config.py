"""Local Database Configuration."""

from egpcommon.common import EGP_DEV_PROFILE, EGP_PROFILE
from egpdb.configuration import DatabaseConfig
from egpdbmgr.configuration import DBManagerConfig

# If the EGP_PROFILE is set to DEV we use the postgres service rather than the local postgres
HOST: str = "postgres" if EGP_PROFILE == EGP_DEV_PROFILE else "localhost"

# The local postgres database configuration
LOCAL_DB_CONFIG = DatabaseConfig(host=HOST, port=5432, dbname="egp_local_db")
LOCAL_DB_MANAGER_CONFIG = DBManagerConfig(databases={"erasmus_db": LOCAL_DB_CONFIG})
