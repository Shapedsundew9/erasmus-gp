"""Load the confifuration and validate it."""

from typing import Any, cast

from egpcommon.common import DictTypeAccessor
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger
from egpcommon.security import dump_signed_json, load_signed_json
from egpcommon.validator import Validator
from egpdb.configuration import DatabaseConfig
from egppy.populations.configuration import PopulationsConfig

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class DBManagerConfig(Validator, DictTypeAccessor):
    """Configuration for a DB Manager.

    Must set from the JSON or internal types and validate the values.
    Getting the values returns the internal types.
    The to_json() method returns the JSON types.
    """

    def __init__(
        self,
        databases: dict[str, DatabaseConfig | dict[str, Any]] | None = None,
        local_db: str = "erasmus_db",
        local_type: str = "pool",
        remote_dbs: list[str] = ["erasmus_db"],
        remote_type: str = "library",
    ) -> None:
        """Initialize the class."""
        setattr(self, "databases", databases if databases is not None else _DEFAULT_DBS)
        setattr(self, "gene_pool", gene_pool)
        setattr(self, "microbiome", microbiome)
        setattr(self, "populations", populations)
        setattr(self, "problem_definitions", problem_definitions)
        setattr(self, "problem_folder", problem_folder)

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
    def gene_pool(self) -> str:
        """Get the gene pool."""
        return self._gene_pool

    @gene_pool.setter
    def gene_pool(self, value: str) -> None:
        """The name of the gene pool."""
        self._is_simple_string("gene_pool", value)
        self._is_length("gene_pool", value, 1, 64)
        assert value in self.databases, "gene_pool must be a database"
        self._gene_pool = value

    @property
    def microbiome(self) -> str:
        """Get the microbiome."""
        return self._microbiome

    @microbiome.setter
    def microbiome(self, value: str) -> None:
        """The name of the microbiome."""
        self._is_simple_string("microbiome", value)
        self._is_length("microbiome", value, 1, 64)
        assert value in self.databases, "microbiome must be a database"
        self._microbiome = value

    @property
    def populations(self) -> PopulationsConfig:
        """Get the populations."""
        return self._populations

    @populations.setter
    def populations(self, value: PopulationsConfig | dict[str, Any]) -> None:
        """The name of the populations."""
        if isinstance(value, dict):
            value = PopulationsConfig(**value)
        assert isinstance(value, PopulationsConfig), "populations must be a PopulationsConfig"
        self._populations = value

    @property
    def problem_definitions(self) -> str:
        """Get the problem definitions."""
        return self._problem_definitions

    @problem_definitions.setter
    def problem_definitions(self, value: str) -> None:
        """The URL to the problem definitions."""
        self._is_length("problem_definitions", value, 8, 2048)
        self._is_url("problem_definitions", value)
        self._problem_definitions = value

    @property
    def problem_folder(self) -> str:
        """Get the problem folder."""
        return self._problem_folder

    @problem_folder.setter
    def problem_folder(self, value: str) -> None:
        """The folder for the problem definitions."""
        self._is_length("problem_folder", value, 1, 256)
        self._is_path("problem_folder", value)
        self._problem_folder = value

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
        self.databases = {k: DatabaseConfig(**v) for k, v in config["databases"].items()}
        self.gene_pool = config["gene_pool"]
        self.microbiome = config["microbiome"]
        self.populations = PopulationsConfig(**config["populations"])
        self.problem_definitions = config["problem_definitions"]
        self.problem_folder = config["problem_folder"]

    def to_json(self) -> dict[str, Any]:
        """Return the configuration as a JSON type."""
        return {
            "databases": {key: val.to_json() for key, val in self.databases.items()},
            "gene_pool": self.gene_pool,
            "microbiome": self.microbiome,
            "populations": self.populations.to_json(),
            "problem_definitions": self.problem_definitions,
            "problem_folder": self.problem_folder,
        }
