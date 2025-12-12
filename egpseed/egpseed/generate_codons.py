"""Generate codons."""

from copy import deepcopy
from datetime import datetime
from glob import glob
from json import load
from os.path import basename, dirname, join, splitext
from re import sub
from typing import Any

from egpcommon.common import (
    EGP_EPOCH,
    NULL_STR,
    SHAPEDSUNDEW9_UUID,
    ensure_sorted_json_keys,
    merge,
    sha256_signature,
)
from egpcommon.egp_log import DEBUG, Logger, egp_logger, enable_debug_logging
from egpcommon.properties import CGraphType, GCType
from egpcommon.security import dump_signed_json, load_signed_json_list
from egpcommon.spinner import Spinner
from egppy.genetic_code.c_graph import CGraph
from egppy.genetic_code.ggc_dict import GGCDict
from egppy.genetic_code.import_def import ImportDef
from egppy.genetic_code.json_cgraph import json_cgraph_to_interfaces, valid_jcg

# Standard EGP logging pattern
enable_debug_logging()
_logger: Logger = egp_logger(name=__name__)


OUTPUT_CODON_PATH = ("..", "..", "egppy", "egppy", "data", "codons.json")
CODON_TEMPLATE: dict[str, Any] = {
    "code_depth": 1,
    "cgraph": {"A": None, "O": None},
    "gca": None,
    "gcb": None,
    "ancestora": None,
    "ancestorb": None,
    "pgc": None,
    "creator": SHAPEDSUNDEW9_UUID,
    "created": EGP_EPOCH.isoformat(),
    "generation": 1,
    "num_codes": 1,
    "num_codons": 1,
    "properties": {
        "gc_type": GCType.CODON,
        # NOTE: The graph type does not have to be primitive.
        "graph_type": CGraphType.PRIMITIVE,
    },
    "meta_data": {"function": {"python3": {"0": {}}}},
}


def load_json_dict(file_path: str) -> dict[str, Any]:
    """Load a JSON file and return the dictionary.

    Arguments:
        file_path: Path to the JSON file.
    Returns:
        The JSON file as a dictionary.
    """
    with open(file_path, "r", encoding="utf-8") as json_file:
        return load(json_file)


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

        # All EGP types and methods must come from the physics module
        # This maintains the abstraction from the structure of egp* modules
        for imp in self.imports:
            if imp["aip"] and imp["aip"][0] == "egppy":
                assert imp["aip"][1] == "physics", f"Invalid EGP physical import: {imp['aip']}"

        # Other members
        self.description = method.get("description", "N/A")
        self.properties = method.get("properties", {})

        # PGC's have some specific requirements

        # 1. They must all import the RuntimeContext class
        is_pgc = self.properties.get("is_pgc", False)
        if is_pgc and not any(i["name"] == "RuntimeContext" for i in self.imports):
            self.imports.append(
                {
                    "aip": ["egppy", "physics", "runtime_context"],
                    "name": "RuntimeContext",
                }
            )

        # 2. They must use the "{pgc}" inline parameter to indicate where the PGC
        #    specific parameters go.
        if is_pgc:
            assert "{pgc}" in self.inline, "PGC codons must use the '{pgc}' inline parameter."

    def to_json(self) -> dict[str, Any]:
        """Convert to json."""
        json_dict = deepcopy(CODON_TEMPLATE)
        json_dict["meta_data"]["function"]["python3"]["0"]["inline"] = self.inline
        json_dict["meta_data"]["function"]["python3"]["0"]["description"] = self.description
        json_dict["meta_data"]["function"]["python3"]["0"]["name"] = self.name
        json_dict["meta_data"]["function"]["python3"]["0"]["imports"] = self.imports
        merge(json_dict["properties"], self.properties, update=True)
        json_dict["cgraph"]["A"] = [["I", idx, typ] for idx, typ in enumerate(self.inputs)]
        json_dict["cgraph"]["O"] = [["A", idx, typ] for idx, typ in enumerate(self.outputs)]
        assert valid_jcg(json_dict["cgraph"]), "Invalid codon connection graph at construction."
        json_dict["signature"] = sha256_signature(
            json_dict["ancestora"],
            json_dict["ancestorb"],
            json_dict["gca"],
            json_dict["gcb"],
            CGraph(json_cgraph_to_interfaces(json_dict["cgraph"])).to_json(True),  # type: ignore
            json_dict["pgc"],
            tuple(ImportDef(**md) for md in self.imports),
            self.inline,
            NULL_STR,
            int(datetime.fromisoformat(json_dict["created"]).timestamp()),
            json_dict["creator"].bytes,
        )
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
    5. Create the endpoint_types.json file.
    """

    # Load the raw codon data for each type. e.g.
    #     "dict": {"codon_name":{codon_definition...}, ...}
    codons: dict[str, dict[str, Any]] = {}
    spinner = Spinner("Generating codons...")
    spinner.start()
    for codon_file in glob(join(dirname(__file__), "data", "languages", "*", "*.json")):
        ensure_sorted_json_keys(codon_file)
        codon_json: dict[str, dict[str, Any]] = load_json_dict(codon_file)
        # NOTE: If the codon file is not for a base type then the inputs and outputs
        # will already be defined so bt will not be used.
        bt = splitext(basename(codon_file))[0].removeprefix("_")
        for name, definition in codon_json.items():  # Methods
            ipts = [f"-{bt}{i}" for i in range(definition.get("num_inputs", 2))]
            opts = [f"-{bt}{i}" for i in range(definition.get("num_outputs", 1))]
            definition.setdefault("inputs", ipts)
            definition.setdefault("outputs", opts)
            new_codon = GGCDict(MethodExpander(name, definition).to_json())
            # NOTE: verify() now raises exceptions on failure rather than returning False.
            new_codon.verify()
            codon = new_codon.to_json()
            assert valid_jcg(
                codon["cgraph"]  #  type: ignore
            ), "Invalid codon connection graph after verification."
            signature = codon["signature"]
            assert isinstance(signature, str), f"Invalid signature type: {type(signature)}"
            assert signature not in codons, f"Duplicate signature: {signature}"
            codons[signature] = codon

    # If we are debugging verify the signatures are correct
    if _logger.isEnabledFor(DEBUG) and not write:
        codon_dict = {
            c["signature"]: c
            for c in load_signed_json_list(join(dirname(__file__), *OUTPUT_CODON_PATH))
        }
        for sig, codon in codons.items():
            assert sig in codon_dict, f"Codon signature {sig} not found in existing codons."
            del codon["updated"]  # Ignore updated timestamp for comparison
            del codon_dict[sig]["updated"]
            for key in codon:
                assert key in codon_dict[sig], f"Codon key {key} not found in existing codon."
                assert (
                    codon[key] == codon_dict[sig][key]
                ), f"Codon key {key} does not match existing codon definition."
            for key in codon_dict[sig]:
                assert key in codon, f"Codon key {key} not found in new codon."

    # If we are writing the codons to a file then we need to ensure that the signatures are unique
    if write:
        dump_signed_json(
            list(codons.values()),
            join(dirname(__file__), *OUTPUT_CODON_PATH),
        )

    # Stop the spinner
    spinner.stop()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate codons.")
    parser.add_argument(
        "--write", "-w", action="store_true", help="If set, write the codons to a JSON file."
    )
    args = parser.parse_args()
    generate_codons(write=args.write)
