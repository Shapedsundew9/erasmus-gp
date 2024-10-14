"""Load the confifuration and validate it."""

from typing import Any, cast

from egpcommon.common import DictTypeAccessor
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger
from egpcommon.security import dump_signed_json, load_signed_json
from egpcommon.validator import Validator
from egpdb.configuration import DatabaseConfig

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# Constants
_DEFAULT_DBS = {"erasmus_db": DatabaseConfig()}


class DBManagerConfig(Validator, DictTypeAccessor):
    """Configuration for a DB Manager.

    Must set from the JSON or internal types and validate the values.
    Getting the values returns the internal types.
    The to_json() method returns the JSON types.
    """

    def __init__(
        self,
        name: str = "DBManagerConfig",
        databases: dict[str, DatabaseConfig | dict[str, Any]] | None = None,
        local_db: str = "erasmus_db",
        local_type: str = "pool",
        remote_dbs: list[str] | None = None,
        remote_type: str = "library",
        archive_db: str = "erasmus_archive_db",
    ) -> None:
        """Initialize the class."""
        setattr(self, "_name", name)
        setattr(self, "databases", databases if databases is not None else _DEFAULT_DBS)
        setattr(self, "local_db", local_db)
        setattr(self, "local_type", local_type)
        setattr(self, "remote_dbs", remote_dbs if remote_dbs is not None else [])
        setattr(self, "remote_type", remote_type)
        setattr(self, "archive_db", archive_db)

    @property
    def name(self) -> str:
        """Get the name of the configuration."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """The name of the configuration.
        User defined and arbitary. Not used by EGP.
        """
        self._is_simple_string("name", value)
        self._is_length("name", value, 1, 64)
        self._name = value

    @property
    def databases(self) -> dict[str, DatabaseConfig]:
        """Get the databases."""
        return self._databases

    @databases.setter
    def databases(self, value: dict[str, DatabaseConfig | dict[str, Any]]) -> None:
        """The databases for the workers."""
        self._is_dict("databases", value)
        for key, val in value.items():
            self._is_simple_string("databases key", key)
            if isinstance(val, dict):
                value[key] = DatabaseConfig(**val)
            assert isinstance(val, DatabaseConfig), "databases value must be a DatabaseConfig"
        self._databases = cast(dict[str, DatabaseConfig], value)

    @property
    def local_db(self) -> str:
        """Get the local database."""
        return self._local_db

    @local_db.setter
    def local_db(self, value: str) -> None:
        """The local database name."""
        self._is_simple_string("local_db", value)
        self._is_length("local_db", value, 1, 64)
        self._local_db = value

    @property
    def local_type(self) -> str:
        """Get the local database type."""
        return self._local_type

    @local_type.setter
    def local_type(self, value: str) -> None:
        """The local database type."""
        self._is_one_of("local_type", value, ("pool", "library", "archive"))
        self._local_type = value

    @property
    def remote_dbs(self) -> list[str]:
        """Get the remote databases."""
        return self._remote_dbs

    @remote_dbs.setter
    def remote_dbs(self, value: list[str]) -> None:
        """The remote databases."""
        self._is_list("remote_dbs", value)
        for val in value:
            self._is_simple_string("remote_dbs", val)
            self._is_length("remote_dbs", val, 1, 64)
        self._remote_dbs = value

    @property
    def remote_type(self) -> str:
        """Get the remote database type."""
        return self._remote_type

    @remote_type.setter
    def remote_type(self, value: str) -> None:
        """The remote database type."""
        self._is_one_of("remote_type", value, ("pool", "library", "archive"))
        self._remote_type = value

    @property
    def archive_db(self) -> str:
        """Get the archive database."""
        return self._archive_db

    @archive_db.setter
    def archive_db(self, value: str) -> None:
        """The archive database name."""
        self._is_simple_string("archive_db", value)
        self._is_length("archive_db", value, 1, 64)
        self._archive_db = value

    def dump_config(self) -> None:
        """Dump the configuration to disk."""
        with open("./config.json", "w", encoding="utf8") as fileptr:
            dump_signed_json(self.to_json(), fileptr)
        print("Configuration written to ./config.json")

    def load_config(self, config_file: str) -> None:
        """Load the configuration from disk."""
        with open(config_file, "r", encoding="utf8") as fileptr:
            config = load_signed_json(fileptr)
        assert isinstance(config, dict), "Configuration must be a dictionary"
        self.name = config["name"]
        self.databases = {k: DatabaseConfig(**v) for k, v in config["databases"].items()}
        self.local_db = config["local_db"]
        self.local_type = config["local_type"]
        self.remote_dbs = config["remote_dbs"]
        self.remote_type = config["remote_type"]
        self.archive_db = config["archive_db"]

    def to_json(self) -> dict[str, Any]:
        """Return the configuration as a JSON type."""
        return {
            "name": self.name,
            "databases": {key: val.to_json() for key, val in self.databases.items()},
            "local_db": self.local_db,
            "local_type": self.local_type,
            "remote_dbs": self.remote_dbs,
            "remote_type": self.remote_type,
            "archive_db": self.archive_db,
        }
