"""Population configuration module."""
from datetime import datetime
from uuid import UUID
from typing import Any, Callable
from itertools import count
from egppy.common.common import DictTypeAccessor, Validator
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.gc_graph.ep_type import asint, asstr, validate
from egppy.gc_graph.typing import EndPointType


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# Locally uniquie population id generator
_POPULATION_IDS: count = count(start=1, step=1)


FitnessFunction = Callable[[Callable], float]
SurvivabilityFunction = Callable[[Callable], float]


class PopulationConfig(Validator, DictTypeAccessor):
    """Validate the population configuration.
    
    Must set from the JSON or internal types and validate the values.
    Getting the values returns the internal types.
    The to_json() method returns the JSON types.
    """

    def __init__(self,
        uid: int,
        problem: str | bytes,
        worker_id: str | UUID,
        size: int,
        inputs: tuple[EndPointType, ...] | list[str],
        outputs: tuple[EndPointType, ...] | list[str],
        ordered_interface_hash: bytes | str,
        unordered_interface_hash: bytes | str,
        name: str,
        description: str | None,
        meta_data: str | None,
        created: datetime | str,
        updated: datetime | str,
        survivability_function: SurvivabilityFunction,
        fitness_function: FitnessFunction
    ) -> None:
        """Initialize the class."""
        setattr(self, "uid", uid)
        setattr(self, "problem", problem)
        setattr(self, "worker_id", worker_id)
        setattr(self, "size", size)
        setattr(self, "inputs", inputs)
        setattr(self, "outputs", outputs)
        setattr(self, "ordered_interface_hash", ordered_interface_hash)
        setattr(self, "unordered_interface_hash", unordered_interface_hash)
        setattr(self, "name", name)
        setattr(self, "description", description)
        setattr(self, "meta_data", meta_data)
        setattr(self, "created", created)
        setattr(self, "updated", updated)
        setattr(self, "survivability_function", survivability_function)
        setattr(self, "fitness_function", fitness_function)

    @property
    def uid(self) -> int:
        """Get the uid."""
        return self._uid

    @uid.setter
    def uid(self, value: int) -> None:
        """The uid of the population."""
        self._in_range("uid", value, 1, 2**15-1)
        self._uid = value

    @property
    def problem(self) -> bytes:
        """Get the problem."""
        return self._problem

    @problem.setter
    def problem(self, value: str | bytes) -> None:
        """The problem to solve."""
        if isinstance(value, str):
            value = bytes.fromhex(value)
        else:
            self._is_bytes("problem", value)
        self._is_length("problem", value, 32, 32)
        self._problem = value

    @property
    def worker_id(self) -> UUID:
        """Get the worker_id."""
        return self._worker_id

    @worker_id.setter
    def worker_id(self, value: str | UUID) -> None:
        """The worker id."""
        if isinstance(value, str):
            value = UUID(value)
        else:
            self._is_uuid("worker_id", value)
        self._worker_id = value

    @property
    def size(self) -> int:
        """Get the size."""
        return self._size

    @size.setter
    def size(self, value: int) -> None:
        """The size of the population."""
        self._is_int("size", value)
        self._in_range("size", value, 1, 2**15-1)
        self._size = value

    @property
    def inputs(self) -> tuple[EndPointType, ...]:
        """Get the inputs."""
        return self._inputs

    @inputs.setter
    def inputs(self, value: tuple[EndPointType, ...] | list[str]) -> None:
        """The inputs."""
        if isinstance(value, tuple):
            assert all(validate(item) for item in value), "Invalid input type."
            self._inputs = value
        elif isinstance(value, list):
            self._inputs = tuple(asint(item) for item in value)
        else:
            assert False, "Invalid input type."

    @property
    def outputs(self) -> tuple[EndPointType, ...]:
        """Get the outputs."""
        return self._outputs

    @outputs.setter
    def outputs(self, value: tuple[EndPointType, ...] | list[str]) -> None:
        """The outputs."""
        if isinstance(value, tuple):
            assert all(validate(item) for item in value), "Invalid output type."
            self._outputs = value
        elif isinstance(value, list):
            self._outputs = tuple(asint(item) for item in value)
        else:
            assert False, "Invalid output type."

    @property
    def ordered_interface_hash(self) -> bytes:
        """Get the ordered_interface_hash."""
        return self._ordered_interface_hash

    @ordered_interface_hash.setter
    def ordered_interface_hash(self, value: bytes | str) -> None:
        """The ordered interface hash."""
        if isinstance(value, str):
            value = bytes.fromhex(value)
        else:
            self._is_bytes("ordered_interface_hash", value)
        self._is_length("ordered_interface_hash", value, 8, 8)
        self._ordered_interface_hash = value

    @property
    def unordered_interface_hash(self) -> bytes:
        """Get the unordered_interface_hash."""
        return self._unordered_interface_hash

    @unordered_interface_hash.setter
    def unordered_interface_hash(self, value: bytes | str) -> None:
        """The unordered interface hash."""
        if isinstance(value, str):
            value = bytes.fromhex(value)
        else:
            self._is_bytes("unordered_interface_hash", value)
        self._is_length("unordered_interface_hash", value, 8, 8)
        self._unordered_interface_hash = value

    @property
    def name(self) -> str:
        """Get the name."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """The name of the population."""
        self._is_string("name", value)
        self._is_length("name", value, 1, 255)
        self._name = value

    @property
    def description(self) -> str:
        """Get the description."""
        return self._description

    @description.setter
    def description(self, value: str | None) -> None:
        """The description of the population."""
        if value is not None:
            self._is_string("description", value)
            self._is_length("description", value, 1, 1024)
            self._description = value
        else:
            self._description = ""

    @property
    def meta_data(self) -> str:
        """Get the meta_data."""
        return self._meta_data

    @meta_data.setter
    def meta_data(self, value: str | None) -> None:
        """The meta data."""
        if value is not None:
            self._is_string("meta_data", value)
            self._is_length("meta_data", value, 1, 1024)
            self._meta_data = value
        else:
            self._meta_data = ""

    @property
    def created(self) -> datetime:
        """Get the created."""
        return self._created

    @created.setter
    def created(self, value: datetime | str) -> None:
        """The created date."""
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        else:
            self._is_datetime("created", value)
        self._created = value

    @property
    def updated(self) -> datetime:
        """Get the updated."""
        return self._updated

    @updated.setter
    def updated(self, value: datetime | str) -> None:
        """The updated date."""
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        else:
            self._is_datetime("updated", value)
        self._updated = value

    @property
    def survivability_function(self) -> SurvivabilityFunction:
        """Get the survivability_function."""
        return self._survivability_function

    @survivability_function.setter
    def survivability_function(self, value: SurvivabilityFunction) -> None:
        """The survivability function."""
        self._is_callable("survivability_function", value)
        self._survivability_function = value

    @property
    def fitness_function(self) -> FitnessFunction:
        """Get the fitness_function."""
        return self._fitness_function

    @fitness_function.setter
    def fitness_function(self, value: FitnessFunction) -> None:
        """The fitness function."""
        self._is_callable("fitness_function", value)
        self._fitness_function = value

    def to_json(self) -> dict[str, Any]:
        """Return the JSON representation of the configuration."""
        return {
            "uid": self.uid,
            "problem": self.problem.hex(),
            "worker_id": str(self.worker_id),
            "size": self.size,
            "inputs": [asstr(item) for item in self.inputs],
            "outputs": [asstr(item) for item in self.outputs],
            "ordered_interface_hash": self.ordered_interface_hash.hex(),
            "unordered_interface_hash": self.unordered_interface_hash.hex(),
            "name": self.name,
            "description": self.description,
            "meta_data": self.meta_data,
            "created": self.created.isoformat(),
            "updated": self.updated.isoformat(),
            "survivability_function": self.survivability_function.__name__,
            "fitness_function": self.fitness_function.__name__
        }


class PopulationsConfig(Validator, DictTypeAccessor):
    """Validate the populations configuration.
    
    Must set from the JSON or internal types and validate the values.
    Getting the values returns the internal types.
    The to_json() method returns the JSON types.
    """

    def __init__(self,
        worker_id: UUID | str = UUID("00000000-0000-0000-0000-000000000000"),
        configs: list[PopulationConfig] | list[dict[str, Any]] | None = None
    ) -> None:
        """Initialize the class."""
        setattr(self, "worker_id", worker_id)
        setattr(self, "configs", configs if configs is not None else [])

    @property
    def worker_id(self) -> UUID:
        """Get the worker_id."""
        return self._worker_id

    @worker_id.setter
    def worker_id(self, value: UUID | str) -> None:
        """The worker id."""
        if isinstance(value, str):
            value = UUID(value)
        else:
            self._is_uuid("worker_id", value)
        self._worker_id = value

    @property
    def configs(self) -> list[PopulationConfig]:
        """Get the configs."""
        return self._configs

    @configs.setter
    def configs(self, value: list[PopulationConfig] | list[dict[str, Any]]) -> None:
        """The population configurations."""
        if isinstance(value, list):
            if len(value) > 0 and isinstance(value[0], dict):
                self._configs = [PopulationConfig(
                    uid=item["uid"],
                    problem=item["problem"],
                    worker_id=item["worker_id"],
                    size=item["size"],
                    inputs=item["inputs"],
                    outputs=item["outputs"],
                    ordered_interface_hash=item["ordered_interface_hash"],
                    unordered_interface_hash=item["unordered_interface_hash"],
                    name=item["name"],
                    description=item["description"],
                    meta_data=item["meta_data"],
                    created=item["created"],
                    updated=item["updated"],
                    survivability_function=item["survivability_function"],
                    fitness_function=item["fitness_function"]
                    ) for item in value
                ]
            elif len(value) > 0 and isinstance(value[0], PopulationConfig):
                self._configs: list[PopulationConfig] = value  # type: ignore
            elif len(value) == 0:
                self._configs = []
            else:
                assert False, "Invalid population config type."

    def to_json(self) -> dict[str, Any]:
        """Return the JSON representation of the configuration."""
        return {"worker_id": self.worker_id, "configs": [item.to_json() for item in self.configs]}
