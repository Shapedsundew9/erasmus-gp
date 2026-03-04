from typing import Any

code_to_insert = """
    def is_compatible(self, src: str | int | TypesDef, dst: str | int | TypesDef) -> bool:
        \"\"\"Check if a source type is compatible with a destination type.

        This method checks for both direct inheritance and generic covariance.
        A source type is compatible with a destination type if:
        1. The destination is an ancestor of the source (standard inheritance).
        2. Both are templated types, their base types are compatible, and their
           corresponding subtypes are compatible (covariance).

        Args:
            src: The source type definition.
            dst: The destination type definition.

        Returns:
            True if src can be passed to an endpoint expecting dst, False otherwise.
        \"\"\"
        if TypesDefStore._db_store is None:
            self._initialize_db_store()

        src_td = self[src] if not isinstance(src, TypesDef) else src
        dst_td = self[dst] if not isinstance(dst, TypesDef) else dst

        # 1. Direct Ancestry Check (Standard Inheritance)
        if dst_td in self.ancestors(src_td):
            return True

        # 2. Covariance Check for Generic Templates
        # Both must have templates defined to be generic
        if not src_td.template or not dst_td.template:
            return False

        # If they are string templates (base templates themselves), they don't have subtypes
        if isinstance(src_td.template, str) or isinstance(dst_td.template, str):
            return False

        # Ensure they are parameterized templates with subtypes
        if not src_td.subtypes or not dst_td.subtypes:
            return False

        # Ensure the number of template arguments match
        if len(src_td.template) != len(dst_td.template):
            return False

        # Ensure the base types are compatible
        # The base type is the first template arg, which is the class itself
        src_base = self[src_td.template[0]]
        dst_base = self[dst_td.template[0]]
        
        # Base type must be compatible
        if dst_base not in self.ancestors(src_base):
            return False

        # Ensure all corresponding subtypes are compatible
        for src_sub_uid, dst_sub_uid in zip(src_td.subtypes, dst_td.subtypes):
            if not self.is_compatible(src_sub_uid, dst_sub_uid):
                return False

        return True
"""

with open("egppy/egppy/genetic_code/types_def_store.py", "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "def ancestors(self" in line:
        insert_idx = i
        break

# Clear out any previous mistaken insertion
new_lines = []
skip = False
for line in lines:
    if "def is_compatible" in line:
        skip = True
    if skip and "return True" in line and "is_compatible" not in line:
        skip = False
        continue
    if not skip:
        new_lines.append(line)
        
lines = new_lines

for i, line in enumerate(lines):
    if "def ancestors(self" in line:
        insert_idx = i
        break

lines.insert(insert_idx, code_to_insert + "\n")

with open("egppy/egppy/genetic_code/types_def_store.py", "w") as f:
    f.writelines(lines)
