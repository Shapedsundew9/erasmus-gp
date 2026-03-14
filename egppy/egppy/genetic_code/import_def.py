"""EGP Import Definition Class.

Definitions of imports are needed for the EGP system to work. This class provides
a way to define imports in a way that is easy to use and understand. End point
type definitions use imports as do codons.
"""

from typing import Any, Sequence

from egpcommon.common import DictTypeAccessor
from egpcommon.egp_log import DEBUG, Logger, egp_logger
from egpcommon.validator import Validator

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


# Constants
EMPTY_STRING = ""


class ImportDef(Validator, DictTypeAccessor):
    """Class to define an import.

    ImportDef instances are read-only after construction. All validation
    occurs during __init__ and once set, attributes cannot be modified.
    """

    __slots__ = ("_aip", "_name", "_as_name", "_frozen")

    def __init__(self, aip: Sequence[str], name: str, as_name: str = EMPTY_STRING) -> None:
        """Initialize the ImportDef class

        Args
        ----
        aip: Sequence[str]: The Absolute Import Path of the import.
        name: str: The name of the import.
        as_name: str: The name to use for the import. This must be globally unique.
        """
        object.__setattr__(self, "_frozen", False)
        setattr(self, "aip", aip)
        setattr(self, "name", name)
        setattr(self, "as_name", as_name)
        object.__setattr__(self, "_frozen", True)

    def __delattr__(self, name: str) -> None:
        """Delete an attribute. Raises AttributeError if the object is read-only."""
        # pylint: disable=no-member
        if self._frozen:
            raise AttributeError(
                f"'{type(self).__name__}' object is read-only; cannot delete attribute '{name}'"
            )
        super().__delattr__(name)

    def __eq__(self, value: object) -> bool:
        """Check equality of ImportDef instances."""
        if not isinstance(value, ImportDef):
            return False
        return self.aip == value.aip and self.name == value.name and self.as_name == value.as_name

    def __hash__(self) -> int:
        """Unique hash for the import def."""
        return hash((self.aip, self.name, self.as_name))

    def __setattr__(self, name: str, value: Any) -> None:
        """Set an attribute. Raises AttributeError if the object is read-only."""
        if name == "_frozen":
            object.__setattr__(self, name, value)
            return
        # pylint: disable=no-member
        if hasattr(self, "_frozen") and self._frozen:
            raise AttributeError(
                f"'{type(self).__name__}' object is read-only; cannot set attribute '{name}'"
            )
        object.__setattr__(self, name, value)

    def __str__(self) -> str:
        """Return the string representation of the object."""
        base_str = f"from {'.'.join(self.aip)} import {self.name}"
        return base_str + " as " + self.as_name if self.as_name else base_str

    @property
    def aip(self) -> tuple[str, ...]:
        """Return the Absolute Import Path."""
        return self._aip

    @aip.setter
    def aip(self, value: Sequence[str]) -> None:
        """Set the Absolute Import Path."""
        if not self._is_sequence("aip", value):
            raise ValueError(f"aip must be a sequence, but is {type(value)}")
        if not len(value) > 0:
            raise ValueError("The aip must have at least one element.")
        if not all(isinstance(x, str) for x in value):
            raise ValueError("All elements of aip must be strings.")
        self._aip = tuple(value)

    @property
    def as_name(self) -> str:
        """Return the as name of the import."""
        return self._as_name

    @as_name.setter
    def as_name(self, value: str) -> None:
        """Set the as name of the import."""
        if _logger.isEnabledFor(level=DEBUG):
            self._is_string("as_name", value)
            self._is_length("as_name", value, 0, 64)
            self._is_printable_string("as_name", value)
        self._as_name = value

    @property
    def name(self) -> str:
        """Return the name of the import."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Set the name of the import."""
        if _logger.isEnabledFor(level=DEBUG):
            self._is_string("name", value)
            self._is_length("name", value, 1, 64)
            self._is_printable_string("name", value)
        self._name = value

    def to_json(self) -> dict[str, Any]:
        """Return the object as a JSON serializable dictionary."""
        return {"aip": list(self.aip), "name": self.name, "as_name": self.as_name}
