"""The genotype module.

An genotype is a single species in the population of species. It is a solution to the problem that
the genetic programming algorithm is trying to solve. The genotype module contains the
classes and functions that define the genotype and its properties to the problem. The problem
is defined by the user and the user instanciates the genotype class (to create phenotypes).
"""
from typing import Callable, Any
from abc import ABC, abstractmethod
from numpy import double, int64


# Constants
DOUBLE_ZERO = double(0.0)
INT64_ZERO = int64(0)
INT64_65536 = int64(2**16)


class StateABC(ABC):
    """The StateABC class.
    
    The state class defines the interface to the state of an instance of a genotype.
    i.e. the state of a phenotype. The state object is list-like in its basic
    indexed access.
    """

    def __init__(self) -> None:
        """Initialize the StateABC class."""

    @abstractmethod
    def __delitem__(self, index: int) -> None:
        """Delete the value type."""
        raise NotImplementedError("State.__delitem__ must be overridden")

    @abstractmethod
    def __getitem__(self, index: int) -> Any:
        """Return the value type."""
        raise NotImplementedError("State.__getitem__ must be overridden")

    @abstractmethod
    def __iter__(self) -> Any:
        """Iterate over the values."""
        raise NotImplementedError("State.__iter__ must be overridden")

    @abstractmethod
    def __len__(self) -> int:
        """Return the number of values."""
        raise NotImplementedError("State.__len__ must be overridden")

    @abstractmethod
    def __setitem__(self, index: int, value: Any) -> None:
        """Set the value type."""
        raise NotImplementedError("State.__setitem__ must be overridden")

    @abstractmethod
    def append(self, value: Any) -> None:
        """Append the value type."""
        raise NotImplementedError("State.append must be overridden")


class State(list[Any], StateABC):  # type: ignore
    """The state class"""


class Genotype:
    """The Genotype class."""

    def __init__(self, signature: bytes, func: Callable, puid: int) -> None:
        """Initialize a phenotype (an instance of a genotype).

        Args:
            signature (bytes): The signature of the Genetic Code.
            func (Callable): The executable function for the Genetic Code.
            puid (int): The genotype population UID.        
        """
        self.signature = signature  # The signature of GC
        self.func = func  # The executable function for the GC
        self.puid = puid  # The population UID
        self.state = State()  # The state of the genotype (which makes it a phenotype)
        self.memory = State()  # Dynamic memory for the phenotype (experiences)
        self.energy = INT64_65536  # The energy of the individual
        self.fitness = DOUBLE_ZERO  # The fitness of the individual
        self.survivability = DOUBLE_ZERO  # The survivability of the individual

    def execute(self, i: tuple) -> tuple:
        """Execute the individual."""
        assert self.energy > INT64_ZERO, "Individual is dead."
        return self.func(i)
