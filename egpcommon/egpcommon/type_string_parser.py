"""Standard Python type hint string parser into a tree structure."""

from __future__ import annotations

from ast import AST, Attribute, BinOp, BitOr, Constant, Name, Subscript, Tuple, parse


class TypeNode:
    """
    Represents a single node in a type hint hierarchy (e.g., 'dict' or 'int').
    It holds the type name conceptually, without requiring the actual Python class.
    """

    def __init__(self, name: str, args: list[TypeNode] | None = None):
        self.name = name
        self.args = args or []

    def get_child(self, index: int) -> TypeNode:
        """Retrieve a specific subtype from the hierarchy."""
        try:
            return self.args[index]
        except IndexError as e:
            raise IndexError(f"Type '{self.name}' has no child at index {index}.") from e

    def __str__(self) -> str:
        """
        Reconstructs the type hint string from this node downwards.
        Standardizes formatting (removes extra spaces).
        """
        if not self.args:
            return self.name

        args_str = ", ".join(str(arg) for arg in self.args)
        return f"{self.name}[{args_str}]"

    def __repr__(self):
        return f"<TypeNode: {self.__str__()}>"


class TypeStringParser:
    """
    Parses type hint strings into TypeNodes.
    Validates syntax and strictly forbids Union types.
    """

    @staticmethod
    def parse(type_str: str) -> TypeNode:
        """Parse a type hint string into a TypeNode hierarchy."""
        if not isinstance(type_str, str):
            raise ValueError(f"Input must be a string, got {type(type_str).__name__}")

        # 1. Parse string into an Abstract Syntax Tree (AST)
        try:
            # mode='eval' ensures we only parse expressions, not statements
            tree = parse(type_str.strip(), mode="eval")
        except SyntaxError as e:
            raise ValueError(f"Invalid Python type syntax: {e}") from e

        # 2. Convert AST to TypeNode hierarchy
        return TypeStringParser._visit(tree.body)

    @staticmethod
    def _visit(node: AST) -> TypeNode:
        """Recursive AST walker."""

        # --- Case 1: Simple Names (e.g., 'int', 'MyClass') ---
        if isinstance(node, Name):
            if node.id == "Union":
                raise ValueError("Union types are not allowed.")
            return TypeNode(node.id)

        # --- Case 2: Subscripted Generics (e.g., 'list[int]') ---
        elif isinstance(node, Subscript):
            origin = TypeStringParser._visit(node.value)

            # Catch 'Union[...]'
            if origin.name == "Union" or origin.name.endswith(".Union"):
                raise ValueError("Union types are not allowed.")

            # Extract arguments (slice)
            args = []
            # Python < 3.9 uses ast.Index/ast.ExtSlice; 3.9+ uses ast.Tuple or node directly
            if isinstance(node.slice, Tuple):
                # multiple args: dict[str, int]
                args = [TypeStringParser._visit(elt) for elt in node.slice.elts]
            else:
                # single arg: list[int]
                args = [TypeStringParser._visit(node.slice)]

            # Sanity for ellipsis
            ellipsis_present = False
            for arg in args:
                if arg.name == "...":
                    if ellipsis_present:
                        raise ValueError("Multiple ellipses '...' are not allowed in type hints.")
                    ellipsis_present = True
            if ellipsis_present and origin.name != "tuple":
                raise ValueError("Ellipsis '...' is only allowed in 'tuple' type hints.")

            return TypeNode(origin.name, args)

        # --- Case 3: Attributes (e.g., 'collections.abc.Iterable') ---
        elif isinstance(node, Attribute):
            full_name = TypeStringParser._flatten_attr(node)
            if full_name.endswith("Union"):
                raise ValueError("Union types are not allowed.")
            return TypeNode(full_name)

        # --- Case 4: Constants (e.g., 'None') ---
        elif isinstance(node, Constant):
            if node.value is None:
                return TypeNode("None")
            if node.value is Ellipsis:
                return TypeNode("...")
            raise ValueError(f"Literals like '{node.value}' are not valid types.")

        # --- Case 5: Binary Operators (The '|' Union operator) ---
        elif isinstance(node, BinOp):
            if isinstance(node.op, BitOr):
                raise ValueError("The Union operator '|' is not supported.")
            raise ValueError("Mathematical operators are not valid in type hints.")

        # --- Catch-all for unsupported syntax ---
        else:
            raise ValueError(f"Unsupported syntax: {type(node).__name__}")

    @staticmethod
    def _flatten_attr(node: Attribute) -> str:
        """Helper to flatten 'module.sub.Class' into a single string."""
        parts = []
        curr = node
        while isinstance(curr, Attribute):
            parts.append(curr.attr)
            curr = curr.value

        if isinstance(curr, Name):
            parts.append(curr.id)

        return ".".join(reversed(parts))


# ---------------------------------------------------------
# Usage Examples
# ---------------------------------------------------------

if __name__ == "__main__":
    print("--- 1. Basic Parsing and Reconstruction ---")
    RAW_INPUT = "  list[  dict[ str,  MyCustomClass ] ]  "
    print(f"Input: '{RAW_INPUT}'")

    # Parse
    root = TypeStringParser.parse(RAW_INPUT)
    print(f"Root Type: {root.name}")  # list

    # Reconstruct (Note: whitespace is normalized)
    print(f"Reconstructed: '{root}'")

    print("\n--- 2. Extraction and Inspection ---")
    # Hierarchy: list -> dict -> (str, MyCustomClass)

    # Get the dictionary inside the list
    inner_dict = root.get_child(0)
    print(f"Extracted Subtype: '{inner_dict}'")  # dict[str, MyCustomClass]

    # Get the value type of the dictionary (index 1)
    value_type = inner_dict.get_child(1)
    print(f"Deepest Subtype:   '{value_type}'")  # MyCustomClass

    print("\n--- 3. Validation (Rejection) Tests ---")
    invalid_inputs = [
        "int | str",  # Pipe syntax
        "Union[int, str]",  # Union keyword
        "typing.Union[int, str]",  # Dotted Union
        "list[ 100 ]",  # Integer literal
        "dict[str, int] + list",  # Math operation
    ]

    for bad_input in invalid_inputs:
        try:
            TypeStringParser.parse(bad_input)
            print(f"FAILED to reject: {bad_input}")
        except ValueError as e:
            print(f"Successfully rejected '{bad_input}': {e}")
