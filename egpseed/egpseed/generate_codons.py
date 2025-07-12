"""Generate codons."""

from copy import deepcopy
from datetime import UTC, datetime
from glob import glob
from itertools import product
from math import prod
from os.path import basename, dirname, join, splitext
from re import findall
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
from egppy.genetic_code.types_def import types_def_store
from egppy.problems.configuration import ACYBERGENESIS_PROBLEM
from egpseed.generate_types import parse_toplevel_args

# Standard EGP logging pattern
enable_debug_logging()
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# Some codon definitions have been specialized to avoid particularly complicated
# type combinations that are not supported by the EGP. These are exceptions to the
# rule that codons must have an input or output with the full base type.
FBT_EXCEPTIONS: set[str] = {"-Iterable0[-EGPNumber0]", "-Iterable0[-Sized0]"}

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

    def __init__(self, name: str, method: dict[str, Any]) -> None:
        """Initialize Method class."""
        super().__init__()
        self.inline = method["inline"]  # Must exist
        self.name = name
        self.num_inputs = len(method["inputs"])
        self.num_outputs = len(method["outputs"])
        self.inputs = method["inputs"]
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
        rsd: dict[str, list[str]] = {
            rt: sorted(
                t.name
                for t in types_def_store.decendants(rt[1:-1])
                if t.tt() == 0 and not t.abstract
            )
            for rt in rset
        }

        if prod((len(v) for v in rsd.values())) > 2**10:
            # If there are too many combinations of relative types then first we remove
            # any custom or abstract types i.e. those that start with a capital letter
            rsd = {
                rt: sorted(v for v in vs if v[0].islower() or len(vs) == 1)
                for rt, vs in rsd.items()
            }
            # If there are still too many combinations then we reduce the
            # number of relative types by halving the length of the longest list
            # until it is less than 2**16.
            # This is a brute force approach but it is simple and effective.
            while prod((len(v) for v in rsd.values())) > 2**10:
                # Find the longest list of relative types
                max_len_rt: str = max(rsd, key=lambda k: len(rsd[k]))
                assert (
                    len(rsd[max_len_rt]) > 1
                ), f"Relative type {max_len_rt} has only one value: {rsd[max_len_rt]}"
                # Reduce the longest list by half (rounding up)
                rsd[max_len_rt] = rsd[max_len_rt][: (len(rsd[max_len_rt]) + 1) // 2]

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

            # Make sure the types are valid. It is possible to create invalid combinations.
            if all(i in types_def_store for i in inputs + outputs):
                if len(io_combos) > 2**16:
                    raise ValueError("Too many combinations of input and output types. ")
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
    #   "dict": {"base": "-dict0[-Hashable0, -Any0]", ...}.
    type_json: dict[str, dict[str, Any]] = {
        t.split("[")[0]: d | {"base": t.replace(t.split("[")[0], f"-{t.split('[')[0]}0")}
        for t, d in load_signed_json_dict(join(dirname(__file__), *TYPES_PATH)).items()
    }

    # Load the raw codon data for each type. e.g.
    #     "dict": {"codon_name":{codon_definition...}, ...}
    codon_json: dict[str, dict[str, dict[str, Any]]] = {}
    for codon_file in glob(join(dirname(__file__), "data", "languages", "python", "*.json")):
        base_type = splitext(basename(codon_file))[0].removeprefix("_")
        codon_json[base_type] = load_signed_json_dict(codon_file)

    # Cache of full base types for each codon json.
    # Cache is lazily populated as we process each codon json.
    # dict[base type, full base type]
    fbt_cache: dict[str, str] = {}

    # The giant list of codons to write out.
    codons: dict[str, dict[str, Any]] = {}

    # cjtb = codon json type bases
    # If this is a type codon json file then we need to ensure that the type is defined
    # Files like _constants.json or random.json are not *type* codon files and so no
    # types need substituting.
    for base_type in sorted(k for k in codon_json if k in types_def_store and k > "Con"):
        # For each qualifying base type we set up a queue of work to do.
        # The work is to populate a list of groups of codon definitions from the
        # inheritance hierarchy of the type. This involves the following steps:
        spinner = Spinner(f"Processing {base_type}")
        spinner.start()

        # 1. Base type and full reference type of the top level type definition
        # into the queue of work. A this point the full reference type is the full base type.
        qow: list[tuple[str, str]] = [(base_type, type_json[base_type]["base"])]
        codon_groups: list[dict[str, dict]] = []
        while qow:
            # 1. Get the full reference type from the work queue and find the full base type
            #    i.e. the mapping from the child type (frt) to the
            #    parent type (fbt). e.g. reversible[-Any0] -> reversible[-Hashable8]
            #    (e.g. for KeysView)
            # 2. Mapping the subtypes e.g. -Any0 -> -Hashable8
            # 3. Replacing the subtypes in the codon definitions with the reference type mappings.
            # 4. Appending the modified codons to the list of codon groups to merge.
            # 5. Appending the parents and full reference types to the work queue.
            #
            # Until the work queue is empty we repeat the above steps.
            # 6. Merge all the codon groups in reverse order (to respect inheritance)
            # 7. For each codon definition create the matrix of concrete type codons.

            # 1. Determine the full_base_type. Base_type is something like "dict"
            # but we need to ensure that the type is fully defined with all sub-types as it is in
            # the codon definitions. There are some rules to this:
            #   i.  If the type is tt==0 then the full_base_type is f"-{base_type}0"
            #         a. If input types are not specified they are assumed to be base_type
            #         b. If the number of inputs is not specified it is assumed to be 2
            #         c. If the output types are not specified they are assumed to be base_type
            #         d. If the number of outputs is not specified it is assumed to be 1
            #         e. Each assumed type is assumed to be a different template
            #   ii. If the type is tt > 0 then the full_base_type *will* be specified in input
            #      and output type strings that start f"-{base_type}0".
            bt, frt = qow.pop()
            cjtb: dict[str, dict[str, Any]] = codon_json[bt]
            if bt not in fbt_cache:
                fbt_set: set[str] = {type_json[bt]["base"]}
                for codon_def in cjtb.values():
                    ipts = [f"-{bt}{i}" for i in range(codon_def.get("num_inputs", 2))]
                    opts = [f"-{bt}{i}" for i in range(codon_def.get("num_outputs", 1))]
                    inputs = codon_def.setdefault("inputs", ipts)
                    outputs = codon_def.setdefault("outputs", opts)
                    all_types = set(inputs + outputs)
                    fbt_set.update(t for t in all_types if t.startswith(f"-{bt}0"))
                fbt_set -= FBT_EXCEPTIONS
                assert len(fbt_set) == 1, f"Type {bt} is inconsistently defined: {fbt_set}"
                fbt_cache[bt] = fbt_set.pop()
            fbt = fbt_cache[bt]

            # 2. Mapping the subtypes
            #   i.   Unpack the top level arguments from the fbt & frt
            #   ii.  Where each argument differs make a mapping of the sub-type
            #        to avoid name collisions (i.e. if we are mapping Any to Hashable we want to
            #        avoid accidentally mapping an Any that is not the template we are looking for).
            #        we ensure the mapping is to a template number >7 which is not supported in tt
            #        so we know is available e.g. -Any0 -> -Hashable8
            #        NOTE: The code only looks for 1 digit so we are limited to 8 & 9 but this is
            #        more than sufficient for now.
            fbt_args: list[str] = parse_toplevel_args(fbt)
            frt_args: list[str] = parse_toplevel_args(frt)
            tt_map: dict[str, str] = {fbt: frt}
            for rt1, rt2 in zip(fbt_args, frt_args):
                if rt1 != rt2:
                    # If the base type is not the same as the reference type then we need to
                    # map the sub-type to a new template number.
                    # e.g. -Any0 -> -Hashable8
                    # NOTE: We assume that the sub-type is always a relative type
                    # (i.e. starts with '-')
                    assert rt2.startswith("-"), f"Type {rt2} is not a relative type."
                    assert rt2[-1].isdigit(), f"Type {rt2} is not a valid template type."
                    assert rt2[-2].isalpha(), f"Type {rt2} is not a valid template type."
                    tt_map[rt1] = (
                        f"-{rt2[1:-1]}{rt2[-1] if rt2[-1] in '89' else str(int(rt2[-1]) + 8)}"
                    )

            # 3. Replace the sub-types in the codon definitions.
            #    i.   Make a copy of the codon definitions for the base type
            #    ii.  For each codon definition replace the sub-types with the reference sub-types
            #         in all the input and output type strings.
            #    iii. Append the modified codon definitions to the codon groups
            codon_group: dict[str, dict[str, Any]] = deepcopy(cjtb)
            for codon_def in codon_group.values():
                for rt1, rt2 in tt_map.items():
                    # Replace the base type with the full base type
                    codon_def["inputs"] = [ipt.replace(rt1, rt2) for ipt in codon_def["inputs"]]
                    codon_def["outputs"] = [opt.replace(rt1, rt2) for opt in codon_def["outputs"]]

            # 4. Append the modified codon definitions to the codon groups
            codon_groups.append(codon_group)

            # 5. Append the parents and full reference types to the work queue.
            #    i.   Get the parents of the base type from the type definitions
            #    ii.  For each parent type, get the full reference type and append to the work queue
            #         e.g. for "KeysView[-Hashable0]" a parent is
            #         "Reversible[-Hashable0]" which is the full reference type to the parent base
            #         type "Reversible[-Any0]
            for parent in type_json[bt].get("parents", []):
                if parent.startswith("EGP"):
                    # EGP types are placeholder base types so can be skipped.
                    continue
                pbt = parent.split("[")[0]
                qow.append((pbt, frt))

        # 6. Merge all the codon groups in reverse order (to respect inheritance)
        full_codon_set = {}
        for codon_group in reversed(codon_groups):
            full_codon_set.update(codon_group)

        # 7. For each codon definition create the matrix of concrete type codons.
        prev_len = len(codons)
        for name, definition in full_codon_set.items():  # Methods
            for ggc_json in MethodExpander(name, definition).to_json():
                new_codon = GGCDict(ggc_json)
                new_codon.consistency()
                codon = new_codon.to_json()
                signature = codon["signature"]
                assert isinstance(signature, str), f"Invalid signature type: {type(signature)}"
                codons[signature] = codon
        spinner.stop(f"(Added {len(codons) - prev_len} codons: Total {len(codons)})")

    # If we are writing the codons to a file then we need to ensure that the signatures are unique
    if write:
        dump_signed_json(list(codons.values()), join(dirname(__file__), *OUTPUT_CODON_PATH))


if __name__ == "__main__":
    generate_codons(False)
