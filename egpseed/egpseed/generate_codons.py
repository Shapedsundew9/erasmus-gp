"""Generate codons."""

from copy import deepcopy
from glob import glob
from os.path import basename, dirname, join, splitext
from re import sub
from typing import Any

from egpcommon.common import EGP_EPOCH
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger, enable_debug_logging
from egpcommon.properties import CGraphType, GCType
from egpcommon.security import dump_signed_json, load_signed_json_dict
from egpcommon.spinner import Spinner
from egppy.genetic_code.ggc_class_factory import NULL_SIGNATURE, GGCDict
from egppy.problems.configuration import ACYBERGENESIS_PROBLEM

# Standard EGP logging pattern
enable_debug_logging()
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


OUTPUT_CODON_PATH = ("..", "..", "egpdbmgr", "egpdbmgr", "data", "codons.json")
CODON_TEMPLATE: dict[str, Any] = {
    "code_depth": 1,
    "cgraph": {"A": None, "O": None, "U": []},
    "gca": NULL_SIGNATURE,
    "gcb": NULL_SIGNATURE,
    "creator": "22c23596-df90-4b87-88a4-9409a0ea764f",
    "created": EGP_EPOCH.isoformat(),
    "generation": 1,
    "num_codes": 1,
    "num_codons": 1,
    "problem": ACYBERGENESIS_PROBLEM,
    "properties": {
        "gc_type": GCType.CODON,
        # NOTE: The graph type does not have to be primitive.
        "graph_type": CGraphType.PRIMITIVE,
        "constant": False,
        "deterministic": True,
        "side_effects": False,
        "static_creation": True,
        "gctsp": {"literal": False},
    },
    "meta_data": {"function": {"python3": {"0": {}}}},
}


class MethodExpander:
    """Method class."""

    trans_tbl = str.maketrans("0123456789", "-" * 10)

    def __init__(self, name: str, method: dict[str, Any]) -> None:
        """Initialize Method class."""
        super().__init__()
        self.inline = method["inline"]  # Must exist
        self.name = name
        self.num_inputs = len(method["inputs"])
        self.num_outputs = len(method["outputs"])
        self.inputs = [sub(r"-(\w+)\d\b", r"\1", i) for i in method["inputs"]]
        self.outputs = [sub(r"-(\w+)\d\b", r"\1", o) for o in method["outputs"]]
        # EGPHighest is a special type that is used to indicate the highest numeric
        # type in the inputs.
        # It is not a valid type for codons so we replace it with EGPNumber.
        self.outputs = [o.replace("EGPHighest", "EGPNumber") for o in self.outputs]

        # Method imports if there are any
        self.imports = method.get("imports", [])

        # Other members
        self.description = method.get("description", "N/A")
        self.properties = method.get("properties", {})

    def to_json(self) -> dict[str, Any]:
        """Convert to json."""
        json_dict = deepcopy(CODON_TEMPLATE)
        json_dict["meta_data"]["function"]["python3"]["0"]["inline"] = self.inline
        json_dict["meta_data"]["function"]["python3"]["0"]["description"] = self.description
        json_dict["meta_data"]["function"]["python3"]["0"]["name"] = self.name
        json_dict["meta_data"]["function"]["python3"]["0"]["imports"] = self.imports
        json_dict["properties"].update(self.properties)
        json_dict["cgraph"]["A"] = [["I", idx, typ] for idx, typ in enumerate(self.inputs)]
        json_dict["cgraph"]["O"] = [["A", idx, typ] for idx, typ in enumerate(self.outputs)]
        return json_dict


def generate_codons(write: bool = False) -> None:
    """Generate codons.

    Arguments:
        write: If True, write the codons to a JSON file.

    1. Find all the JSON files in the python directory.
    2. Load each JSON file and parse the codon definitions.
    3. Create a codon for each definition using the types defined.
        NOTE: The types are templated using a preceding '-' and a trailing digit
        to indicate the template index. Parameters with the same type template must
        all have exactly the same type (and be of a type in the template type name hierarchy).
        These feature is not used any more for codon generation (it got too complex) but
        remains as the effort was put in and it may be useful in the future. For now only the
        base type codons are created and it is left to EGP to expand the input and output types
        to the concrete types using meta codons (type cast codons). This is a more robust
        approach as the type cast codons can do runtime validation of the types thus proving
        the type is correct.
    4. Save the codons dictionary to a JSON file.
    5. Create the end_point_types.json file.
    """

    # Load the raw codon data for each type. e.g.
    #     "dict": {"codon_name":{codon_definition...}, ...}
    codons: dict[str, dict[str, Any]] = {}
    spinner = Spinner("Generating codons...")
    spinner.start()
    for codon_file in glob(join(dirname(__file__), "data", "languages", "python", "*.json")):
        codon_json: dict[str, dict[str, Any]] = load_signed_json_dict(codon_file)
        # NOTE: If the codon file is not for a base type then the inputs and outputs
        # will already be defined so bt will not be used.
        bt = splitext(basename(codon_file))[0].removeprefix("_")
        for name, definition in codon_json.items():  # Methods
            ipts = [f"-{bt}{i}" for i in range(definition.get("num_inputs", 2))]
            opts = [f"-{bt}{i}" for i in range(definition.get("num_outputs", 1))]
            definition.setdefault("inputs", ipts)
            definition.setdefault("outputs", opts)
            new_codon = GGCDict(MethodExpander(name, definition).to_json())
            new_codon.consistency()
            codon = new_codon.to_json()
            signature = codon["signature"]
            assert isinstance(signature, str), f"Invalid signature type: {type(signature)}"
            assert signature not in codons, f"Duplicate signature: {signature}"
            codons[signature] = codon
    spinner.stop()

    # If we are writing the codons to a file then we need to ensure that the signatures are unique
    if write:
        dump_signed_json(list(codons.values()), join(dirname(__file__), *OUTPUT_CODON_PATH))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate codons.")
    parser.add_argument(
        "--write", "-w", action="store_true", help="If set, write the codons to a JSON file."
    )
    args = parser.parse_args()
    generate_codons(write=args.write)
