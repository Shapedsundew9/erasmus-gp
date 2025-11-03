#!/usr/bin/env python3
"""Script to fix refs usages in test_c_graph_stabilize.py"""

import re

# Read the file
with open("tests/test_egppy/test_genetic_code/test_c_graph_stabilize.py", "r") as f:
    content = f.read()

# Pattern 1: iface[idx].refs[0][0] -> get src_row
# Example: a_ref_row = ad_interface[0].refs[0][0]
# Becomes: conns = ad_interface.get_connections(0); a_ref_row = conns[0].src_row
pattern1 = r"(\w+_ref_row) = (\w+)\[(\d+)\]\.refs\[0\]\[0\]"


def replace1(match):
    var_name = match.group(1)
    iface = match.group(2)
    idx = match.group(3)
    return f"conns = {iface}.get_connections({idx})\n        {var_name} = conns[0].src_row"


content = re.sub(pattern1, replace1, content)

# Pattern 2: ep.refs[0][0] in assertions
# Example: self.assertEqual(ep.refs[0][0], "I")
# Becomes: conns = iface.get_connections(ep.idx); self.assertEqual(conns[0].src_row, SrcRow.I)
# This is tricky - need context

# Pattern 3: ep.refs[0] with tuple unpacking
# Example: ref_row, ref_idx = ep.refs[0]
pattern3 = r"(\w+), (\w+) = (\w+)\.refs\[0\]"


def replace3(match):
    row_var = match.group(1)
    idx_var = match.group(2)
    ep_var = match.group(3)
    # This needs the interface context which we don't have easily
    # Return a placeholder
    return f"# FIXME: {row_var}, {idx_var} = get connection for {ep_var}"


# Pattern 4: Remove EndPoint with refs parameter like [["I", 0]]
pattern4 = r"EndPoint\(([^)]+), \[\[.*?\]\]\)"
content = re.sub(pattern4, r"EndPoint(\1)", content)

# Write back
with open("tests/test_egppy/test_genetic_code/test_c_graph_stabilize.py", "w") as f:
    f.write(content)

print("Fixed patterns 1 and 4")
