"""Generate types_def.json from types.json.

This script generates a comprehensive type definition file (`types_def.json`) from a raw type
specification (`types.json`). It processes type definitions, expands template types, establishes
parent-child relationships, and assigns unique identifiers (UIDs) to each type. The script performs
multiple passes to handle complex type hierarchies, template instantiations, and special
cases such as pairs and triplets. It ensures all relationships are correctly established,
sets type depths, and serializes the final structure to JSON for downstream use in
genetic programming or type analysis.

Main steps:
1. Parse and initialize type definitions from `types.json`.
2. Expand template types and create concrete instances.
3. Establish parent-child relationships for all types.
4. Expand types with template parameters (tt == 1 and tt == 2).
5. Handle special cases for pairs and triplets.
6. Remove unused or abstract template types.
7. Assign depth values based on type hierarchy.
8. Generate unique UIDs for each type using bit fields.
9. Serialize and write the final type definitions to `types_def.json`.
"""

from copy import deepcopy
from itertools import count
from json import load
from os.path import dirname, join
from re import search
from typing import Any

from bitdict import BitDictABC, bitdict_factory

from egpcommon.common import ensure_sorted_json_keys
from egpcommon.security import dump_signed_json
from egppy.genetic_code.types_def_bit_dict import TYPESDEF_CONFIG

# The XUID_ZERO_NAMES are the names that are reserved for the xuid 0.
XUID_ZERO_NAMES: set[str] = {"tuple"}


# Location of the types_def.json file
TYPES_DEF_FILE = join(dirname(__file__), "..", "..", "egppy", "egppy", "data", "types_def.json")


def parse_toplevel_args(type_string: str) -> list[str]:
    """
    Extracts top-level, comma-separated arguments from within the first
    and last square brackets of a string, correctly handling nested brackets.
    """
    # Step 1: Use a greedy regex to find the content between the
    # first '[' and the last ']'.
    match = search(r"\[(.*)\]", type_string)

    # If no brackets are found or they are empty, return an empty list.
    if not match or not match.group(1):
        return []

    content = match.group(1)

    # Step 2: Manually parse the content to split by top-level commas.
    _args = []
    bracket_level = 0
    current_arg_start_index = 0

    for i, char in enumerate(content):
        if char == "[":
            bracket_level += 1
        elif char == "]":
            bracket_level -= 1
        elif char == "," and bracket_level == 0:
            # This comma is at the top level, so it's a delimiter.
            # Extract the argument found so far.
            arg = content[current_arg_start_index:i].strip()
            _args.append(arg)
            # Set the starting point for the next argument.
            current_arg_start_index = i + 1

    # After the loop, add the final argument (the one after the last comma).
    last_arg = content[current_arg_start_index:].strip()
    if last_arg:
        _args.append(last_arg)

    return _args


class TTCounters:
    """Template Type Counters.
    This class is responsible for generating unique template type IDs.
    With knowledge of the existing type definitions it can generate
    unique IDs for new types.
    """

    def __init__(self, existing_uid_map: dict[int, str]) -> None:
        # NOTE: xuid 0 is reserved for the Any type, so the counters start at 1.
        self.counters: list[count[int]] = [  # pylint: disable=unsubscriptable-object
            count(1) for _ in range(8)
        ]
        self.existing_uid_map = existing_uid_map
        self.tdbd: type[BitDictABC] = bitdict_factory(TYPESDEF_CONFIG)

    def __getitem__(self, tt: int) -> int:
        """Get the next unique ID for the given template type."""
        if tt < 0 or tt >= len(self.counters):
            raise ValueError(f"Invalid template type: {tt}")
        while True:
            uid = self.tdbd(
                {
                    "tt": tt,
                    "xuid": next(self.counters[tt]),
                }
            ).to_int()
            # The tt_counters are used to generate unique xuid values for each type in each
            # template type (TT).
            if uid in self.existing_uid_map:
                # If the generated UID already exists, we need to find a new one.
                continue
            return uid


def generate_types_def(write: bool = False) -> None:
    """Generate the types_def.json file from the types.json file.

    Arguments:
        write: If True, write the generated types to a JSON file. When False, just perform
               generation/validation without writing, matching the CLI pattern used elsewhere.
    """
    # The types.json file is a raw definition of types.
    # Only non-default key:value pairs are stored in the file and
    # container types (TT > 0) are all defined with their root types e.g. "dict[Hashable, Any]"
    types_file = join(dirname(__file__), "data", "types.json")
    ensure_sorted_json_keys(types_file)
    with open(types_file, encoding="utf-8") as f:
        types: dict[str, dict[str, Any]] = load(f)

    # Load any existing types_def.json file to preserve UIDs where possible
    # and create an efficient reverse mapping of UID to type name.
    with open(TYPES_DEF_FILE, encoding="utf-8") as f:
        existing_types_def: dict[str, dict[str, Any]] = load(f)
    existing_uid_map: dict[int, str] = {
        v["uid"]: k for k, v in existing_types_def.items() if "uid" in v
    }
    tt_counters = TTCounters(existing_uid_map)

    # Multiple passes are made of the types as some types are defined in terms of others. Pass:
    #   1. Creates a new type definition dictionary with unique names and UIDs.
    #   2. Ensures that all parent-child relationships are established correctly.
    #   3. Creates explicit sub-types e.g. Expand the 'Any' in Iterable[Any] to include all types.
    #   4. Expand types that are defined with tt == 2
    #   5. Special handling for Pair types, which are products of dicts, ItemsView etc.
    #   6: Special Pairs: Some Pairs are required as children of other base types.
    #   7: Strip remaining templated types.
    #   8. Establish parent-child relationships for new type definitions.
    #   9. Set depths. The depth is the number of edges from the root type (object) to the type.
    #  10. JSON-ize the fields and add a UID to each type definition.
    #  11: Convert the parents and children sets to sorted lists.
    #  12: Assertions
    #  11. Write the new type definition dictionary to a JSON file.

    # Pass 1: Create the new type definition dictionary.
    trans_tbl = str.maketrans("0123456789", "-" * 10)
    new_tdd: dict[str, dict[str, Any]] = {}
    for name, definition in types.items():
        if "name" not in definition:
            definition["name"] = name

        # These are the fields that are needed to create a new type definition.
        # NOTE: That the types.json file may define other fields that are not used here.
        # e.g. "tt"
        new_tdd[definition["name"]] = {
            "name": definition.get("name"),
            "imports": definition.get("imports", []),
            "parents": definition.get("parents", ["object"]),
            "children": definition.get("children", set()),
            "abstract": definition.get("abstract", False),
            "meta": definition.get("meta", False),
            "depth": definition.get("depth", 0),
            "default": definition.get("default"),
            "tt": definition.get("tt", 0),
        }
        if name == "object":
            # The object type is the root type and has no parents.
            # NOTE: Will cause an infinite loop if anything else.
            new_tdd[definition["name"]]["parents"] = []
        if new_tdd[definition["name"]]["tt"] > 0:
            # If the type is a template type, then make a 0 tt ("Any") version of it.
            tt_name: str = definition["name"].split("[")[0]
            new_tdd[tt_name] = deepcopy(new_tdd[definition["name"]])
            new_tdd[tt_name]["name"] = tt_name
            new_tdd[tt_name]["tt"] = 0
            new_tdd[tt_name]["abstract"] = True
            new_tdd[tt_name]["parents"] = [
                p.split("[")[0] for p in new_tdd[definition["name"]]["parents"]
            ]

        # The generic type definition for tt > 1 (tt == 1 is handled in pass 2)
        if new_tdd[definition["name"]]["tt"] > 1:
            new_name = name.translate(trans_tbl).replace("-", "")
            new_tdd[new_name] = deepcopy(new_tdd[name])
            new_tdd[new_name]["name"] = new_name
            new_tdd[new_name]["parents"] = [
                p.translate(trans_tbl).replace("-", "") for p in new_tdd[name]["parents"]
            ]

    # Pass 2: Establish parent-child relationships for concrete types (tt=0 initially).
    new_tdd["Any"]["children"] = set(nd["name"] for nd in new_tdd.values() if nd["tt"] == 0)
    new_tdd["Any"]["children"].remove("Any")  # Remove self-reference
    type_list = list(nd for nd in new_tdd.values() if nd["tt"] == 0)
    while type_list:
        td = type_list.pop(0)
        for parent in td["parents"]:
            # If the parent is not in the new_tdd dictionary, it should be a tt=1 template type.
            # NOTE: No other undefined parent types are supported at this time.
            if parent not in new_tdd:
                assert "[" in parent, (
                    f"Parent '{parent}' is not defined in new_tdd and does "
                    "not appear to be a template type (missing '[')."
                )
                parent_template = None
                for key in new_tdd:
                    if key.startswith(parent[: parent.find("[") + 1]):
                        parent_template = key
                        break
                if parent_template is None:
                    raise ValueError(
                        f"Parent template '{parent}' not found in new_tdd. "
                        "Please define it in types.json or add the capability here."
                    )
                template: str = parent_template[
                    parent_template.find("[") + 1 : parent_template.rfind("]")
                ]
                template_type: str = parent[parent.find("[") + 1 : parent.rfind("]")]
                assert (
                    parent_template[: parent_template.find("[") + 1] + template_type + "]" == parent
                ), f"Parent template '{parent}' does not match."

                # Create a new type definition for the parent template if it doesn't exist.
                template = template.replace(", ...", "")
                template_type = template_type.replace(", ...", "")
                new_tdd[parent] = deepcopy(new_tdd[parent_template])
                new_tdd[parent]["name"] = parent
                new_tdd[parent]["parents"] = {
                    p.replace(template, template_type) for p in new_tdd[parent_template]["parents"]
                }

                # The new type definition is a concrete type that is utilized by other types so
                # it can be added to the type_list for further processing.
                type_list.append(new_tdd[parent])
                new_tdd["Any"]["children"].add(parent)

            # Add the current type to the parent's children set.
            new_tdd[parent]["children"].add(td["name"])

    # Pass 3: Expand types that are defined with tt == 1, e.g. Iterable[Any] to include all types.
    tt1_tuple = tuple(nd for nd in new_tdd.values() if nd["tt"] == 1)
    for td in tt1_tuple:
        # Find what base class the type is a template of.
        name: str = td["name"]
        start: int = name.find("[-")
        end: int = name.rfind("0]")

        # Special case for tuple[x, ...] where the ellipsis is not part of the template.
        if end == -1 and start != -1:
            end = name.rfind("0, ...]")
        assert start == end == -1 or start < end, f"Malformed name template: {name}"

        # Template flag indicates whether the type is a template type.
        flag: bool = start != -1
        if not flag:
            base_class = name[name.find("[") + 1 : name.rfind("]")].replace(", ...", "")
        else:
            # Remove the ellipsis if it exists in the template name.
            # tuple[x, ...] should be the only case where this is used.
            base_class = name[start + 2 : end]

        if base_class == "Any":
            # If the base class is Any, then all types are sub-types.
            sub_types = new_tdd["Any"]["children"].copy()
            sub_types.add("Any")
        else:
            # Search the type tree for all valid sub-types of the base class.
            search_tree: set[str] = new_tdd[base_class]["children"].copy()
            sub_types: set[str] = {base_class}  # Start with the base class itself.
            while search_tree:
                current = search_tree.pop()
                search_tree.update(new_tdd[current]["children"])
                sub_types.add(current)

        # Add the sub-types to the type definition.
        template = "-" + base_class + "0" if flag else base_class
        for st in sub_types:
            # Replace the template with the sub-type name and
            # create a new concrete type definition.
            # NOTE: That the type may already exist as a concrete parent of a scalar
            # type (i.e. created in Phase 2)
            new_name = name.replace(template, st)
            if new_name not in new_tdd:
                new_tdd[new_name] = deepcopy(td)
                new_tdd[new_name]["name"] = new_name
                if flag:
                    new_tdd[new_name]["parents"] = {p.replace(template, st) for p in td["parents"]}
                # The subtype may require imports
                impt_names = set(imp["name"] for imp in new_tdd[new_name]["imports"])
                for imp in (
                    impt for impt in new_tdd[st]["imports"] if impt["name"] not in impt_names
                ):
                    new_tdd[new_name]["imports"].append(imp)

        # Remove the templated entry from the new type definition dictionary.
        if flag:
            del new_tdd[name]

    # Pass 4: Expand types that are defined with tt == 2
    # NOTE: We exclude all abstract & meta sub-types to reduce the volume of types
    # created with the exception
    # of Hashable, which is an abstract type but is used as a sub-type of many types.
    # pylint: disable=pointless-string-statement
    """
    for td in tuple(nd for nd in new_tdd.values() if nd["tt"] == 2):
        # Find what base class the type is a template of.
        name: str = td["name"]
        parameters: list[str] = parse_toplevel_args(name)
        assert len(parameters) == 2, f"Malformed name template: {name}"
        base_classes: list[str] = [p[1:-1] if p[0] == "-" else p for p in parameters]
        sub_types_list: list[set[str]] = []

        for parameter, base_class in zip(parameters, base_classes):
            flag: bool = parameter[0] == "-"
            if base_class == "Any":
                # If the base class is Any, then all types are sub-types.
                sub_types_list.append(
                    {
                        c
                        for c in new_tdd["Any"]["children"]
                        if not (new_tdd[c]["abstract"] or new_tdd[c]["meta"]) or c == "Hashable"
                    }
                )
                sub_types_list[-1].add("Any")
            else:
                # Search the type tree for all valid sub-types of the base class.
                search_tree: set[str] = {
                    c
                    for c in new_tdd[base_class]["children"]
                    if not (new_tdd[c]["abstract"] or new_tdd[c]["meta"]) or c == "Hashable"
                }
                sub_types_list.append({base_class})
                while search_tree:
                    current = search_tree.pop()
                    search_tree.update(
                        {
                            c
                            for c in new_tdd[current]["children"]
                            if not (new_tdd[c]["abstract"] or new_tdd[c]["meta"]) or c == "Hashable"
                        }
                    )
                    sub_types_list[-1].add(current)

        # Add the sub-types to the type definition.
        for st0 in sub_types_list[0]:
            for st1 in sub_types_list[1]:
                # Skip [Any, Any] as it is already defined as a tt==0 type.
                if st0 == "Any" and st1 == "Any":
                    continue
                # Replace the template with the sub-type name and
                # create a new concrete type definition.
                # NOTE: That the type may already exist as a concrete parent of a scalar
                # type (i.e. created in Phase 2)
                new_name = name.replace(parameters[1], st1).replace(parameters[0], st0)
                if new_name not in new_tdd:
                    new_tdd[new_name] = deepcopy(td)
                    new_tdd[new_name]["name"] = new_name
                    if parameters[0][0] == "-":
                        new_tdd[new_name]["parents"] = {
                            p.replace(parameters[0], st0) for p in td["parents"]
                        }
                    if parameters[1][0] == "-":
                        new_tdd[new_name]["parents"] = {
                            p.replace(parameters[1], st1) for p in new_tdd[new_name]["parents"]
                        }
                    # The subtype may require imports
                    impt_names = set(imp["name"] for imp in new_tdd[new_name]["imports"])
                    for imp in (
                        impt for impt in new_tdd[st0]["imports"] if impt["name"] not in impt_names
                    ):
                        new_tdd[new_name]["imports"].append(imp)
                    for imp in (
                        impt for impt in new_tdd[st1]["imports"] if impt["name"] not in impt_names
                    ):
                        new_tdd[new_name]["imports"].append(imp)
    """

    # Pass 5: Pairs - since Pairs (tuple[Any, Any]) are products of dicts they are treated as
    # as a concrete type that can be used in tt == 1 Containers. Any type that has a Hashable
    # type as a parameter can be expanded to include all Pair types.
    """
    pairs: list[str] = [p for p in new_tdd if p.startswith("Pair[")]
    for td in tt1_tuple:
        # Find what base class the type is a template of.
        name: str = td["name"]
        start: int = name.find("[-")
        end: int = name.rfind("0]")

        # Special case for tuple[x, ...] where the ellipsis is not part of the template.
        if end == -1 and start != -1:
            end = name.rfind("0, ...]")
        assert start == end == -1 or start < end, f"Malformed name template: {name}"

        # Template flag indicates whether the type is a template type.
        flag: bool = start != -1
        if not flag:
            base_class = name[name.find("[") + 1 : name.rfind("]")].replace(", ...", "")
        else:
            # Remove the ellipsis if it exists in the template name.
            # tuple[x, ...] should be the only case where this is used.
            base_class = name[start + 2 : end]

        # Add the sub-types to the type definition.
        template = "-" + base_class + "0" if flag else base_class
        for st in pairs:
            # Replace the template with the sub-type (pair) name and
            # create a new concrete type definition.
            # NOTE: That the type may already exist as a concrete parent of a scalar
            # type (i.e. created in Phase 2)
            new_name = name.replace(template, st)
            if new_name not in new_tdd:
                new_tdd[new_name] = deepcopy(td)
                new_tdd[new_name]["name"] = new_name
                if flag:
                    new_tdd[new_name]["parents"] = {p.replace(template, st) for p in td["parents"]}
                impt_names = set(imp["name"] for imp in new_tdd[new_name]["imports"])
                for imp in (
                    impt for impt in new_tdd[st]["imports"] if impt["name"] not in impt_names
                ):
                    new_tdd[new_name]["imports"].append(imp)
    """
    # Pass 6: Special: Some types are required as children of other base types.

    # Needed by str.partition (and rpartition)
    new_tdd["Triplet[str, str, str]"] = deepcopy(new_tdd["Triplet[-Any0, -Any1, -Any2]"])
    new_tdd["Triplet[str, str, str]"]["name"] = "Triplet[str, str, str]"
    new_tdd["Triplet[str, str, str]"]["parents"] = ["tuple[str, ...]"]
    new_tdd["Triplet[Bytes, Bytes, Bytes]"] = deepcopy(new_tdd["Triplet[-Any0, -Any1, -Any2]"])
    new_tdd["Triplet[Bytes, Bytes, Bytes]"]["name"] = "Triplet[Bytes, Bytes, Bytes]"
    new_tdd["Triplet[Bytes, Bytes, Bytes]"]["parents"] = ["tuple[Bytes, ...]"]

    # Parent of Itemsview
    new_tdd["Set[Pair[Hashable, Any]]"] = deepcopy(new_tdd["Set[Hashable]"])
    new_tdd["Set[Pair[Hashable, Any]]"]["name"] = "Set[Pair[Hashable, Any]]"
    new_tdd["Set[Pair[Hashable, Any]]"]["parents"] = ["Collection[Pair[Hashable, Any]]"]

    # Parent of the above
    new_tdd["Collection[Pair[Hashable, Any]]"] = deepcopy(new_tdd["Collection[Hashable]"])
    new_tdd["Collection[Pair[Hashable, Any]]"]["name"] = "Collection[Pair[Hashable, Any]]"
    new_tdd["Collection[Pair[Hashable, Any]]"]["parents"] = [
        "Iterable[Pair[Hashable, Any]]",
        "Sized",
        "Container[Pair[Hashable, Any]]",
    ]

    # Parent of the above
    new_tdd["Iterable[Pair[Hashable, Any]]"] = deepcopy(new_tdd["Iterable[Any]"])
    new_tdd["Iterable[Pair[Hashable, Any]]"]["name"] = "Iterable[Pair[Hashable, Any]]"
    new_tdd["Iterable[Pair[Hashable, Any]]"]["parents"] = ["object"]

    # Parent of the above
    new_tdd["Container[Pair[Hashable, Any]]"] = deepcopy(new_tdd["Container[Any]"])
    new_tdd["Container[Pair[Hashable, Any]]"]["name"] = "Container[Pair[Hashable, Any]]"
    new_tdd["Container[Pair[Hashable, Any]]"]["parents"] = ["object"]

    # Sub-type of the above
    new_tdd["Pair[Hashable, Any]"] = deepcopy(new_tdd["Pair[Any, Any]"])
    new_tdd["Pair[Hashable, Any]"]["name"] = "Pair[Hashable, Any]"
    new_tdd["Pair[Hashable, Any]"]["parents"] = ["tuple"]

    # Parent of itemsview
    new_tdd["Reversible[Pair[Hashable, Any]]"] = deepcopy(new_tdd["Reversible[Any]"])
    new_tdd["Reversible[Pair[Hashable, Any]]"]["name"] = "Reversible[Pair[Hashable, Any]]"
    new_tdd["Reversible[Pair[Hashable, Any]]"]["parents"] = ["Iterable[Pair[Hashable, Any]]"]

    # Needed for divmod
    new_tdd["Pair[EGPNumber, EGPNumber]"] = deepcopy(new_tdd["Pair[Any, Any]"])
    new_tdd["Pair[EGPNumber, EGPNumber]"]["name"] = "Pair[EGPNumber, EGPNumber]"
    new_tdd["Pair[EGPNumber, EGPNumber]"]["parents"] = ["tuple"]

    # Needed for enumeration (including of keys)
    new_tdd["Pair[int, Any]"] = deepcopy(new_tdd["Pair[Any, Any]"])
    new_tdd["Pair[int, Any]"]["name"] = "Pair[int, Any]"
    new_tdd["Pair[int, Any]"]["parents"] = ["tuple"]
    new_tdd["Pair[int, Hashable]"] = deepcopy(new_tdd["Pair[Any, Any]"])
    new_tdd["Pair[int, Hashable]"]["name"] = "Pair[int, Hashable]"
    new_tdd["Pair[int, Hashable]"]["parents"] = ["tuple"]
    new_tdd["Iterator[Pair[int, Any]]"] = deepcopy(new_tdd["Iterator[Any]"])
    new_tdd["Iterator[Pair[int, Any]]"]["name"] = "Iterator[Pair[int, Any]]"
    new_tdd["Iterator[Pair[int, Any]]"]["parents"] = ["Iterable[Pair[int, Any]]"]
    new_tdd["Iterator[Pair[int, Hashable]]"] = deepcopy(new_tdd["Iterator[Any]"])
    new_tdd["Iterator[Pair[int, Hashable]]"]["name"] = "Iterator[Pair[int, Hashable]]"
    new_tdd["Iterator[Pair[int, Hashable]]"]["parents"] = ["Iterable[Pair[int, Hashable]]"]
    new_tdd["Iterable[Pair[int, Any]]"] = deepcopy(new_tdd["Iterable[Any]"])
    new_tdd["Iterable[Pair[int, Any]]"]["name"] = "Iterable[Pair[int, Any]]"
    new_tdd["Iterable[Pair[int, Any]]"]["parents"] = ["object"]
    new_tdd["Iterable[Pair[int, Hashable]]"] = deepcopy(new_tdd["Iterable[Any]"])
    new_tdd["Iterable[Pair[int, Hashable]]"]["name"] = "Iterable[Pair[int, Hashable]]"
    new_tdd["Iterable[Pair[int, Hashable]]"]["parents"] = ["object"]

    # Needed for mapping iteration
    new_tdd["Iterator[Pair[Hashable, Any]]"] = deepcopy(new_tdd["Iterator[Any]"])
    new_tdd["Iterator[Pair[Hashable, Any]]"]["name"] = "Iterator[Pair[Hashable, Any]]"
    new_tdd["Iterator[Pair[Hashable, Any]]"]["parents"] = ["Iterable[Pair[Hashable, Any]]"]

    # Needed for integer_as_ratio
    new_tdd["Pair[int, int]"] = deepcopy(new_tdd["Pair[Any, Any]"])
    new_tdd["Pair[int, int]"]["name"] = "Pair[int, int]"
    new_tdd["Pair[int, int]"]["parents"] = ["tuple"]

    # Needed for zip()
    # Pair
    new_tdd["Iterator[Pair[Any, Any]]"] = deepcopy(new_tdd["Iterator[Any]"])
    new_tdd["Iterator[Pair[Any, Any]]"]["name"] = "Iterator[Pair[Any, Any]]"
    new_tdd["Iterator[Pair[Any, Any]]"]["parents"] = ["Iterable[Pair[Any, Any]]"]
    new_tdd["Iterable[Pair[Any, Any]]"] = deepcopy(new_tdd["Iterable[Any]"])
    new_tdd["Iterable[Pair[Any, Any]]"]["name"] = "Iterable[Pair[Any, Any]]"
    new_tdd["Iterable[Pair[Any, Any]]"]["parents"] = ["object"]

    # Triplet
    new_tdd["Iterable[Triplet[Any, Any, Any]]"] = deepcopy(new_tdd["Iterable[Any]"])
    new_tdd["Iterator[Triplet[Any, Any, Any]]"] = deepcopy(new_tdd["Iterator[Any]"])
    new_tdd["Iterator[Triplet[Any, Any, Any]]"]["name"] = "Iterator[Triplet[Any, Any, Any]]"
    new_tdd["Iterator[Triplet[Any, Any, Any]]"]["parents"] = ["Iterable[Triplet[Any, Any, Any]]"]
    new_tdd["Iterable[Triplet[Any, Any, Any]]"]["name"] = "Iterable[Triplet[Any, Any, Any]]"
    new_tdd["Iterable[Triplet[Any, Any, Any]]"]["parents"] = ["object"]

    # Quadruplet
    new_tdd["Iterator[Quadruplet[Any, Any, Any, Any]]"] = deepcopy(new_tdd["Iterator[Any]"])
    new_tdd["Iterator[Quadruplet[Any, Any, Any, Any]]"][
        "name"
    ] = "Iterator[Quadruplet[Any, Any, Any, Any]]"
    new_tdd["Iterator[Quadruplet[Any, Any, Any, Any]]"]["parents"] = [
        "Iterable[Quadruplet[Any, Any, Any, Any]]"
    ]
    new_tdd["Iterable[Quadruplet[Any, Any, Any, Any]]"] = deepcopy(new_tdd["Iterable[Any]"])
    new_tdd["Iterable[Quadruplet[Any, Any, Any, Any]]"][
        "name"
    ] = "Iterable[Quadruplet[Any, Any, Any, Any]]"
    new_tdd["Iterable[Quadruplet[Any, Any, Any, Any]]"]["parents"] = ["object"]

    # Quintuplet
    new_tdd["Iterator[Quintuplet[Any, Any, Any, Any, Any]]"] = deepcopy(new_tdd["Iterator[Any]"])
    new_tdd["Iterator[Quintuplet[Any, Any, Any, Any, Any]]"][
        "name"
    ] = "Iterator[Quintuplet[Any, Any, Any, Any, Any]]"
    new_tdd["Iterator[Quintuplet[Any, Any, Any, Any, Any]]"]["parents"] = [
        "Iterable[Quintuplet[Any, Any, Any, Any, Any]]"
    ]
    new_tdd["Iterable[Quintuplet[Any, Any, Any, Any, Any]]"] = deepcopy(new_tdd["Iterable[Any]"])
    new_tdd["Iterable[Quintuplet[Any, Any, Any, Any, Any]]"][
        "name"
    ] = "Iterable[Quintuplet[Any, Any, Any, Any, Any]]"
    new_tdd["Iterable[Quintuplet[Any, Any, Any, Any, Any]]"]["parents"] = ["object"]

    # Sextuplet
    new_tdd["Iterator[Sextuplet[Any, Any, Any, Any, Any, Any]]"] = deepcopy(
        new_tdd["Iterator[Any]"]
    )
    new_tdd["Iterator[Sextuplet[Any, Any, Any, Any, Any, Any]]"][
        "name"
    ] = "Iterator[Sextuplet[Any, Any, Any, Any, Any, Any]]"
    new_tdd["Iterator[Sextuplet[Any, Any, Any, Any, Any, Any]]"]["parents"] = [
        "Iterable[Sextuplet[Any, Any, Any, Any, Any, Any]]"
    ]
    new_tdd["Iterable[Sextuplet[Any, Any, Any, Any, Any, Any]]"] = deepcopy(
        new_tdd["Iterable[Any]"]
    )
    new_tdd["Iterable[Sextuplet[Any, Any, Any, Any, Any, Any]]"][
        "name"
    ] = "Iterable[Sextuplet[Any, Any, Any, Any, Any, Any]]"
    new_tdd["Iterable[Sextuplet[Any, Any, Any, Any, Any, Any]]"]["parents"] = ["object"]

    # Septuplet
    new_tdd["Iterator[Septuplet[Any, Any, Any, Any, Any, Any, Any]]"] = deepcopy(
        new_tdd["Iterator[Any]"]
    )
    new_tdd["Iterator[Septuplet[Any, Any, Any, Any, Any, Any, Any]]"][
        "name"
    ] = "Iterator[Septuplet[Any, Any, Any, Any, Any, Any, Any]]"
    new_tdd["Iterator[Septuplet[Any, Any, Any, Any, Any, Any, Any]]"]["parents"] = [
        "Iterable[Septuplet[Any, Any, Any, Any, Any, Any, Any]]"
    ]
    new_tdd["Iterable[Septuplet[Any, Any, Any, Any, Any, Any, Any]]"] = deepcopy(
        new_tdd["Iterable[Any]"]
    )
    new_tdd["Iterable[Septuplet[Any, Any, Any, Any, Any, Any, Any]]"][
        "name"
    ] = "Iterable[Septuplet[Any, Any, Any, Any, Any, Any, Any]]"
    new_tdd["Iterable[Septuplet[Any, Any, Any, Any, Any, Any, Any]]"]["parents"] = ["object"]

    # Pass 7: Strip remaining templated types. These may not have been expanded in the previous
    # passes
    # because they would generate to many variants (high tt) and only the "Any" tt==0 types are
    # needed.
    for name in list(new_tdd.keys()):
        if "-" in name:
            del new_tdd[name]

    # Pass 8: Establish parent child relationships for new type definitions.
    for new_name, new_td in new_tdd.items():
        for parent in new_td["parents"]:
            new_tdd[parent]["children"].add(new_name)
    new_tdd["Any"]["children"] = set(new_tdd.keys())  # All types are children of Any
    new_tdd["Any"]["children"].remove("Any")  # Remove self-reference

    # Pass 9: Set depths. The depth is the number of edges from the root type (object) to the type.
    stack = list(new_tdd["object"]["children"])
    while stack:
        current = stack.pop()
        # Object is a child of Any and is the root type, so it has a depth of 0.
        if current != "object":
            new_tdd[current]["depth"] = (
                max((new_tdd[p]["depth"] for p in new_tdd[current]["parents"])) + 1
            )
            stack.extend(new_tdd[current]["children"])

    # Pass 10: JSON-ize the fields and add a UID to each type definition.
    for definition in sorted(new_tdd.values(), key=lambda d: d["name"]):
        definition["uid"] = (
            tt_counters[definition["tt"]]
            if definition["name"] not in existing_types_def
            else existing_types_def[definition["name"]]["uid"]
        )

    # Pass 11: Convert the parents and children sets to sorted lists.
    for definition in new_tdd.values():
        # Convert the parents and children sets to sorted lists.
        definition["parents"] = sorted([new_tdd[p]["uid"] for p in definition["parents"]])
        definition["children"] = sorted([new_tdd[c]["uid"] for c in definition["children"]])

    # Pass 12: Assertions
    uids: set[int] = set()
    for definition in new_tdd.values():
        # Ensure that the UID is unique.
        assert (
            definition["uid"] not in uids
        ), f"Duplicate UID found: {definition['uid']} for {definition['name']}"
        uids.add(definition["uid"])

        # All EGP types and methods must come from the physics.pgc_api module
        # This maintains the abstraction from the structure of egp* modules
        for imp in definition.get("imports", []):
            if imp["aip"] and imp["aip"][0].startswith("egp"):
                assert imp["aip"][0] == "egppy", f"Invalid EGP import: {imp['aip']}"
                assert imp["aip"][1] == "physics", f"Invalid EGP physical import: {imp['aip']}"
                assert imp["aip"][2] == "pgc_api", f"Invalid EGP physical import: {imp['aip']}"

        # Make sure previous definitions are not violated.
        if definition["name"] in existing_types_def:
            assert definition["uid"] == existing_types_def[definition["name"]]["uid"], (
                f"UID mismatch for {definition['name']}: {definition['uid']}"
                f" != {existing_types_def[definition['name']]['uid']}"
            )

    # Pass 13: Write the new type definition dictionary to a JSON file (optional).
    if write:
        dump_signed_json(new_tdd, TYPES_DEF_FILE)


if __name__ == "__main__":
    # Generate the types_def.json file.
    import argparse

    parser = argparse.ArgumentParser(description="Generate types_def.json from types.json")
    parser.add_argument(
        "--write", "-w", action="store_true", help="If set, write the types to a JSON file."
    )
    args = parser.parse_args()
    generate_types_def(write=args.write)
