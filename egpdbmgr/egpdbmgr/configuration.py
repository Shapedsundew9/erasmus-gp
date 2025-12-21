"""Load the configuration and validate it."""

from enum import StrEnum
from typing import Any, cast

from egpcommon.common import DictTypeAccessor
from egpcommon.common_obj import CommonObj
from egpcommon.egp_log import Logger, egp_logger
from egpcommon.security import dump_signed_json, load_signed_json
from egpcommon.validator import Validator
from egpdb.configuration import DatabaseConfig

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


class TableTypes(StrEnum):
    """Enumeration of table types."""

    LOCAL = "local"  # Local database: Extra meta-data, highly indexed.
    POOL = "pool"  # Pool database: Shared resources, less indexing.
    LIBRARY = "library"  # Library database: Remote, low indexing, large (slow)
    ARCHIVE = "archive"  # Archive database: Long-term storage, infrequent access.


# Constants
_DEFAULT_DBS = {"erasmus_db": DatabaseConfig()}


class DBManagerConfig(Validator, DictTypeAccessor, CommonObj):
    """Configuration for a DB Manager.

    Must set from the JSON or internal types and validate the values.
    Getting the values returns the internal types.
    The to_json() method returns the JSON types.
    """

    def __init__(
        self,
        name: str = "DBManagerConfig",
        databases: dict[str, DatabaseConfig | dict[str, Any]] | None = None,
        managed_db: str = "erasmus_db",
        managed_type: TableTypes = TableTypes.POOL,
        upstream_dbs: list[str] | None = None,
        upstream_type: TableTypes = TableTypes.LIBRARY,
        upstream_url: str | None = None,  # TODO: Not sure if this is needed/why it is here
        archive_db: str = "erasmus_archive_db",
    ) -> None:
        """Initialize the class.

        Args
        ----
        name: The name of the configuration.
        databases: The definitions of the database servers.
        managed_db: The managed database name.
        managed_type: The managed database type.
        upstream_dbs: The remote databases to manage.
        upstream_type: The remote database type.
        upstream_url: The remote database URL.
        archive_db: The archive database name.
        """
        setattr(self, "_name", name)
        setattr(self, "databases", databases if databases is not None else _DEFAULT_DBS)
        setattr(self, "managed_db", managed_db)
        setattr(self, "managed_type", managed_type)
        setattr(self, "upstream_dbs", upstream_dbs if upstream_dbs is not None else [])
        setattr(self, "upstream_type", upstream_type)
        setattr(self, "upstream_url", upstream_url)
        setattr(self, "archive_db", archive_db)

    @property
    def archive_db(self) -> str:
        """Get the archive database."""
        return self._archive_db

    @archive_db.setter
    def archive_db(self, value: str) -> None:
        """The archive database name."""
        self.value_error(
            self._is_simple_string("archive_db", value),
            f"archive_db must be a simple string, but is {value}",
        )
        self.value_error(
            self._is_length("archive_db", value, 1, 64),
            f"archive_db length must be between 1 and 64, but is {len(value)}",
        )
        self._archive_db = value

    @property
    def databases(self) -> dict[str, DatabaseConfig]:
        """Get the databases."""
        return self._databases

    @databases.setter
    def databases(self, value: dict[str, DatabaseConfig | dict[str, Any]]) -> None:
        """The databases for the workers."""
        self.value_error(
            self._is_dict("databases", value), f"databases must be a dict, but is {type(value)}"
        )
        for key, val in value.items():
            self.value_error(
                self._is_simple_string("databases key", key),
                f"databases key must be a simple string, but is {key}",
            )
            if isinstance(val, dict):
                value[key] = DatabaseConfig(**val)
            self.value_error(
                isinstance(val, DatabaseConfig), "databases value must be a DatabaseConfig"
            )
        self._databases = cast(dict[str, DatabaseConfig], value)

    def dump_config(self) -> None:
        """Dump the configuration to disk."""
        dump_signed_json(self.to_json(), "./config.json")
        print("Configuration written to ./config.json")

    def load_config(self, config_file: str) -> None:
        """Load the configuration from disk."""
        config = load_signed_json(config_file)
        assert isinstance(config, dict), "Configuration must be a dictionary"
        self.name = config["name"]
        self.databases = {k: DatabaseConfig(**v) for k, v in config["databases"].items()}
        self.managed_db = config["managed_db"]
        self.managed_type = config["managed_type"]
        self.upstream_dbs = config["upstream_dbs"]
        self.upstream_type = config["upstream_type"]
        self.archive_db = config["archive_db"]

    @property
    def managed_db(self) -> str:
        """Get the managed database name."""
        return self._managed_db

    @managed_db.setter
    def managed_db(self, value: str) -> None:
        """The local database name."""
        self.value_error(
            self._is_simple_string("managed_db", value),
            f"managed_db must be a simple string, but is {value}",
        )
        self.value_error(
            self._is_length("managed_db", value, 1, 64),
            f"managed_db length must be between 1 and 64, but is {len(value)}",
        )
        self._managed_db = value

    @property
    def managed_type(self) -> TableTypes:
        """Get the local database type."""
        return self._managed_type

    @managed_type.setter
    def managed_type(self, value: TableTypes) -> None:
        """The local database type."""
        self.value_error(
            self._is_one_of("managed_type", value, TableTypes),
            f"managed_type must be one of {TableTypes}, but is {value}",
        )
        self._managed_type = value

    @property
    def name(self) -> str:
        """Get the name of the configuration."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """The name of the configuration.
        User defined and arbitary. Not used by EGP.
        """
        self.value_error(
            self._is_simple_string("name", value), f"name must be a simple string, but is {value}"
        )
        self.value_error(
            self._is_length("name", value, 1, 64),
            f"name length must be between 1 and 64, but is {len(value)}",
        )
        self._name = value

    def to_json(self) -> dict[str, Any]:
        """Return the configuration as a JSON type."""
        return {
            "name": self.name,
            "databases": {key: val.to_json() for key, val in self.databases.items()},
            "managed_db": self.managed_db,
            "managed_type": self.managed_type,
            "upstream_dbs": self.upstream_dbs,
            "upstream_type": self.upstream_type,
            "archive_db": self.archive_db,
        }

    @property
    def upstream_dbs(self) -> list[str]:
        """Get the remote databases."""
        return self._upstream_dbs

    @upstream_dbs.setter
    def upstream_dbs(self, value: list[str]) -> None:
        """The remote databases."""
        self.value_error(
            self._is_list("upstream_dbs", value),
            f"upstream_dbs must be a list, but is {type(value)}",
        )
        for val in value:
            self.value_error(
                self._is_simple_string("upstream_dbs", val),
                f"upstream_dbs value must be a simple string, but is {val}",
            )
            self.value_error(
                self._is_length("upstream_dbs", val, 1, 64),
                f"upstream_dbs value length must be between 1 and 64, but is {len(val)}",
            )
        self._upstream_dbs = value

    @property
    def upstream_type(self) -> str:
        """Get the remote database type."""
        return self._upstream_type

    @upstream_type.setter
    def upstream_type(self, value: TableTypes) -> None:
        """The remote database type."""
        self.value_error(
            self._is_one_of("upstream_type", value, TableTypes),
            f"upstream_type must be one of {TableTypes}, but is {value}",
        )
        self._upstream_type = value

    @property
    def upstream_url(self) -> str | None:
        """Get the remote database URL."""
        return self._upstream_url

    @upstream_url.setter
    def upstream_url(self, value: str | None) -> None:
        """The remote database file URL for download."""
        if value is not None:
            self.value_error(
                self._is_url("upstream_url", value),
                f"upstream_url must be a valid URL, but is {value}",
            )
        self._upstream_url = value
