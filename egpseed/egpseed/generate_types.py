"""Generate types_def.json from types.json.
This script reads a JSON file containing type definitions, processes them to create a new structure
with unique identifiers, and writes the result to a new JSON file. It also handles special cases
for template types and ensures that all parent-child relationships are correctly established.
"""

from copy import deepcopy
from itertools import count
from json import dump, load
from os.path import dirname, join
from typing import Any

from bitdict import BitDictABC, bitdict_factory
from egppy.c_graph.end_point.types_def.types_def_bit_dict import TYPESDEF_CONFIG


# The Types Definition BitDict type defines the UID from the bit field values.
tdbd: type[BitDictABC] = bitdict_factory(TYPESDEF_CONFIG)

# The types.json file is a raw definition of types.
# Only non-default key:value pairs are stored in the file and
# container types (TT > 0) are all defined with their root types e.g. "dict[Hashable, Any]"
with open(join(dirname(__file__), "data", "types.json"), encoding="utf-8") as f:
    types: dict[str, dict[str, Any]] = load(f)

# The tt_counters are used to generate unique xuid values for each type in each template type (TT).
tt_counters: list[count] = [count(0) for _ in range(8)]

# Multiple passes are made of the types as some types are defined in terms of others.
#   1. The first pass creates a new type definition dictionary with unique names and UIDs.
#   2. The second pass ensures that all parent-child relationships are established correctly.


# Pass 1: Create the new type definition dictionary.
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
        "parents": definition.get("parents", []),
        "children": definition.get("children", []),
        "abstract": definition.get("abstract", False),
        "default": definition.get("default"),
        "ept": definition.get("ept", []),
    }

    tt = definition.get("tt", 0)
    new_tdd[definition["name"]]["uid"] = tdbd({"tt": tt, "xuid": next(tt_counters[tt])}).to_int()

# Pass 2: Establish parent-child relationships and ensure unique UIDs.
testset = set()
for td in new_tdd.values():
    for parent in td["parents"]:
        # This line will error if the parent is not in the new_tdd dictionary.
        new_tdd[parent]["children"].append(td["name"])
    if td["uid"] not in testset:
        testset.add(td["uid"])
    else:
        raise ValueError(f"Duplicate uid {td['uid']} for {td['name']}")

for td in new_tdd.values():
    td["parents"] = sorted(td["parents"])
    td["children"] = sorted(td["children"])
    td["ept"] = [td["uid"]]
    tt = tdbd(td["uid"])["tt"]
    assert isinstance(tt, int)
    for _ in range(tt):
        td["ept"].append(new_tdd["Any"]["uid"])

with open("/home/shapedsundew9/types_def.json", "w", encoding="utf-8") as f:
    dump(new_tdd, f, indent=4, sort_keys=True)
