"""Unit tests for the TypeContext class in egpseed.type_context module."""

import unittest
from doctest import testmod
from egpseed import type_context
from egpseed.type_context import TypeContext, ParsedType


# pylint: disable=missing-function-docstring,pointless-statement,missing-class-docstring,protected-access
class TestTypeContextInit(unittest.TestCase):

    def test_docstrings(self):
        """Ensure that the docstrings examples are correct."""
        testmod(type_context, raise_on_error=True)

    def test_valid_simple_types(self):
        tc = TypeContext(["int", "str", "bool"])
        self.assertEqual(tc.get_current_type_strings(), ["int", "str", "bool"])

    def test_valid_generic_types(self):
        tc = TypeContext(["list[int]", "dict[str, float]"])
        self.assertEqual(tc.get_current_type_strings(), ["list[int]", "dict[str, float]"])

    def test_valid_references(self):
        tc = TypeContext(["int", "list[0]", "tuple[0, 1]"])
        self.assertEqual(
            tc.get_current_type_strings(), ["int", "list[int]", "tuple[int, list[int]]"]
        )

    def test_valid_nested_references(self):
        tc = TypeContext(["int", "float", "list[0]", "dict[1, 2]", "Wrapper[3, 2_0]"])
        self.assertEqual(
            tc.get_current_type_strings(),
            [
                "int",
                "float",
                "list[int]",
                "dict[float, list[int]]",
                "Wrapper[dict[float, list[int]], int]",
            ],
        )

    def test_valid_tuple_ellipsis(self):
        tc = TypeContext(["tuple[int, ...]", "str"])
        self.assertEqual(tc.get_current_type_strings(), ["tuple[int, ...]", "str"])
        tc2 = TypeContext(["MyType", "Wrapper[tuple[0, ...]]"])
        self.assertEqual(tc2.get_current_type_strings(), ["MyType", "Wrapper[tuple[MyType, ...]]"])

    def test_error_both_type_strings_and_pre_resolved(self):
        with self.assertRaisesRegex(
            ValueError, "Cannot provide both type_strings and _pre_resolved_type."
        ):
            TypeContext(type_strings=["int"], _pre_resolved_type=ParsedType("float", "float"))

    def test_error_neither_type_strings_nor_pre_resolved_is_handled_by_argparse_or_usage(self):
        # This specific error is for when the constructor is called with all defaults (None),
        # which TypeContext's constructor definition with type hints prevents directly
        # if called programmatically without bypassing normal argument passing.
        # The explicit check for `type_strings is None` (when _pre_resolved_type is also None)
        # handles this.
        with self.assertRaisesRegex(ValueError, "Must provide type_strings or _pre_resolved_type."):
            TypeContext()

    def test_error_type_strings_not_list(self):
        with self.assertRaisesRegex(
            TypeError, "TypeContext type_strings must be a list of strings."
        ):
            TypeContext("int")  # type: ignore

    def test_error_type_strings_list_with_non_string(self):
        with self.assertRaisesRegex(
            TypeError, "TypeContext type_strings must be a list of strings."
        ):
            TypeContext(["int", 123])  # type: ignore

    def test_error_type_strings_empty_list(self):
        with self.assertRaisesRegex(
            ValueError, "TypeContext type_strings must not be empty if provided."
        ):
            TypeContext([])

    def test_error_empty_type_string_in_list(self):
        # _extract_base_and_args raises "Type string cannot be empty."
        with self.assertRaisesRegex(ValueError, "Type string cannot be empty."):
            TypeContext(["int", ""])

    def test_error_mismatched_brackets_close(self):
        with self.assertRaises(ValueError):
            TypeContext(
                ["list int]"]
            )  # Will likely fail earlier at _extract_base_and_args if name is invalid
        with self.assertRaises(ValueError):
            TypeContext(["list[str]]"])

    def test_error_content_after_closing_bracket(self):
        with self.assertRaises(ValueError):
            TypeContext(["list[int] foo"])

    def test_error_nameless_bracketed_args(self):
        with self.assertRaisesRegex(
            ValueError,
            "Invalid type string format: '\\[int\\]'. "
            "Bracketed argument lists must be associated with a type name",
        ):
            TypeContext(["[int]"])

    def test_error_empty_arg_list_direct_constructor(self):
        # Error from _parse_top_level_type_by_index
        with self.assertRaisesRegex(
            ValueError,
            "Top-level type 'MyType' in 'MyType\\[\\]' has an empty argument list '\\[\\]'.",
        ):
            TypeContext(["MyType[]"])

    def test_error_empty_arg_list_nested_constructor(self):
        # Error from _parse_literal_type_string
        with self.assertRaisesRegex(
            ValueError, "Type 'MyType' in 'MyType\\[\\]' has an empty argument list '\\[\\]'."
        ):
            TypeContext(["list[MyType[]]"])

    def test_error_circular_dependency_direct(self):
        with self.assertRaisesRegex(ValueError, "Circular dependency detected: A\\[0\\]"):
            TypeContext(["A[0]"])

    def test_error_circular_dependency_indirect(self):
        with self.assertRaisesRegex(
            ValueError, "Circular dependency detected: A\\[1\\] -> B\\[0\\]"
        ):
            TypeContext(["A[1]", "B[0]"])

    def test_error_invalid_tuple_ellipsis_alone(self):
        with self.assertRaisesRegex(
            ValueError,
            "For 'tuple' type, '...' can only be used as the second element .* "
            "Invalid format for arguments: '...' in 'tuple\\[...\\]'",
        ):
            TypeContext(["tuple[...]"])

    def test_error_invalid_tuple_ellipsis_too_many_args(self):
        with self.assertRaisesRegex(
            ValueError,
            "For 'tuple' type, '...' can only be used as the second element .* "
            "Invalid format for arguments: 'A, B, ...' in 'tuple\\[A, B, ...\\]'",
        ):
            TypeContext(["tuple[A, B, ...]"])

    def test_error_invalid_tuple_ellipsis_first_arg(self):
        with self.assertRaisesRegex(
            ValueError,
            "For 'tuple' type, '...' can only be used as the second element .* "
            "Invalid format for arguments: '..., A' in 'tuple\\[..., A\\]'",
        ):
            TypeContext(["tuple[..., A]"])

    def test_error_invalid_ellipsis_for_list(self):
        with self.assertRaisesRegex(
            ValueError,
            "'...' ellipsis is not supported for type 'list'.*:"
            " Found in arguments: '...' in 'list\\[...\\]'",
        ):
            TypeContext(["list[...]"])

    def test_error_reference_out_of_bounds_init(self):
        with self.assertRaises(IndexError):
            TypeContext(["A[1]"])  # Only A at index 0 exists.

    def test_error_reference_to_non_generic_arg_init(self):
        with self.assertRaises(IndexError):
            TypeContext(["int", "B[0_0]"])

    def test_error_reference_to_ellipsis_arg_init(self):
        with self.assertRaises(IndexError):
            TypeContext(["tuple[int, ...]", "MyWrapper[0_1]"])


class TestTypeContextGetItem(unittest.TestCase):
    def setUp(self):
        self.tc_simple = TypeContext(["int", "str"])
        self.tc_generic = TypeContext(["list[float]", "tuple[bool, str, int]"])
        self.tc_refs = TypeContext(["MyData", "dict[str, int]", "Wrapper[0, 1_0]"])
        self.tc_tuple_ellipsis = TypeContext(["tuple[str, ...]", "AnotherType"])
        self.tc_complex_nesting = TypeContext(["A[B, C[E, F[G,H]]]", "D"])

    def test_getitem_simple_type(self):
        self.assertEqual(self.tc_simple["0"].get_current_type_strings(), ["int"])
        self.assertEqual(self.tc_simple["1"].get_current_type_strings(), ["str"])

    def test_getitem_generic_type(self):
        self.assertEqual(self.tc_generic["0"].get_current_type_strings(), ["list[float]"])

    def test_getitem_generic_arg(self):
        self.assertEqual(self.tc_generic["0_0"].get_current_type_strings(), ["float"])
        self.assertEqual(self.tc_generic["1_1"].get_current_type_strings(), ["str"])

    def test_getitem_nested_generic_arg(self):
        focused_c = self.tc_complex_nesting["0_1"]  # C[E, F[G,H]]
        self.assertEqual(focused_c.get_current_type_strings(), ["C[E, F[G, H]]"])
        focused_f = focused_c["0_1"]  # F[G,H]
        self.assertEqual(focused_f.get_current_type_strings(), ["F[G, H]"])
        focused_h = focused_f["0_1"]  # H
        self.assertEqual(focused_h.get_current_type_strings(), ["H"])

    def test_getitem_from_focused_context(self):
        list_type_ctx = self.tc_generic["0"]  # Focused on list[float]
        self.assertEqual(list_type_ctx["0_0"].get_current_type_strings(), ["float"])

    def test_getitem_with_resolved_references(self):
        # tc_refs = TypeContext(["MyData", "dict[str, int]", "Wrapper[0, 1_0]"])
        # Wrapper[MyData, str]
        wrapper_ctx = self.tc_refs["2"]
        self.assertEqual(wrapper_ctx.get_current_type_strings(), ["Wrapper[MyData, str]"])
        # First arg of Wrapper is MyData (resolved from "0")
        self.assertEqual(wrapper_ctx["0_0"].get_current_type_strings(), ["MyData"])
        # Second arg of Wrapper is str (resolved from "1_0")
        self.assertEqual(wrapper_ctx["0_1"].get_current_type_strings(), ["str"])

    def test_getitem_valid_tuple_arg_before_ellipsis(self):
        # tc_tuple_ellipsis = TypeContext(["tuple[str, ...]", "AnotherType"])
        self.assertEqual(self.tc_tuple_ellipsis["0_0"].get_current_type_strings(), ["str"])

    def test_error_getitem_non_string_ref(self):
        with self.assertRaisesRegex(TypeError, "Relative position reference must be a string."):
            self.tc_simple[0]  # type: ignore

    def test_error_getitem_malformed_ref_alpha(self):
        with self.assertRaisesRegex(
            ValueError, "Malformed reference: 'a_b'. Indices must be integers."
        ):
            self.tc_simple["a_b"]

    def test_error_getitem_malformed_ref_trailing_underscore(self):
        with self.assertRaisesRegex(
            ValueError, "Malformed reference: '0_'. Indices must be integers."
        ):
            self.tc_simple["0_"]

    def test_error_getitem_empty_ref_string(self):
        with self.assertRaisesRegex(ValueError, "Empty reference string."):
            self.tc_simple[""]
        with self.assertRaisesRegex(ValueError, "Empty reference string."):
            self.tc_simple["   "]

    def test_error_getitem_index_out_of_bounds_main(self):
        with self.assertRaisesRegex(IndexError, "Index 2 out of bounds for main type list"):
            self.tc_simple["2"]

    def test_error_getitem_index_out_of_bounds_arg(self):
        with self.assertRaisesRegex(
            IndexError, "Subtype index 1 out of bounds for 'list\\[float\\]'"
        ):
            self.tc_generic["0_1"]  # list[float] has only one arg at index 0

    def test_error_getitem_arg_from_non_generic(self):
        with self.assertRaisesRegex(IndexError, "Type 'int'.*has no type arguments. Ref: '0_0'"):
            self.tc_simple["0_0"]  # "int" is not generic

    def test_error_getitem_arg_from_ellipsis_traversal(self):
        # tc_tuple_ellipsis is ["tuple[str, ...]", "AnotherType"]
        # "0_1" points to "..."
        # If we try "0_1_0", it means accessing arg 0 of "..."
        with self.assertRaises(IndexError):
            self.tc_tuple_ellipsis["0_1_0"]

    def test_error_getitem_focus_on_ellipsis(self):
        # tc_tuple_ellipsis is ["tuple[str, ...]", "AnotherType"]
        # "0_1" should resolve to "..."
        with self.assertRaisesRegex(
            ValueError,
            "Cannot create a focused TypeContext on '...' "
            "ellipsis. The type at '0_1' resolves to '...'.",
        ):
            self.tc_tuple_ellipsis["0_1"]


class TestTypeContextGetCurrentTypeStrings(unittest.TestCase):
    def test_get_strings_simple_init(self):
        tc = TypeContext(["int", "str"])
        self.assertEqual(tc.get_current_type_strings(), ["int", "str"])

    def test_get_strings_after_getitem(self):
        tc = TypeContext(["list[int]", "str"])
        focused_tc = tc["0"]
        self.assertEqual(focused_tc.get_current_type_strings(), ["list[int]"])
        focused_arg_tc = tc["0_0"]
        self.assertEqual(focused_arg_tc.get_current_type_strings(), ["int"])

    def test_get_strings_with_references(self):
        tc = TypeContext(["dict[str, int]", "Wrapper[0, 0_0, 0_1]"])
        self.assertEqual(
            tc.get_current_type_strings(), ["dict[str, int]", "Wrapper[dict[str, int], str, int]"]
        )

    def test_get_strings_with_tuple_ellipsis(self):
        tc = TypeContext(["tuple[bool, ...]", "list[0]"])
        self.assertEqual(
            tc.get_current_type_strings(), ["tuple[bool, ...]", "list[tuple[bool, ...]]"]
        )

    def test_get_strings_complex_nested(self):
        tc = TypeContext(["A[B[C,D], E[F[G]]]", "H[0, 0_1, 0_1_0, 0_1_0_0]"])
        expected = ["A[B[C, D], E[F[G]]]", "H[A[B[C, D], E[F[G]]], E[F[G]], F[G], G]"]
        self.assertEqual(tc.get_current_type_strings(), expected)


class TestTypeContextReprStr(unittest.TestCase):
    def test_repr_output(self):
        tc = TypeContext(["int", "list[0]"])
        self.assertEqual(repr(tc), "TypeContext(['int', 'list[int]'])")
        focused_tc = tc["1"]  # list[int]
        self.assertEqual(repr(focused_tc), "TypeContext(['list[int]'])")

    def test_str_output(self):
        tc = TypeContext(["str"])
        self.assertEqual(str(tc), "TypeContext focused on: ['str']")


class TestInternalStaticMethods(unittest.TestCase):
    # Testing internal methods can be useful but is not always standard practice
    # Here are a few examples for key internal static methods

    def test_is_reference_string(self):
        self.assertTrue(TypeContext._is_reference_string("0"))
        self.assertTrue(TypeContext._is_reference_string("1_0"))
        self.assertTrue(TypeContext._is_reference_string("12_345_67"))
        self.assertFalse(TypeContext._is_reference_string("abc"))
        self.assertFalse(TypeContext._is_reference_string("0_a"))
        self.assertFalse(TypeContext._is_reference_string("0_"))
        self.assertFalse(TypeContext._is_reference_string(""))

    def test_extract_base_and_args(self):
        self.assertEqual(TypeContext._extract_base_and_args("int"), ("int", None))
        self.assertEqual(TypeContext._extract_base_and_args("list[int]"), ("list", "int"))
        self.assertEqual(TypeContext._extract_base_and_args("dict[str, Any]"), ("dict", "str, Any"))
        self.assertEqual(
            TypeContext._extract_base_and_args("  Wrapper [ list [ int ] , str ]  "),
            ("Wrapper", "list [ int ] , str"),
        )

        with self.assertRaisesRegex(ValueError, "Type string cannot be empty"):
            TypeContext._extract_base_and_args("   ")
        with self.assertRaisesRegex(ValueError, "Mismatched brackets"):
            TypeContext._extract_base_and_args("list[int")
        with self.assertRaisesRegex(ValueError, "Unexpected content after closing bracket"):
            TypeContext._extract_base_and_args("list[int] oops")
        with self.assertRaisesRegex(ValueError, "Invalid type string format: '\\[int\\]'"):
            TypeContext._extract_base_and_args("[int]")

    def test_split_args_string(self):
        self.assertEqual(TypeContext._split_args_string("int, str"), ["int", "str"])
        self.assertEqual(
            TypeContext._split_args_string("list[int], MyType"), ["list[int]", "MyType"]
        )
        self.assertEqual(TypeContext._split_args_string("A, B, C"), ["A", "B", "C"])
        self.assertEqual(TypeContext._split_args_string(""), [])
        self.assertEqual(TypeContext._split_args_string("  "), [])

        # Ellipsis tests for _split_args_string
        self.assertEqual(
            TypeContext._split_args_string("T, ...", for_type_name="tuple"), ["T", "..."]
        )

        with self.assertRaisesRegex(
            ValueError,
            "For 'tuple' type, '...' can only be used as the second element.*tuple\\[..., T\\]",
        ):
            TypeContext._split_args_string("..., T", for_type_name="tuple")
        with self.assertRaisesRegex(
            ValueError,
            "For 'tuple' type, '...' can only be used as the second element.*tuple\\[T, U, ...\\]",
        ):
            TypeContext._split_args_string("T, U, ...", for_type_name="tuple")
        with self.assertRaisesRegex(
            ValueError,
            "For 'tuple' type, '...' can only be used as the second element.*tuple\\[...\\]",
        ):
            TypeContext._split_args_string("...", for_type_name="tuple")

        with self.assertRaisesRegex(ValueError, "'...' ellipsis is not supported for type 'list'"):
            TypeContext._split_args_string("T, ...", for_type_name="list")
        with self.assertRaisesRegex(ValueError, "'...' ellipsis is not supported for type 'dict'"):
            TypeContext._split_args_string("...", for_type_name="dict")


if __name__ == "__main__":
    unittest.main(argv=["first-arg-is-ignored"], exit=False)
