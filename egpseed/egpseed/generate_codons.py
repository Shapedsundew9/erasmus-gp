"""Generate codons."""

from copy import deepcopy
from datetime import UTC, datetime
from glob import glob
from itertools import product
from os.path import basename, dirname, join, splitext
from re import findall, split
from typing import Any

from egpcommon.egp_log import (
    CONSISTENCY,
    DEBUG,
    VERIFY,
    Logger,
    egp_logger,
    enable_debug_logging,
)
from egpcommon.properties import CGraphType, GCType
from egpcommon.security import dump_signed_json, load_signed_json_dict
from egpcommon.spinner import Spinner
from egppy.genetic_code.ggc_class_factory import NULL_SIGNATURE, GGCDict
from egppy.genetic_code.types_def import TypesDef, types_def_store
from egppy.problems.configuration import ACYBERGENESIS_PROBLEM

# Standard EGP logging pattern
enable_debug_logging()
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


TYPES_PATH = ("data", "types.json")
OUTPUT_CODON_PATH = ("..", "..", "egpdbmgr", "egpdbmgr", "data", "codons.json")
CODON_TEMPLATE: dict[str, Any] = {
    "code_depth": 1,
    "cgraph": {"A": None, "O": None, "U": []},
    "gca": NULL_SIGNATURE,
    "gcb": NULL_SIGNATURE,
    "creator": "22c23596-df90-4b87-88a4-9409a0ea764f",
    "created": datetime.now(UTC).isoformat(),
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

    # Flag for printing a warning about too many relative type combinations
    warned = False

    def __init__(self, td: TypesDef, name: str, method: dict[str, Any]) -> None:
        """Initialize Method class."""
        super().__init__()
        self.inline = method["inline"]  # Must exist
        self.name = name

        # If neither exist then assume 2 inputs of type type_str
        if "num_inputs" not in method and "inputs" not in method:
            method["num_inputs"] = 2
        if "num_inputs" in method:
            assert "inputs" not in method, "Cannot have both num_inputs and inputs."
            self.num_inputs = method["num_inputs"]
            self.inputs = [td.name for _ in range(self.num_inputs)]
        else:
            self.num_inputs = len(method["inputs"])
            self.inputs = method["inputs"]

        # If neither exist then assume 1 output of type type_str
        if "num_outputs" not in method and "outputs" not in method:
            method["num_outputs"] = 1
        if "num_outputs" in method:
            assert "outputs" not in method, "Cannot have both num_outputs and outputs."
            self.num_outputs = method["num_outputs"]
            self.outputs = [td.name for _ in range(self.num_outputs)]
        else:
            self.num_outputs = len(method["outputs"])
            self.outputs = method["outputs"]

        # Method imports if there are any
        self.imports = method.get("imports", [])

        # Other members
        self.description = method.get("description", "N/A")
        self.properties = method.get("properties", {})

        # Generate the input type combinations and output type combinations
        self.io_combos = self.generate_io_combos()

    def generate_io_combos(self) -> list[tuple[tuple[str, ...], tuple[str, ...]]]:
        """Generate the valid input and output type combinations.

        There are a few restrictions to prevent things from exploding:
         - decendants of relative types must be tt==0 (not container variants)
         - more than 4 relative types is not supported (too many combinations)
         - more than 2 "Any" relative types is not supported (too many combinations)
        """

        # 1. Expand each input & output type into its components
        # 2. Collect the set of types into tset
        #       e.g. {Any0, Hashable0, int, str, ...}
        # 3. Collect the set of relative type labels into rset
        #       e.g. {-Any0, -Hashable0, ...}
        # 4. Create a dictionary or relative types to valid relative type choices in rsd
        #       e.g. {-Any0: [Any, float, ...], -Hashable0: [int, str, ...], ...}
        #       NOTE: Relative types are "find & replace" labels and all other types are fixed.
        io_list: list[str] = self.inputs + self.outputs
        egph_flag: bool = "EGPHighest" in io_list
        rset: set[str] = {t for tl in io_list for t in findall(r"-.*?[0-9]", tl)}
        rsd: dict[str, tuple[str, ...]] = {
            rt: tuple(t.name for t in types_def_store.decendants(rt[1:-1]) if t.tt() == 0)
            for rt in rset
        }

        # Implement constraints to prevent runtime explosion
        if len(rset) > 4:
            if not MethodExpander.warned:
                print("WARNING: More than 4 relative types is not supported. Truncating.")
                MethodExpander.warned = True
            for i in range(2, 10):
                if f"-Any{i}" in rsd:
                    rsd[f"-Any{i}"] = ("Any",)
            count = sum(len(v) > 1 for v in rsd.values())
            assert count <= 4, "More than 4 relative types is not supported."

        # rsd is a map of each relative type to all the values it can take.
        # Each set of input and output types has each relative type replaced with one of its values.
        # 6. Create all combinations of relative types
        if not rsd:
            # If there are no relative types then we can just return the single combination
            assert not egph_flag, "EGPHighest should not be used with static types."
            return [(tuple(self.inputs), tuple(self.outputs))]

        io_combos: list[tuple[tuple[str, ...], tuple[str, ...]]] = []
        for rcombo in product(*[rsd[rt] for rt in rsd]):
            # Replace relative types in input and output types with their values
            inputs: list[str] = self.inputs.copy()
            outputs: list[str] = self.outputs.copy()
            # For each relative type, replace it in the inputs and outputs with the current combo
            for rt, typ in zip(rsd.keys(), rcombo):
                inputs = [t.replace(rt, typ) for t in inputs]
                outputs = [t.replace(rt, typ) for t in outputs]
            # If EGPHighest is used, we need to replace it with the highest (closest ot object) type
            if egph_flag:
                # Highest could be a parameter at the end of inthe inputs list
                highest = min(
                    (types_def_store[i] for i in inputs if i != "EGPHighest"), key=lambda x: x.depth
                )
                inputs = [t.replace("EGPHighest", highest.name) for t in inputs]
                outputs = [t.replace("EGPHighest", highest.name) for t in outputs]
            io_combos.append((tuple(inputs), tuple(outputs)))
        return io_combos

    def to_json(self) -> list[dict[str, Any]]:
        """Convert to json."""
        json_list: list[dict[str, Any]] = []
        for io_combo in self.io_combos:
            json_dict = deepcopy(CODON_TEMPLATE)
            json_dict["meta_data"]["function"]["python3"]["0"]["inline"] = self.inline
            json_dict["meta_data"]["function"]["python3"]["0"]["description"] = self.description
            json_dict["meta_data"]["function"]["python3"]["0"]["name"] = self.name
            json_dict["meta_data"]["function"]["python3"]["0"]["imports"] = self.imports
            json_dict["properties"].update(self.properties)
            json_dict["cgraph"]["A"] = [["I", idx, typ] for idx, typ in enumerate(io_combo[0])]
            json_dict["cgraph"]["O"] = [["A", idx, typ] for idx, typ in enumerate(io_combo[1])]
            json_list.append(json_dict)
        return json_list


def generate_codons(write: bool = False) -> None:
    """Generate codons.

    Arguments:
        write: If True, write the codons to a JSON file.

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
    7. Verify the signatures are unique.
    8. Create the end_point_types.json file.
    """

    # Load the types template definitions (need this to map sub-types to parent types).
    # Store template types (tt > 0) with just the base type name and add a "base" key to the dict.
    # with the fully defined base name. This is so we can match the type to the codon file.
    # e.g. "dict[-Hashable0, -Any0]" will be stored as
    #   "dict": {"base": "dict[-Hashable0, -Any0]", ...}.
    type_json: dict[str, dict[str, Any]] = {
        t.split("[")[0]: d | {"base": t}
        for t, d in load_signed_json_dict(join(dirname(__file__), *TYPES_PATH)).items()
    }

    # Load the raw codon data for each type. e.g.
    #     "dict": {"codon_name":{codon_definition...}, ...}
    codon_json: dict[str, dict[str, dict[str, Any]]] = {}
    for codon_file in glob(join(dirname(__file__), "data", "languages", "python", "*.json")):
        base_type = splitext(basename(codon_file))[0].removeprefix("_")
        codon_json[base_type] = load_signed_json_dict(codon_file)

    # cjtb = codon json type bases
    for base_type, cjtb in codon_json.items():
        # If this is a type codon json file then we need to ensure that the type is defined
        # Files like _constants.json or random.json are not *type* codon files and so no
        # types need substituting.
        if base_type in types_def_store:
            # Next we need to determine the full_base_type. Base_type is something like "dict"
            # but we need to ensure that the type is fully defined with all sub-types as it is in
            # the codon definitions. There are some rules to this:
            #   1. If the type is tt==0 then the full_base_type is f"-{base_type}0"
            #      a. If input types are not specified they are assumed to be base_type
            #      b. If the number of inputs is not specified it is assumed to be 2
            #      c. If the output types are not specified they are assumed to be base_type
            #      d. If the number of outputs is not specified it is assumed to be 1
            #   2. If the type is tt > 0 then the full_base_type *will* be specified in input
            #      and output type strings that start f"-{base_type}0".
            fbt_set: set[str] = set()
            dft = f"-{base_type}0"
            for codon_def in cjtb.values():
                ipts = [dft] * codon_def.get("num_inputs", 2)
                opts = [dft] * codon_def.get("num_outputs", 1)
                inputs = codon_def.setdefault("inputs", ipts)
                outputs = codon_def.setdefault("outputs", opts)
                all_types = set(inputs + outputs)
                fbt_set.update(t for t in all_types if t.startswith(dft))
            assert len(fbt_set) == 1, f"Type {base_type} is inconsistently defined: {fbt_set}"
            full_base_type = fbt_set.pop()

            # The ancestors method gets base_type and all ancestors down to "object" (the
            # root type).
            # To ensure inheritance works correctly we build the type codon definitions from
            # "object" up and then any overides are correctly applied.
            # NOTE: This does result in overwrites of the same thing but not worth the effort
            # to optimize
            # e.g. "dict": {object codons} | ... | {mutable_mapping codons} | {dict codons}
            for typ in reversed(types_def_store.ancestors(base_type)):
                cjtb.update(codon_json[typ.name.split("[")[0]])

            # Now codon_json[base_type] is a complete dictionary of codon definitions for the type
            # but the sub-types (when tt > 0) are not mapped. The classic example (and the one that
            # caused the issue to refactor this) is the "dict" type which has 2 subtypes
            # "dict[-Hashable0, -Any0]"
            # but inherits from "Container[-Any0]" where the "-Any0" in this case is actually the
            # "-Hashable0" sub-type.
            # The following code does that mapping so that the codon template have the right
            # input and output type templates for the top level type.

            # 1. Build type template mappings (order matters): Every mention of the fully defined
            # parent type in input position 0 or output position 0 is replaced with the fully
            # defined base type name (which for codon definitions always includes the template
            # markers '-' and '0')
            tbtd = type_json[base_type]
            assert tbtd["base"].replace(base_type, f"-{base_type}0") == full_base_type, (
                f"Type {base_type} is not defined correctly in types.json: "
                f"{tbtd['base']} != -{base_type}0"
            )
            assert full_base_type.count(base_type) == 1, f"Type {base_type} is recursively defined!"
            fbtp = {p: p.split("[")[0] for p in tbtd["parents"]}
            tt_map = {pb.replace(p, f"-{p}0"): full_base_type for pb, p in fbtp.items()}
            print(tt_map)

    exit()
    codons: list[dict[str, Any]] = []
    spinner = Spinner(f"Processing {base_type}")
    spinner.start()
    for td in types_def_store.get(base_type):
        for name, definition in load_signed_json_dict(codon_file).items():  # Methods
            for ggc_json in MethodExpander(td, name, definition).to_json():
                new_codon = GGCDict(ggc_json)
                new_codon.consistency()
                codons.append(new_codon.to_json())
    spinner.stop(f"({len(codons)} codons)")
    if write:
        dump_signed_json(codons, join(dirname(__file__), *OUTPUT_CODON_PATH))

    # Verify the signatures are unique
    # This check picks up any errors in sigurature generation or type defintions
    signature_set = set()
    for codon in codons:
        assert codon["signature"] not in signature_set, f"Duplicate signature: {codon['signature']}"
        signature_set.add(codon["signature"])


if __name__ == "__main__":
    generate_codons(False)
