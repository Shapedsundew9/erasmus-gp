"""Population configuration module."""
from datetime import datetime
from uuid import UUID, uuid4
from typing import Callable, TypedDict
from itertools import count
from egppy.common.common import NULL_UUID, Validator, NULL_SHA256_STR
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# Locally uniquie population id generator
_POPULATION_IDS: count = count(start=1, step=1)


FitnessFunction = Callable[[Callable], float]
SurvivabilityFunction = Callable[[Callable], float]

class _PopulationConfig(TypedDict):
    """Type definition."""

    uid: int
    egp_problem: str
    worker_id: UUID
    size: int
    inputs: list[str]
    outputs: list[str]
    ordered_interface_hash: int
    unordered_interface_hash: int
    name: str
    description: str | None
    meta_data: str | None
    created: datetime
    updated: datetime
    survivability_function: SurvivabilityFunction
    fitness_function: FitnessFunction

class _PopulationsConfig(TypedDict):
    """Type definition."""

    worker_id: UUID
    configs: list[_PopulationConfig]


class PopulationConfig(Validator):
    """Validate the population configuration."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the class."""
        self._uid: int = uid
        self._egp_problem: str = egp_problem
        self._worker_id: UUID = worker_id
        self._size: int = size
        self._inputs: list[str] = inputs
        self._outputs: list[str] = outputs
        self._ordered_interface_hash: int = ordered_interface_hash
        self._unordered_interface_hash: int = unordered_interface_hash
        self._name: str = name
        self._description: str | None = description
        self._meta_data: str | None = meta_data
        self._created: datetime = created
        self._updated: datetime = updated
        self._survivability_function: SurvivabilityFunction = survivability_function
        self._fitness_function: FitnessFunction = fitness_function