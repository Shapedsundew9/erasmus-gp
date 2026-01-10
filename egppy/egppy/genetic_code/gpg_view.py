"""The Gene Pool Genetic Code dictionary view class module.

The Need for a Third Type: Gene Pool Genetic Code (GPG Code)
 - The Gene Pool is a database schema designed for efficient querying.
 - The GGCDict is not optimized for this. The GPG code acts as a necessary layer of abstraction.
 - Its role is to take information from the GG code, ignore unnecessary fields, and derive
   necessary fields for the database schema.
 - Examples of derived fields include the input and output interface fields (types and indexes),
   which are sourced from the C-graph (the source of truth). These are derived and stored as the
   GG code is written to the Gene Pool, rather than being stored within the evolving EG/GG code
   itself.
 - The GPGC Dict isolates the Gene Pool database schema from the structure of the GGC Dict.
 - It is a transient type; it is not stored itself but is the format used for updating and
   inserting data into the Gene Pool.
 - Communication of genetic codes for fitness assessment must occur through the Gene Pool
   (or be independent of incomplete codes), reinforcing the need for this isolated, complete
   representation.
"""

from collections.abc import Mapping
from copy import deepcopy
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from egpcommon.egp_log import DEBUG, Logger, egp_logger
from egpcommon.properties import PropertiesBD
from egppy.genetic_code.c_graph_abc import FrozenCGraphABC
from egppy.genetic_code.c_graph_constants import DstIfKey, SrcIfKey
from egppy.genetic_code.genetic_code import GCABC
from egppy.genetic_code.types_def_store import types_def_store

_logger: Logger = egp_logger(name=__name__)


# TODO: Once stable this should become a slotted class for performance.
# Noting that it is a lower priority as it is a transient type.
class GPGCView(Mapping):
    """The Gene Pool Genetic Code dictionary view class.

    This class is a pared-down version of the GGCDict, using only the fields
    necessary for the Gene Pool database schema. It derives certain fields from
    the C-graph to ensure completeness and consistency with the database requirements.

    The implementation inherits from GGCDict to leverage existing functionality,
    **and share the underlying data** while overriding the initialization to derive
    the necessary fields and provide methods specific to the Gene Pool schema /
    database interactions.
    """

    __slots__ = ("_src", "_drvd")

    def __init__(self, ggcode: GCABC):
        """Initialize the GPGCDict from a GGCDict-like dictionary.

        Args:
            ggcode (GGCDict): A GGCDict instance.
        """
        self._src: GCABC = ggcode
        self._drvd: dict[str, Any] = {}
        cgrph = self._src["cgraph"]
        self._drvd["input_types"], self._drvd["inputs"] = cgrph[SrcIfKey.IS].types_and_indices()
        self._drvd["output_types"], self._drvd["outputs"] = cgrph[DstIfKey.OD].types_and_indices()
        self._drvd["updated"] = datetime.now(UTC)
        assert not any(
            key in self._src for key in self._drvd
        ), "Derived keys overlap with source keys in GPGCView."

    def __getitem__(self, key: str) -> Any:
        """Get an item from the GPGC view.

        Args:
            key (str): The key to retrieve.
        Returns:
            Any: The value associated with the key.
        """
        if key in self._src:
            return self._src[key]
        return self._drvd[key]

    def __iter__(self):
        """Return an iterator over the GPGC view keys."""
        for key in self._src:
            yield key
        for key in self._drvd:
            yield key

    def __len__(self) -> int:
        """Return the number of items in the GPGC view."""
        return len(self._src) + len(self._drvd)

    def to_json(self) -> dict[str, int | str | float | list | dict]:
        """Return a JSON serializable dictionary."""
        retval = {}
        # Only keys that are persisted in the DB are included in the JSON.
        for key in self._src.GC_KEY_TYPES:
            if not self._src.GC_KEY_TYPES[key]:
                continue  # Skip non-persistent keys
            value = self.get(key)
            if key == "meta_data":
                assert isinstance(value, dict), "Meta data must be a dict."
                md = deepcopy(value)
                if (
                    "function" in md
                    and "python3" in md["function"]
                    and "0" in md["function"]["python3"]
                    and "imports" in md["function"]["python3"]["0"]
                ):
                    md["function"]["python3"]["0"]["imports"] = [
                        imp.to_json() for imp in self["imports"]
                    ]
                retval[key] = md
            elif key == "properties":
                # Make properties humman readable.
                assert isinstance(value, int), "Properties must be an int."
                retval[key] = PropertiesBD(value).to_json()
            elif isinstance(value, GCABC):
                # Must get signatures from GC objects first otherwise will recursively
                # call this function.
                retval[key] = value["signature"].hex() if value is not None else None
            elif isinstance(value, FrozenCGraphABC):
                # Need to set json_c_graph to True so that the endpoints are correctly serialized
                retval[key] = value.to_json(json_c_graph=True)
            elif key.endswith("_types") and isinstance(value, list):
                retval[key] = [types_def_store[t].name for t in self[key]]
            elif getattr(self[key], "to_json", None) is not None:
                retval[key] = self[key].to_json()
            elif isinstance(value, bytes):
                retval[key] = value.hex()
            elif value is None:
                retval[key] = None
            elif isinstance(value, datetime):
                retval[key] = value.isoformat()
            elif isinstance(value, UUID):
                retval[key] = str(value)
            else:
                retval[key] = value
                if _logger.isEnabledFor(DEBUG):
                    assert isinstance(
                        value, (int, str, float, list, dict, tuple)
                    ), f"Invalid type: {type(value)}"
        return retval
