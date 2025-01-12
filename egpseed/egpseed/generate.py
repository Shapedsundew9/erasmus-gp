"""Generate codons."""

from copy import deepcopy
from datetime import UTC, datetime
from glob import glob
from os.path import basename, dirname, join, splitext
from typing import Any

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger, enable_debug_logging
from egpcommon.security import load_signed_json_dict, dump_signed_json
from egppy.gc_graph.end_point.end_point_type import ept_to_str
from egppy.gc_graph.end_point.types_def import TypesDef, types_db
from egppy.gc_types.ggc_class_factory import GGCDirtyDict
from egppy.problems.configuration import ACYBERGENESIS_PROBLEM

# Standard EGP logging pattern
enable_debug_logging()
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


CODON_PATH = ("..", "..", "egpdbmgr", "egpdbmgr", "data", "codons.json")
CODON_TEMPLATE: dict[str, Any] = {
    "graph": {"A": None, "O": None},
    "gca": None,
    "gcb": None,
    "creator": "22c23596-df90-4b87-88a4-9409a0ea764f",
    "created": datetime.now(UTC).isoformat(),
    "problem": ACYBERGENESIS_PROBLEM,
    "properties": {
        "constant": False,
        "deterministic": True,
        "simplification": False,
        "literal": False,
    },
    "meta_data": {"function": {"python3": {"0": {}}}},
}


class MethodExpander:
    """Method class."""

    def __init__(self, td: TypesDef, name: str, method: dict[str, Any]) -> None:
        """Initialize Method class."""
        super().__init__()
        self.inline = method["inline"]  # Must exist
        self.name = name
        type_str = ept_to_str((td,) + tuple(types_db["object"] for _ in range(td.tt())))

        # If neither exist then assume 2 inputs of type type_str
        if "num_inputs" not in method and "inputs" not in method:
            method["num_inputs"] = 2
        if "num_inputs" in method:
            self.num_inputs = method["num_inputs"]
            self.inputs = [type_str for _ in range(self.num_inputs)]
        else:
            self.num_inputs = len(method["inputs"])
            self.inputs = method["inputs"]

        # If neither exist then assume 1 output of type type_str
        if "num_outputs" not in method and "outputs" not in method:
            method["num_outputs"] = 1
        if "num_outputs" in method:
            self.num_outputs = method["num_outputs"]
            self.outputs = [type_str for _ in range(self.num_outputs)]
        else:
            self.num_outputs = len(method["outputs"])
            self.outputs = method["outputs"]

        # Other members
        self.description = method.get("description", "N/A")
        self.properties = method.get("properties", {})

    def to_json(self) -> dict[str, Any]:
        """Convert to json."""
        json_dict = deepcopy(CODON_TEMPLATE)
        json_dict["meta_data"]["function"]["python3"]["0"]["inline"] = self.inline
        json_dict["meta_data"]["function"]["python3"]["0"]["description"] = self.description
        json_dict["meta_data"]["function"]["python3"]["0"]["name"] = self.name
        json_dict["properties"].update(self.properties)
        json_dict["graph"]["A"] = [["I", idx, [typ]] for idx, typ in enumerate(self.inputs)]
        json_dict["graph"]["O"] = [["A", idx, [typ]] for idx, typ in enumerate(self.outputs)]
        return json_dict


def generate_codons() -> None:
    """Generate codons.

    1. Find all the JSON files in the python directory.
    2. Extract the name of the file. If it begins with '_' (for custom objects) remove it.
    3. Look up the name in the type definitions or default to the 'object' type.
    4. Load the JSON file.
    5. For each method in the JSON file:
        a. Create a MethodExpander object. This willl populate defaults e.g. the in/output types.
        b. Convert the MethodExpander object to a JSON object.
        c. Convert the JSON object to a GGCDirtyDict object. Populates more defaults & verifies.
        d. Convert the GGCDirtyDict object to a JSON object.
        e. Add the JSON object to the codons dictionary.
    6. Save the codons dictionary to a JSON file.
    """
    codons: list[dict[str, Any]] = []
    for json_file in sorted(glob(join(dirname(__file__), "data", "languages", "python", "*.json"))):
        td: TypesDef = types_db.get(splitext(basename(json_file))[0].removeprefix("_"))
        for name, definition in load_signed_json_dict(json_file).items():  # Methods
            codons.append(GGCDirtyDict(MethodExpander(td, name, definition).to_json()).to_json())
    dump_signed_json(codons, join(dirname(__file__), *CODON_PATH))


if __name__ == "__main__":
    generate_codons()
