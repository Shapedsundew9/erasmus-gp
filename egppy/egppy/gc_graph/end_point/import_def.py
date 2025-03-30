"""EGP Import Definition Class.

Definitions of imports are needed for the EGP system to work. This class provides
a way to define imports in a way that is easy to use and understand. End point
type definitions use imports as do codons.
"""

from typing import Any, Sequence

from egpcommon.common import DictTypeAccessor
from egpcommon.validator import Validator
from egpcommon.object_set import ObjectSet


# Constants
EMPTY_STRING = ""


class ImportDef(Validator, DictTypeAccessor):
    """Class to define an import."""

    def __init__(self, aip: Sequence[str], name: str, as_name: str = EMPTY_STRING) -> None:
        """Initialize the ImportDef class

        Args
        ----
        aip: Sequence[str]: The Absolute Import Path of the import.
        name: str: The name of the import.
        as_name: str: The name to use for the import. This must be globally unique.
        """
        super().__init__()
        setattr(self, "aip", aip)
        setattr(self, "name", name)
        setattr(self, "as_name", as_name)

    def __eq__(self, value: object) -> bool:
        """Check equality of ImportDef instances."""
        if not isinstance(value, ImportDef):
            return NotImplemented
        return self.key() == value.key()

    def __hash__(self) -> int:
        """Unique hash for the import def."""
        return self.key()

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
        self._is_sequence("aip", value)
        assert len(value) > 0, "The aip must have at least one element."
        assert all(isinstance(x, str) for x in value), "All elements of aip must be strings."
        self._aip = tuple(value)

    @property
    def name(self) -> str:
        """Return the name of the import."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Set the name of the import."""
        self._is_string("name", value)
        self._is_length("name", value, 1, 64)
        self._is_printable_string("name", value)
        self._name = value

    @property
    def as_name(self) -> str:
        """Return the as name of the import."""
        return self._as_name

    @as_name.setter
    def as_name(self, value: str) -> None:
        """Set the as name of the import."""
        self._is_string("as_name", value)
        self._is_length("as_name", value, 0, 64)
        self._is_printable_string("as_name", value)
        self._as_name = value

    def key(self) -> int:
        """Return the key for the import definition."""
        return hash((self.aip, self.name, self.as_name))

    def to_json(self) -> dict[str, Any]:
        """Return the object as a JSON serializable dictionary."""
        return {"aip": list(self.aip), "name": self.name, "as_name": self.as_name}


class ImportDefStore(ObjectSet):
    """Class to store ImportDef objects."""


import_def_store: ImportDefStore = ImportDefStore("Import Def Store")
