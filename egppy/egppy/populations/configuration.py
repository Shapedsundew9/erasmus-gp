"""Population configuration module."""

from datetime import datetime
from itertools import count
from typing import Any, Callable, Sequence
from uuid import UUID

from egpcommon.common import DictTypeAccessor
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger
from egpcommon.validator import Validator
from egppy.genetic_code.c_graph_constants import DstRow, SrcRow
from egppy.genetic_code.end_point import EndPoint
from egppy.genetic_code.interface import Interface, TypesDef

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# Locally uniquie population id generator
_POPULATION_IDS: count = count(start=1, step=1)
INITIAL_POPULATION_SOURCES = ("BEST", "DIVERSE", "RELATED", "UNRELATED", "SPONTANEOUS")
UNDERFLOW_OPTIONS = INITIAL_POPULATION_SOURCES + ("NEXT", "NONE")


FitnessFunction = Callable[[Callable], float]
SurvivabilityFunction = Callable[[Callable], float]


class SourceConfig(Validator, DictTypeAccessor):
    """Validate the source configuration.

    Must set from the JSON or internal types and validate the values.
    Getting the values returns the internal types.
    The to_json() method returns the JSON types.
    """

    def __init__(
        self,
        source: str = "BEST",
        scope: int = 127,
        limit: int = 20,
        underflow: str = "NEXT",
        **kwargs,
    ) -> None:
        """Initialize the class."""
        setattr(self, "source", source)
        setattr(self, "scope", scope)
        setattr(self, "limit", limit)
        setattr(self, "underflow", underflow)
        self._check_kwargs(kwargs)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def _check_kwargs(self, kwargs: dict[str, Any]) -> None:
        """Check the kwargs.
        The additional key word arguments must be one of these sets:
        = set() # No additional keys for BEST
        - {'minimum_distance', 'fitness_threshold', 'novelty_threshold'}  # DIVERSE
        - {'maximum_problem_distance', 'minimum_distance', 'tolerence'}  # RELATED
        - {'minimum_problem_distance', 'minimum_distance', 'tolerence'}  # UNRELATED
        - {'sse_limit', 'tolerence', 'min_generation', 'max_generation'}  # SPONTANEOUS
        """
        if self.source == "BEST":
            assert len(kwargs) == 0, f"Additional keys not allowed for BEST. {kwargs} specified."
        elif self.source == "DIVERSE":
            assert len(kwargs) == 3, "Invalid number of keys for DIVERSE."
            assert "minimum_distance" in kwargs, "Missing minimum_distance key."
            assert "fitness_threshold" in kwargs, "Missing fitness_threshold key."
            assert "novelty_threshold" in kwargs, "Missing novelty_threshold key."
        elif self.source == "RELATED":
            assert len(kwargs) == 3, "Invalid number of keys for RELATED."
            assert "maximum_problem_distance" in kwargs, "Missing maximum_problem_distance key."
            assert "minimum_distance" in kwargs, "Missing minimum_distance key."
            assert "tolerence" in kwargs, "Missing tolerence key."
        elif self.source == "UNRELATED":
            assert len(kwargs) == 3, "Invalid number of keys for UNRELATED."
            assert "minimum_problem_distance" in kwargs, "Missing minimum_problem_distance key."
            assert "minimum_distance" in kwargs, "Missing minimum_distance key."
            assert "tolerence" in kwargs, "Missing tolerence key."
        elif self.source == "SPONTANEOUS":
            assert len(kwargs) == 4, "Invalid number of keys for SPONTANEOUS."
            assert "sse_limit" in kwargs, "Missing sse_limit key."
            assert "tolerence" in kwargs, "Missing tolerence key"
            assert "minimum_generation" in kwargs, "Missing minimum_generation key."
            assert "maximum_generation" in kwargs, "Missing maximum_generation key."
        else:
            assert False, "Invalid source type."

    @property
    def source(self) -> str:
        """Get the source."""
        return self._source

    @source.setter
    def source(self, value: str) -> None:
        """The source of the genetic code."""
        if not self._is_one_of("source", value, INITIAL_POPULATION_SOURCES):
            raise ValueError(f"source must be one of {INITIAL_POPULATION_SOURCES}, but is {value}")
        self._source = value

    @property
    def scope(self) -> int:
        """Get the scope."""
        return self._scope

    @scope.setter
    def scope(self, value: int) -> None:
        """The scope of the source."""
        self._is_int("scope", value)
        self._in_range("scope", value, 1, 127)
        self._scope = value

    @property
    def limit(self) -> int:
        """Get the limit."""
        return self._limit

    @limit.setter
    def limit(self, value: int) -> None:
        """The maximum number of GC's allowed from this source."""
        self._is_int("limit", value)
        self._in_range("limit", value, 1, 2**31 - 1)
        self._limit = value

    @property
    def underflow(self) -> str:
        """Get the underflow."""
        return self._underflow

    @underflow.setter
    def underflow(self, value: str) -> None:
        """The underflow of the source."""
        self._is_one_of("underflow", value, UNDERFLOW_OPTIONS)
        self._underflow = value

    @property
    def minimum_distance(self) -> int:
        """Get the minimum_distance."""
        return self._minimum_distance

    @minimum_distance.setter
    def minimum_distance(self, value: int) -> None:
        """The minimum distance."""
        self._is_int("minimum_distance", value)
        self._in_range("minimum_distance", value, 1, 2**31 - 1)
        self._minimum_distance = value

    @property
    def fitness_threshold(self) -> float:
        """Get the fitness_threshold."""
        return self._fitness_threshold

    @fitness_threshold.setter
    def fitness_threshold(self, value: float) -> None:
        """The fitness threshold."""
        self._is_float("fitness_threshold", value)
        self._in_range("fitness_threshold", value, 0.0, 1.0)
        self._fitness_threshold = value

    @property
    def novelty_threshold(self) -> float:
        """Get the novelty_threshold."""
        return self._novelty_threshold

    @novelty_threshold.setter
    def novelty_threshold(self, value: float) -> None:
        """The novelty threshold."""
        self._is_float("novelty_threshold", value)
        self._in_range("novelty_threshold", value, 0.0, 1.0)
        self._novelty_threshold = value

    @property
    def maximum_problem_distance(self) -> int:
        """Get the maximum_problem_distance."""
        return self._maximum_problem_distance

    @maximum_problem_distance.setter
    def maximum_problem_distance(self, value: int) -> None:
        """The maximum problem distance."""
        self._is_int("maximum_problem_distance", value)
        self._in_range("maximum_problem_distance", value, 1, 2**31 - 1)
        self._maximum_problem_distance = value

    @property
    def minimum_problem_distance(self) -> int:
        """Get the minimum_problem_distance."""
        return self._minimum_problem_distance

    @minimum_problem_distance.setter
    def minimum_problem_distance(self, value: int) -> None:
        """The minimum problem distance."""
        self._is_int("minimum_problem_distance", value)
        self._in_range("minimum_problem_distance", value, 1, 2**31 - 1)
        self._minimum_problem_distance = value

    @property
    def tolerence(self) -> int:
        """Get the tolerence."""
        return self._tolerence

    @tolerence.setter
    def tolerence(self, value: int) -> None:
        """The tolerence."""
        self._is_int("tolerence", value)
        self._in_range("tolerence", value, 1, 2**31 - 1)
        self._tolerence = value

    @property
    def sse_limit(self) -> int:
        """Get the sse_limit."""
        return self._sse_limit

    @sse_limit.setter
    def sse_limit(self, value: int) -> None:
        """The sse limit."""
        self._is_int("sse_limit", value)
        self._in_range("sse_limit", value, 1, 2**31 - 1)
        self._sse_limit = value

    @property
    def minimum_generation(self) -> int:
        """Get the minimum_generation."""
        return self._minimum_generation

    @minimum_generation.setter
    def minimum_generation(self, value: int) -> None:
        """The minimum generation."""
        self._is_int("minimum_generation", value)
        self._in_range("minimum_generation", value, 0, 2**31 - 1)
        self._minimum_generation = value

    @property
    def maximum_generation(self) -> int:
        """Get the maximum_generation."""
        return self._maximum_generation

    @maximum_generation.setter
    def maximum_generation(self, value: int) -> None:
        """The maximum generation."""
        self._is_int("maximum_generation", value)
        self._in_range("maximum_generation", value, 0, 2**31 - 1)
        self._maximum_generation = value

    def to_json(self) -> dict[str, Any]:
        """Return the JSON representation of the configuration."""
        common = {
            "source": self.source,
            "scope": self.scope,
            "limit": self.limit,
            "underflow": self.underflow,
        }
        if self.source == "DIVERSE":
            return {
                **common,
                "minimum_distance": self.minimum_distance,
                "fitness_threshold": self.fitness_threshold,
                "novelty_threshold": self.novelty_threshold,
            }
        elif self.source == "RELATED":
            return {
                **common,
                "maximum_problem_distance": self.maximum_problem_distance,
                "minimum_distance": self.minimum_distance,
                "tolerence": self.tolerence,
            }
        elif self.source == "UNRELATED":
            return {
                **common,
                "minimum_problem_distance": self.minimum_problem_distance,
                "minimum_distance": self.minimum_distance,
                "tolerence": self.tolerence,
            }
        elif self.source == "SPONTANEOUS":
            return {
                **common,
                "sse_limit": self.sse_limit,
                "tolerence": self.tolerence,
                "minimum_generation": self.minimum_generation,
                "maximum_generation": self.maximum_generation,
            }
        else:
            return common


class PopulationConfig(Validator, DictTypeAccessor):
    """Validate the population configuration.

    Must set from the JSON or internal types and validate the values.
    Getting the values returns the internal types.
    The to_json() method returns the JSON types.
    """

    def __init__(
        self,
        uid: int,
        problem: str | bytes,
        worker_id: str | UUID,
        inputs: Sequence[int | str],
        outputs: Sequence[int | str],
        name: str,
        description: str | None,
        meta_data: str | None,
        created: datetime | str,
        updated: datetime | str,
        survivability_function: SurvivabilityFunction,
        fitness_function: FitnessFunction,
        best_source: SourceConfig | dict[str, Any] = SourceConfig(),
        diverse_source: SourceConfig | dict[str, Any] = SourceConfig(
            source="DIVERSE", minimum_distance=4, fitness_threshold=0.0, novelty_threshold=0.5
        ),
        related_source: SourceConfig | dict[str, Any] = SourceConfig(
            source="RELATED", maximum_problem_distance=4, minimum_distance=4, tolerence=10
        ),
        unrelated_source: SourceConfig | dict[str, Any] = SourceConfig(
            source="UNRELATED", minimum_problem_distance=5, minimum_distance=4, tolerence=10
        ),
        spontaneous_source: SourceConfig | dict[str, Any] = SourceConfig(
            source="SPONTANEOUS",
            sse_limit=100,
            tolerence=100,
            minimum_generation=0,
            maximum_generation=2**31 - 1,
        ),
    ) -> None:
        """Initialize the class."""
        setattr(self, "uid", uid)
        setattr(self, "problem", problem)
        setattr(self, "worker_id", worker_id)
        setattr(self, "inputs", inputs)
        setattr(self, "outputs", outputs)
        setattr(self, "name", name)
        setattr(self, "description", description)
        setattr(self, "meta_data", meta_data)
        setattr(self, "created", created)
        setattr(self, "updated", updated)
        setattr(self, "survivability_function", survivability_function)
        setattr(self, "fitness_function", fitness_function)
        setattr(self, "best_source", best_source)
        setattr(self, "diverse_source", diverse_source)
        setattr(self, "related_source", related_source)
        setattr(self, "unrelated_source", unrelated_source)
        setattr(self, "spontaneous_source", spontaneous_source)

    @property
    def uid(self) -> int:
        """Get the uid."""
        return self._uid

    @uid.setter
    def uid(self, value: int) -> None:
        """The uid of the population."""
        self._in_range("uid", value, 1, 2**15 - 1)
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
    def inputs(self) -> Interface:
        """Get the inputs."""
        return self._inputs

    @inputs.setter
    def inputs(
        self, value: Sequence[EndPoint] | Sequence[list | tuple] | Sequence[str | int | TypesDef]
    ) -> None:
        """The inputs."""
        self._is_sequence("inputs", value)
        self._inputs = Interface(value, SrcRow.I)

    @property
    def outputs(self) -> Interface:
        """Get the outputs."""
        return self._outputs

    @outputs.setter
    def outputs(
        self, value: Sequence[EndPoint] | Sequence[list | tuple] | Sequence[str | int | TypesDef]
    ) -> None:
        """The inputs."""
        self._is_sequence("inputs", value)
        self._outputs = Interface(value, DstRow.O)

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

    @property
    def best_source(self) -> SourceConfig:
        """Get the best_source."""
        return self._best_source

    @best_source.setter
    def best_source(self, value: SourceConfig | dict[str, Any]) -> None:
        """The best source."""
        if isinstance(value, dict):
            value = SourceConfig(**value)
        assert isinstance(value, SourceConfig), "best_source must be a SourceConfig"
        assert value.source == "BEST", f"best_source must be the BEST source but is {value.source}"
        self._best_source = value

    @property
    def diverse_source(self) -> SourceConfig:
        """Get the diverse_source."""
        return self._diverse_source

    @diverse_source.setter
    def diverse_source(self, value: SourceConfig | dict[str, Any]) -> None:
        """The diverse source."""
        if isinstance(value, dict):
            value = SourceConfig(**value)
        assert isinstance(value, SourceConfig), "diverse_source must be a SourceConfig"
        assert (
            value.source == "DIVERSE"
        ), f"diverse_source must be the DIVERSE source but is {value.source}"
        self._diverse_source = value

    @property
    def related_source(self) -> SourceConfig:
        """Get the related_source."""
        return self._related_source

    @related_source.setter
    def related_source(self, value: SourceConfig | dict[str, Any]) -> None:
        """The related source."""
        if isinstance(value, dict):
            value = SourceConfig(**value)
        assert isinstance(value, SourceConfig), "related_source must be a SourceConfig"
        assert (
            value.source == "RELATED"
        ), f"related_source must be the RELATED source but is {value.source}"
        self._related_source = value

    @property
    def unrelated_source(self) -> SourceConfig:
        """Get the unrelated_source."""
        return self._unrelated_source

    @unrelated_source.setter
    def unrelated_source(self, value: SourceConfig | dict[str, Any]) -> None:
        """The unrelated source."""
        if isinstance(value, dict):
            value = SourceConfig(**value)
        assert isinstance(value, SourceConfig), "unrelated_source must be a SourceConfig"
        assert (
            value.source == "UNRELATED"
        ), f"unrelated_source must be the UNRELATED source but is {value.source}"
        self._unrelated_source = value

    @property
    def spontaneous_source(self) -> SourceConfig:
        """Get the spontaneous_source."""
        return self._spontaneous_source

    @spontaneous_source.setter
    def spontaneous_source(self, value: SourceConfig | dict[str, Any]) -> None:
        """The spontaneous source."""
        if isinstance(value, dict):
            value = SourceConfig(**value)
        assert isinstance(value, SourceConfig), "spontaneous_source must be a SourceConfig"
        assert (
            value.source == "SPONTANEOUS"
        ), f"spontaneous_source must be the SPONTANEOUS source but is {value.source}"
        self._spontaneous_source = value

    def to_json(self) -> dict[str, Any]:
        """Return the JSON representation of the configuration."""
        return {
            "uid": self.uid,
            "problem": self.problem.hex(),
            "worker_id": str(self.worker_id),
            "inputs": self.inputs.to_json(),
            "outputs": self.outputs.to_json(),
            "name": self.name,
            "description": self.description,
            "meta_data": self.meta_data,
            "created": self.created.isoformat(),
            "updated": self.updated.isoformat(),
            # pylint: disable=no-member
            "survivability_function": self.survivability_function.__name__,
            "fitness_function": self.fitness_function.__name__,
            "best_source": self.best_source.to_json(),
            "diverse_source": self.diverse_source.to_json(),
            "related_source": self.related_source.to_json(),
            "unrelated_source": self.unrelated_source.to_json(),
            "spontaneous_source": self.spontaneous_source.to_json(),
        }


class PopulationsConfig(Validator, DictTypeAccessor):
    """Validate the populations configuration.

    Must set from the JSON or internal types and validate the values.
    Getting the values returns the internal types.
    The to_json() method returns the JSON types.
    """

    def __init__(
        self,
        worker_id: UUID | str = UUID("00000000-0000-0000-0000-000000000000"),
        configs: list[PopulationConfig] | list[dict[str, Any]] | None = None,
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
                self._configs = [
                    PopulationConfig(
                        uid=item["uid"],
                        problem=item["problem"],
                        worker_id=item["worker_id"],
                        inputs=item["inputs"],
                        outputs=item["outputs"],
                        name=item["name"],
                        description=item["description"],
                        meta_data=item["meta_data"],
                        created=item["created"],
                        updated=item["updated"],
                        survivability_function=item["survivability_function"],
                        fitness_function=item["fitness_function"],
                        best_source=item["best_source"],
                        diverse_source=item["diverse_source"],
                        related_source=item["related_source"],
                        unrelated_source=item["unrelated_source"],
                        spontaneous_source=item["spontaneous_source"],
                    )
                    for item in value
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
