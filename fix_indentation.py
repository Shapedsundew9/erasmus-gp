with open("egppy/egppy/genetic_code/types_def_store.py", "r") as f:
    lines = f.readlines()

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

code_to_insert = """
    def is_compatible(self, src: str | int | 'TypesDef', dst: str | int | 'TypesDef') -> bool:
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

        src_td = self[src] if not hasattr(src, 'uid') else src
        dst_td = self[dst] if not hasattr(dst, 'uid') else dst

        # 1. Direct Ancestry Check (Standard Inheritance)
        if dst_td in self.ancestors(src_td):
            return True

        # 2. Covariance Check for Generic Templates
        # Types without subtypes cannot be covariant
        if not src_td.subtypes or not dst_td.subtypes:
            return False

        # If they are string templates (base templates themselves), they don't have subtypes to check
        if isinstance(src_td.template, str) or isinstance(dst_td.template, str):
            return False

        # Ensure the number of subtypes match
        if len(src_td.subtypes) != len(dst_td.subtypes):
            return False

        # Check if they share the same base template family.
        # This is slightly tricky as we don't store the exact base class natively.
        # However, we can check if the base types of their lineage match.
        # e.g. Mapping[str, int] -> dict[str, int]. 
        # A simpler heuristic for now: check if they share a templated parent structure
        # or have compatible base typenames. 
        # The true test is to check the base templates. 
        src_base_name = src_td.name.split('[')[0]
        dst_base_name = dst_td.name.split('[')[0]
        
        # Resolve the base types to check inheritance
        try:
            src_base = self[src_base_name]
            dst_base = self[dst_base_name]
            if dst_base not in self.ancestors(src_base):
                return False
        except KeyError:
            return False

        # Ensure all corresponding subtypes are compatible (recursive)
        for src_sub_uid, dst_sub_uid in zip(src_td.subtypes, dst_td.subtypes):
            if not self.is_compatible(src_sub_uid, dst_sub_uid):
                return False

        return True
"""

for i, line in enumerate(new_lines):
    if "def ancestors(self" in line:
        insert_idx = i
        break

new_lines.insert(insert_idx, code_to_insert + "\n")

with open("egppy/egppy/genetic_code/types_def_store.py", "w") as f:
    f.writelines(new_lines)
