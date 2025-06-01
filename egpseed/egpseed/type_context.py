"""The TypeContext class is used to determine positionally defined types.

In a codon definition a type my be defined as the 1st input type or the 2nd type of the
first input type. This class is used to determine types defined in such contexts.

It can also be used to determine types defined in the types.json where a parent type
is defined in terms of a child type, e.g. "dict[Hashable, Any]" has a parent Collection
that has the type Pair[Hashable, Any] as its first input type.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field


@dataclass
class ParsedType:
    """
    Represents a parsed type, including its name, original string representation,
    and any type arguments it may have.
    """

    name: str
    original_string: str
    args: list[ParsedType] = field(default_factory=list)

    def reconstruct_resolved_string(self) -> str:
        """
        Reconstructs the string representation of the type, using resolved names
        for itself and its arguments.

        Returns:
            str: The reconstructed type string.
        """
        if self.name == "...":  # Handle ellipsis type
            return "..."
        if not self.args:
            return self.name
        else:
            args_str = ", ".join(arg.reconstruct_resolved_string() for arg in self.args)
            return f"{self.name}[{args_str}]"


class TypeContext:
    """
    Manages a context of related type definitions, typically initialized from a list of type
    strings. This class parses these strings into structured `ParsedType` objects,
    resolving nested types, generic arguments, and references between types within the context.

    The `TypeContext` can represent one or more top-level types. It supports a string-based
    referencing system to navigate and access specific types or their arguments. For example,
    if initialized with `["list[int]", "dict[str, 0_0]"]`, the "0_0" in the second type string
    refers to the first argument (`int`) of the first type string (`list[int]`).

    Special handling for `tuple` with ellipsis (e.g., `tuple[str, ...]`) is supported:
    - `tuple[T, ...]` is parsed, and the "..." is treated as a special marker.
    - Attempting to use "..." in other contexts (e.g., `list[...]`, `tuple[T, U, ...]`, `tuple[...]`)
      will result in a ValueError during initialization.
    - Attempting to get a `TypeContext` focused on the "..." marker itself (e.g., `tc["0_1"]`
      if `tc` is `TypeContext(["tuple[str, ...]"])`) will also result in a ValueError.

    Key functionalities include:
    - Parsing type strings like "int", "list[str]", "tuple[int, str]", "MyType[0_1]", "tuple[str, ...]".
    - Resolving references during initial parsing:
        - "0" refers to the 1st top-level type in the original list provided at initialization.
        - "0_1" refers to the 2nd type argument of the 1st top-level type from the original list.
    - Creating new `TypeContext` instances focused on specific sub-types using `__getitem__`
      (e.g., `tc["0_1"]`). The indices in `__getitem__` refer to the types currently in focus
      by that `TypeContext` instance.
    - Reconstructing resolved type strings via `get_current_type_strings()`.
    - Detecting circular dependencies during the initial parsing phase.

    The primary purpose is to provide a structured way to work with potentially complex and
    interrelated type signatures, allowing for easy inspection and navigation of parts
    of these signatures.

    Examples:
        >>> tc_simple = TypeContext(["int", "str"])
        >>> print(tc_simple.get_current_type_strings())
        ['int', 'str']
        >>> # Focus on the first type ('int')
        >>> print(repr(tc_simple["0"]))
        TypeContext(['int'])

        >>> tc_generic = TypeContext(["list[float]", "tuple[bool, str]"])
        >>> print(tc_generic.get_current_type_strings())
        ['list[float]', 'tuple[bool, str]']

        >>> # Focus on the 'list[float]' type (the 0-th type in tc_generic)
        >>> list_type_ctx = tc_generic["0"]
        >>> print(list_type_ctx.get_current_type_strings())
        ['list[float]']

        >>> # Focus on 'float', the first argument (index 0) of 'list[float]'
        >>> float_type_ctx_from_orig = tc_generic["0_0"]
        >>> print(float_type_ctx_from_orig.get_current_type_strings())
        ['float']

        >>> # Example with references during initialization:
        >>> tc_refs = TypeContext(["MyData", "dict[str, int]", "Wrapper[0, 1_0]"])
        >>> print(tc_refs.get_current_type_strings())
        ['MyData', 'dict[str, int]', 'Wrapper[MyData, str]']

        >>> # Example with tuple and ellipsis
        >>> tc_tuple_ellipsis = TypeContext(["tuple[str, ...]", "list[0]"])
        >>> print(tc_tuple_ellipsis.get_current_type_strings())
        ['tuple[str, ...]', 'list[tuple[str, ...]]']
        >>> print(repr(tc_tuple_ellipsis["0_0"]))
        TypeContext(['str'])
        >>> try:
        ...     tc_tuple_ellipsis["0_1"] # Attempt to focus on "..."
        ... except ValueError as e:
        ...     print(e)
        Cannot create a focused TypeContext on '...' ellipsis. The type at '0_1' resolves to '...'.

        >>> # Invalid uses of ellipsis
        >>> try:
        ...     TypeContext(["tuple[int, str, ...]"])
        ... except ValueError as e:
        ...     print(e) # doctest: +ELLIPSIS
        For 'tuple' type, '...' can only be used as the second element in a two-argument list (e.g., 'tuple[T, ...]'). Invalid format for arguments: 'int, str, ...' in 'tuple[int, str, ...]'.
        >>> try:
        ...     TypeContext(["list[...]"])
        ... except ValueError as e:
        ...     print(e) # doctest: +ELLIPSIS
        '...' ellipsis is not supported for type 'list'. It is only allowed in the format 'tuple[T, ...]'. Found in arguments: '...'.
        >>> try:
        ...     TypeContext(["tuple[...]"]) # Ellipsis alone is not allowed for tuple
        ... except ValueError as e:
        ...     print(e) # doctest: +ELLIPSIS
        For 'tuple' type, '...' can only be used as the second element in a two-argument list (e.g., 'tuple[T, ...]'). Invalid format for arguments: '...' in 'tuple[...]'.

        >>> # Focusing changes the context for subsequent operations
        >>> tc_complex = TypeContext(["A[B, C[E, F]]", "D"])
        >>> # Focus on C[E, F] (0-th type, 1-st argument)
        >>> focused_on_C_generic = tc_complex["0_1"]
        >>> print(focused_on_C_generic.get_current_type_strings())
        ['C[E, F]']
        >>> # Now, from this new context, focus on F (0-th type, 1-st argument)
        >>> focused_on_F = focused_on_C_generic["0_1"]
        >>> print(focused_on_F.get_current_type_strings())
        ['F']
    """

    _original_type_strings: list[str]
    _resolved_top_level_types: list[ParsedType]

    _parsing_cache: dict[int, ParsedType]
    _parsing_stack: list[int]

    def __init__(
        self, type_strings: list[str] | None = None, _pre_resolved_type: ParsedType | None = None
    ) -> None:
        if _pre_resolved_type is not None:
            if type_strings is not None:
                raise ValueError("Cannot provide both type_strings and _pre_resolved_type.")
            self._original_type_strings = [_pre_resolved_type.original_string]
            self._resolved_top_level_types = [_pre_resolved_type]
            return

        if type_strings is None:
            raise ValueError("Must provide type_strings or _pre_resolved_type.")

        if not isinstance(type_strings, list) or not all(isinstance(s, str) for s in type_strings):
            raise TypeError("TypeContext type_strings must be a list of strings.")
        if not type_strings:
            raise ValueError("TypeContext type_strings must not be empty if provided.")

        self._original_type_strings = list(type_strings)
        self._resolved_top_level_types = [None] * len(type_strings)  # type: ignore[list-item]

        self._parsing_cache = {}
        self._parsing_stack = []

        for i in range(len(self._original_type_strings)):
            self._resolved_top_level_types[i] = self._parse_top_level_type_by_index(i)

        del self._parsing_cache  # type: ignore
        del self._parsing_stack  # type: ignore

    @staticmethod
    def _is_reference_string(s: str) -> bool:
        return bool(re.fullmatch(r"\d+(_\d+)*", s.strip()))

    @staticmethod
    def _extract_base_and_args(type_str_input: str) -> tuple[str, str | None]:
        type_str = type_str_input.strip()
        if not type_str:
            raise ValueError("Type string cannot be empty.")

        first_bracket_idx = type_str.find("[")
        if first_bracket_idx == -1:
            # If there's no opening bracket, there shouldn't be a closing one either.
            if type_str.find("]") != -1:  # Check for a stray closing bracket [type_context.py]
                # This will make the specific test case pass, assuming the regex matches.
                raise ValueError(f"Mismatched brackets in type string: '{type_str_input}'")
            return type_str, None

        balance = 0
        outer_last_bracket_idx = -1
        for i, char_at_i in enumerate(type_str):
            if char_at_i == "[":
                balance += 1
            elif char_at_i == "]":
                balance -= 1
            if balance == 0 and i >= first_bracket_idx:
                outer_last_bracket_idx = i
                if i == len(type_str) - 1:
                    break
                if type_str[i + 1 :].strip():
                    raise ValueError(
                        f"Unexpected content after closing bracket in '{type_str_input}'"
                    )
                break

        if outer_last_bracket_idx == -1 or balance != 0:
            raise ValueError(f"Mismatched brackets in type string: '{type_str_input}'")

        name_part = type_str[:first_bracket_idx].strip()
        args_content = type_str[first_bracket_idx + 1 : outer_last_bracket_idx].strip()

        if not name_part:
            raise ValueError(
                f"Invalid type string format: '{type_str_input}'. "
                "Bracketed argument lists must be associated with a type name"
                " (e.g., 'list[int]', not '[int]')."
            )
        return name_part, args_content

    @staticmethod
    def _split_args_string(args_content_str: str, for_type_name: str | None = None) -> list[str]:
        """
        Splits a raw argument string into a list of individual argument strings.
        Handles nested generics correctly and validates the use of ellipsis "..."
        which is only permitted for `tuple` in the form `tuple[T, ...]`.

        E.g., "int, str" -> ["int", "str"]
               "list[int], MyType" -> ["list[int]", "MyType"]
               "SomeType, ..." (for_type_name="tuple") -> ["SomeType", "..."]

        Args:
            args_content_str: The raw string content from within the brackets of a generic type.
            for_type_name: The name of the generic type these arguments belong to.
                           Used for special handling like "..." in "tuple".

        Returns:
            A list of strings, where each string is a type argument.

        Raises:
            ValueError: If brackets within the argument string are mismatched, or if "..."
                        is used incorrectly (e.g., not with tuple, or in wrong tuple format).
        """
        collected_arg_strings = []
        # Handles cases like "Type[]" where content is empty, this is validated before _split_args_string
        if not args_content_str.strip():
            return []

        current_arg_start, balance = 0, 0
        for i, char in enumerate(args_content_str):
            if char == "[":
                balance += 1
            elif char == "]":
                balance -= 1
                if balance < 0:
                    raise ValueError(f"Mismatched brackets in arg string: '{args_content_str}'")
            elif char == "," and balance == 0:
                arg_str = args_content_str[current_arg_start:i].strip()
                if arg_str:  # Collect all non-empty, including "..."
                    collected_arg_strings.append(arg_str)
                current_arg_start = i + 1

        last_segment = args_content_str[current_arg_start:].strip()
        if last_segment:  # Collect last segment, including if it's "..."
            collected_arg_strings.append(last_segment)

        # Validation for "..."
        has_ellipsis = "..." in collected_arg_strings

        if for_type_name == "tuple":
            if has_ellipsis:
                # "..." must be the last element, and there must be exactly one element before it.
                if not (
                    len(collected_arg_strings) == 2
                    and collected_arg_strings[1] == "..."
                    and collected_arg_strings[0].strip() != "..."  # First arg shouldn't be "..."
                ):
                    full_type_repr = (
                        f"{for_type_name}[{args_content_str}]"
                        if for_type_name
                        else f"[{args_content_str}]"
                    )
                    raise ValueError(
                        f"For 'tuple' type, '...' can only be used as the second element "
                        f"in a two-argument list (e.g., 'tuple[T, ...]'). Invalid format for arguments: '{args_content_str}' "
                        f"in '{full_type_repr}'."
                    )
        elif has_ellipsis:  # Not a tuple, but contains "..."
            full_type_repr = (
                f"{for_type_name}[{args_content_str}]" if for_type_name else f"[{args_content_str}]"
            )
            raise ValueError(
                f"'...' ellipsis is not supported for type '{for_type_name}'. "
                f"It is only allowed in the format 'tuple[T, ...]'. Found in arguments: '{args_content_str}' "
                f"in '{full_type_repr}'."
            )

        return collected_arg_strings

    def _resolve_reference_to_parsed_type(self, ref_str: str) -> ParsedType:
        stripped_ref = ref_str.strip()
        indices_str = stripped_ref.split("_")
        try:
            indices = [int(i) for i in indices_str]
        except ValueError as exc:
            raise ValueError(f"Invalid reference format: {ref_str}") from exc

        base_type_idx = indices[0]
        if not (0 <= base_type_idx < len(self._original_type_strings)):
            raise IndexError(
                f"Reference '{ref_str}' base index {base_type_idx} is out of bounds"
                " for the initial list of type strings."
            )

        current_obj = self._parse_top_level_type_by_index(base_type_idx)

        for i in range(1, len(indices)):
            sub_idx = indices[i]
            if current_obj.name == "...":
                raise IndexError(
                    f"Reference '{ref_str}' attempts to access subtype from '...' ellipsis placeholder "
                    f"within '{current_obj.original_string}'."
                )
            if not current_obj.args:
                raise IndexError(
                    f"Reference '{ref_str}' accesses subtype from non-generic "
                    f"'{current_obj.original_string}'."
                )
            try:
                current_obj = current_obj.args[sub_idx]
            except IndexError as exc:
                raise IndexError(
                    f"Reference '{ref_str}' subtype index {sub_idx} out of "
                    f"bounds for '{current_obj.original_string}'."
                ) from exc

        # If the final resolved object is an ellipsis AND it was resolved via a path
        # indicating an argument (e.g., "0_1", not just "0"), raise an error.
        # This makes the test `test_error_reference_to_ellipsis_arg_init` pass.
        if current_obj.name == "..." and len(indices) > 1:
            raise IndexError(
                f"Reference '{ref_str}' resolved to an ellipsis ('...'), which is not permissible "
                f"as a directly referenced type argument through this path."
            )

        return current_obj

    def _parse_literal_type_string(self, type_str_to_parse: str) -> ParsedType:
        type_str_cleaned = type_str_to_parse.strip()
        if not type_str_cleaned:
            raise ValueError("Type string for parsing cannot be empty.")

        name, args_content_raw = TypeContext._extract_base_and_args(type_str_cleaned)
        parsed_obj = ParsedType(name=name, args=[], original_string=type_str_cleaned)

        if args_content_raw is not None:
            # This check handles "MyType[]"
            if not args_content_raw.strip():
                raise ValueError(
                    f"Type '{name}' in '{type_str_cleaned}' has an empty argument list '[]'. "
                    f"If arguments are intended, they must be specified (e.g., '{name}[Any]')."
                )
            # _split_args_string will further validate content, e.g. ellipsis usage
            arg_strings = TypeContext._split_args_string(args_content_raw, for_type_name=name)
            for (
                arg_s
            ) in arg_strings:  # arg_s is already stripped and non-empty by _split_args_string
                if arg_s == "...":  # Ellipsis is a special type, not a reference
                    parsed_obj.args.append(ParsedType(name="...", original_string="...", args=[]))
                elif TypeContext._is_reference_string(arg_s):
                    resolved_arg_pt = self._resolve_reference_to_parsed_type(arg_s)
                    parsed_obj.args.append(resolved_arg_pt)
                else:
                    parsed_obj.args.append(self._parse_literal_type_string(arg_s))
        return parsed_obj

    def _parse_top_level_type_by_index(self, index: int) -> ParsedType:
        # 1. Check for circular dependency (MOVED TO TOP and MODIFIED for message)
        if index in self._parsing_stack:
            # Construct cycle path using original type strings
            path_determining_indices = self._parsing_stack[self._parsing_stack.index(index) :] + [
                index
            ]
            cycle_path_str_list = [self._original_type_strings[i] for i in path_determining_indices]
            cycle_path = " -> ".join(cycle_path_str_list)
            raise ValueError(f"Circular dependency detected: {cycle_path}")

        # 2. Check cache (if parsing has already started/completed for this index and it's not a direct cycle)
        if index in self._parsing_cache:
            return self._parsing_cache[index]

        # 3. Proceed with parsing (Original logic from L283 onwards, slightly adapted)
        self._parsing_stack.append(index)

        type_str = self._original_type_strings[index]
        name, args_content_raw = TypeContext._extract_base_and_args(type_str)

        current_pt_shell = ParsedType(name=name, args=[], original_string=type_str)
        self._parsing_cache[index] = current_pt_shell

        if args_content_raw is not None:
            if not args_content_raw.strip():
                self._parsing_stack.pop()
                raise ValueError(
                    f"Top-level type '{name}' in '{type_str}' has an empty argument list '[]'. "
                    f"If arguments are intended, they must be specified (e.g., '{name}[Any]')."
                )
            arg_strings = TypeContext._split_args_string(args_content_raw, for_type_name=name)
            for arg_s_orig in arg_strings:
                arg_s = (
                    arg_s_orig  # Assuming arg_s_orig is already stripped from _split_args_string
                )

                if arg_s == "...":
                    current_pt_shell.args.append(
                        ParsedType(name="...", original_string="...", args=[])
                    )
                elif TypeContext._is_reference_string(arg_s):
                    resolved_arg_pt = self._resolve_reference_to_parsed_type(arg_s)
                    current_pt_shell.args.append(resolved_arg_pt)
                else:
                    # Recursively parse literal string arguments
                    current_pt_shell.args.append(self._parse_literal_type_string(arg_s))

        self._parsing_stack.pop()
        # The object in _parsing_cache[index] (current_pt_shell) is now fully populated with its arguments.
        return current_pt_shell

    def __getitem__(self, relative_pos_ref: str) -> "TypeContext":
        if not isinstance(relative_pos_ref, str):
            raise TypeError("Relative position reference must be a string.")

        stripped_ref = relative_pos_ref.strip()
        if not stripped_ref:
            raise ValueError("Empty reference string.")

        indices_str = stripped_ref.split("_")
        try:
            indices = [int(i) for i in indices_str]
        except ValueError as exc:
            raise ValueError(
                f"Malformed reference: '{relative_pos_ref}'. Indices must be integers."
            ) from exc

        # An empty string like "" split by "_" gives [''], int('') fails.
        # A string like "0_" split by "_" gives ['0', ''], int('') fails.
        # Handled by try-except for int conversion.

        base_type_idx = indices[0]
        if not 0 <= base_type_idx < len(self._resolved_top_level_types):
            raise IndexError(
                f"Index {base_type_idx} out of bounds for main type list (size {len(self._resolved_top_level_types)}). Ref: '{relative_pos_ref}'"
            )

        current_obj = self._resolved_top_level_types[base_type_idx]

        for i in range(1, len(indices)):
            arg_idx = indices[i]
            if current_obj.name == "...":  # Cannot get sub-type from ellipsis
                raise IndexError(
                    f"Type '{current_obj.original_string}' resolved to '...' "
                    f"has no type arguments. Attempted to access argument {arg_idx} via ref: '{relative_pos_ref}'."
                )
            if not current_obj.args:
                raise IndexError(
                    f"Type '{current_obj.original_string}'"
                    f" (resolved: '{current_obj.reconstruct_resolved_string()}') "
                    f"has no type arguments. Ref: '{relative_pos_ref}'."
                )
            try:
                current_obj = current_obj.args[arg_idx]
            except IndexError as exc:
                raise IndexError(
                    f"Subtype index {arg_idx} out of bounds for '{current_obj.original_string}' "
                    f"(resolved: '{current_obj.reconstruct_resolved_string()}', {len(current_obj.args)} args)."
                    f" Ref: '{relative_pos_ref}'."
                ) from exc

        # If the final selected type is "...", disallow focusing on it.
        if current_obj.name == "...":
            raise ValueError(
                f"Cannot create a focused TypeContext on '...' ellipsis. "
                f"The type at '{relative_pos_ref}' resolves to '...'."
            )

        return TypeContext(_pre_resolved_type=current_obj)

    def get_current_type_strings(self) -> list[str]:
        return [pt.reconstruct_resolved_string() for pt in self._resolved_top_level_types]

    def __repr__(self) -> str:
        return f"TypeContext({self.get_current_type_strings()!r})"

    def __str__(self) -> str:
        return f"TypeContext focused on: {self.get_current_type_strings()}"


if __name__ == "__main__":
    import doctest

    # Run embedded doctests
    results = doctest.testmod()
    print(f"\nDoctest results: {results}")

    # Original example usage
    print("\n--- Original Main Example ---")
    tc = TypeContext(["int", "list[0]", "dict[0, 1]"])
    print(f"Original: {tc.get_current_type_strings()}")
    # Expected: ['int', 'list[int]', 'dict[int, list[int]]']
    print(f"tc['1']: {tc['1'].get_current_type_strings()}")  # list[int]
    print(f"tc['1_0']: {tc['1_0'].get_current_type_strings()}")  # int
    print(f"tc['2']: {tc['2'].get_current_type_strings()}")  # dict[int, list[int]]
    print(f"tc['2_0']: {tc['2_0'].get_current_type_strings()}")  # int
    print(f"tc['2_1']: {tc['2_1'].get_current_type_strings()}")  # list[int]
    print(f"tc['2_1_0']: {tc['2_1_0'].get_current_type_strings()}")  # int

    print("\n--- Testing Empty Argument List Errors ---")
    test_cases_for_empty_args = [
        (
            "MyType[]",
            "Type 'MyType' in 'MyType[]' has an empty argument list '[]'.",
        ),
        (
            "MyType[ ]",
            "Type 'MyType' in 'MyType[ ]' has an empty argument list '[]'.",
        ),
        (
            "list[int, MyType[]]",
            "Type 'MyType' in 'MyType[]' has an empty argument list '[]'.",
        ),
        (
            "Wrapper[OK, Bad[]]",
            "Type 'Bad' in 'Bad[]' has an empty argument list '[]'.",
        ),
        (
            "TopLevel[]",
            "Top-level type 'TopLevel' in 'TopLevel[]' has an empty argument list '[]'.",
        ),
        (
            "tuple[]",
            "Top-level type 'tuple' in 'tuple[]' has an empty argument list '[]'.",
        ),
    ]

    for type_str_list, expected_msg_fragment in test_cases_for_empty_args:
        type_input = [type_str_list] if not isinstance(type_str_list, list) else type_str_list
        print(f"\nTesting with input: {type_input}")
        try:
            TypeContext(type_input)
            print(f"ERROR: Expected ValueError for {type_input}, but none was raised.")
        except ValueError as e:
            if expected_msg_fragment in str(e):
                print(f"Caught expected error: {e}")
            else:
                print(f"ERROR: Caught ValueError for {type_input}, but message mismatch.")
                print(f'  Expected fragment: "{expected_msg_fragment}"')
                print(f'  Actual error: "{e}"')
        except Exception as e:
            print(f"ERROR: Expected ValueError for {type_input}, but got {type(e).__name__}: {e}")

    print("\n--- Testing Valid Complex Cases ---")
    tc_valid = TypeContext(["A[B, C[E, F]]", "D"])
    print(f"tc_valid: {tc_valid.get_current_type_strings()}")
    # Expected: ['A[B, C[E, F]]', 'D']
    focused_on_C_generic = tc_valid["0_1"]
    print(f"focused_on_C_generic: {focused_on_C_generic.get_current_type_strings()}")
    # Expected: ['C[E, F]']
    focused_on_F = focused_on_C_generic["0_1"]
    print(f"focused_on_F: {focused_on_F.get_current_type_strings()}")
    # Expected: ['F']

    print("\n--- Testing Tuple Ellipsis Specifics ---")
    # Satisfying user requirements:
    # 1. TypeContext(["tuple[int, ...]"])["0_0"] == TypeContext(["int"])
    tc_tuple_int_ellipsis = TypeContext(["tuple[int, ...]"])
    tc_int = TypeContext(["int"])
    val1 = tc_tuple_int_ellipsis["0_0"].get_current_type_strings()
    val2 = tc_int.get_current_type_strings()
    print(f"TypeContext(['tuple[int, ...]'])['0_0'] -> {val1}")
    print(f"TypeContext(['int']) -> {val2}")
    assert val1 == val2, "Test 1 FAILED"
    print("Test 1 PASSED: TypeContext(['tuple[int, ...]'])['0_0'] == TypeContext(['int'])")

    # 2. TypeContext(["tuple[int, ...]"])["0_1"] raises a ValueError
    try:
        TypeContext(["tuple[int, ...]"])["0_1"]
        print("ERROR: Test 2 FAILED - Expected ValueError for tc['0_1'] on tuple ellipsis")
    except ValueError as e:
        print(f"Test 2 PASSED: Caught expected error for tc['0_1'] on tuple ellipsis: {e}")
        assert "Cannot create a focused TypeContext on '...' ellipsis" in str(
            e
        ), "Test 2 message check FAILED"

    # 3. TypeContext(["tuple[int, ...]"]).get_current_type_strings() == ["tuple[int, ...]"]
    val3 = TypeContext(["tuple[int, ...]"]).get_current_type_strings()
    print(f"TypeContext(['tuple[int, ...]']).get_current_type_strings() -> {val3}")
    assert val3 == ["tuple[int, ...]"], "Test 3 FAILED"
    print("Test 3 PASSED: Correct string reconstruction for tuple[int, ...]")

    # 4. TypeContext(["tuple[int, str, ...]"]) raises a ValueError
    try:
        TypeContext(["tuple[int, str, ...]"])
        print("ERROR: Test 4 FAILED - Expected ValueError for tuple[int, str, ...]")
    except ValueError as e:
        print(f"Test 4 PASSED: Caught expected error for tuple[int, str, ...]: {e}")
        assert "For 'tuple' type, '...' can only be used as the second element" in str(
            e
        ), "Test 4 message check FAILED"

    # 5. TypeContext(["list[...]"]) raises a ValueError
    try:
        TypeContext(["list[...]"])
        print("ERROR: Test 5 FAILED - Expected ValueError for list[...]")
    except ValueError as e:
        print(f"Test 5 PASSED: Caught expected error for list[...]: {e}")
        assert "'...' ellipsis is not supported for type 'list'" in str(
            e
        ), "Test 5 message check FAILED"

    # 6. TypeContext(["list[tuple[int, ...]]"])["0_0"] == TypeContext(["tuple[int, ...]"])
    tc_list_tuple_ellipsis = TypeContext(["list[tuple[int, ...]]"])
    tc_tuple_ellipsis_standalone = TypeContext(["tuple[int, ...]"])
    val6a = tc_list_tuple_ellipsis["0_0"].get_current_type_strings()
    val6b = tc_tuple_ellipsis_standalone.get_current_type_strings()
    print(f"TypeContext(['list[tuple[int, ...]]'])['0_0'] -> {val6a}")
    print(f"TypeContext(['tuple[int, ...]']) -> {val6b}")
    assert val6a == val6b, "Test 6 FAILED"
    print("Test 6 PASSED: Correct focusing on list[tuple[int, ...]]")

    print("\n--- Additional Reference Tests with Ellipsis ---")
    try:
        TypeContext(["tuple[int, ...]", "ErrorType[0_1]"])
        print("ERROR: Expected IndexError for ref '0_1' pointing to ellipsis.")
    except IndexError as e:  # Or ValueError depending on where it's caught first for refs.
        # _resolve_reference_to_parsed_type raises IndexError if sub_idx from ellipsis
        print(f"Caught expected error for ref '0_1' pointing to ellipsis: {e}")
        assert "attempts to access subtype from '...' ellipsis placeholder" in str(e)

    print("\nAll specified tests in __main__ completed.")
