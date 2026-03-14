"""Unit tests for the TypeStringParser class."""

import unittest

from egpcommon.type_string_parser import TypeNode, TypeStringParser


class TestTypeStringParser(unittest.TestCase):
    """Unit tests for the TypeStringParser class."""

    def test_simple_types(self):
        """Test parsing of simple type names."""
        node = TypeStringParser.parse("int")
        self.assertIsInstance(node, TypeNode)
        self.assertEqual(node.name, "int")
        self.assertEqual(node.args, [])
        self.assertEqual(str(node), "int")

        node = TypeStringParser.parse("MyClass")
        self.assertEqual(node.name, "MyClass")

    def test_generics(self):
        """Test parsing of generic types."""
        node = TypeStringParser.parse("list[int]")
        self.assertEqual(node.name, "list")
        self.assertEqual(len(node.args), 1)
        self.assertEqual(node.args[0].name, "int")
        self.assertEqual(str(node), "list[int]")

        node = TypeStringParser.parse("dict[str, int]")
        self.assertEqual(node.name, "dict")
        self.assertEqual(len(node.args), 2)
        self.assertEqual(node.args[0].name, "str")
        self.assertEqual(node.args[1].name, "int")
        self.assertEqual(str(node), "dict[str, int]")

    def test_nested_generics(self):
        """Test parsing of nested generic types."""
        input_str = "list[dict[str, list[int]]]"
        node = TypeStringParser.parse(input_str)
        self.assertEqual(node.name, "list")
        self.assertEqual(str(node), input_str)

        inner_dict = node.get_child(0)
        self.assertEqual(inner_dict.name, "dict")

        inner_list = inner_dict.get_child(1)
        self.assertEqual(inner_list.name, "list")
        self.assertEqual(inner_list.get_child(0).name, "int")

    def test_dotted_names(self):
        """Test parsing of dotted module paths."""
        node = TypeStringParser.parse("collections.abc.Iterable[int]")
        self.assertEqual(node.name, "collections.abc.Iterable")
        self.assertEqual(node.args[0].name, "int")
        self.assertEqual(str(node), "collections.abc.Iterable[int]")

    def test_none_type(self):
        """Test parsing of None."""
        node = TypeStringParser.parse("None")
        self.assertEqual(node.name, "None")

    def test_spacing(self):
        """Test that extra whitespace is handled correctly."""
        node = TypeStringParser.parse("  list[  dict[ str,  int ] ]  ")
        self.assertEqual(node.name, "list")
        self.assertEqual(str(node), "list[dict[str, int]]")

    def test_get_child(self):
        """Test the get_child method."""
        node = TypeStringParser.parse("dict[str, int]")
        self.assertEqual(node.get_child(0).name, "str")
        self.assertEqual(node.get_child(1).name, "int")

        with self.assertRaises(IndexError):
            node.get_child(2)

    def test_invalid_union_keyword(self):
        """Test that Union types are rejected."""
        with self.assertRaisesRegex(ValueError, "Union types are not allowed"):
            TypeStringParser.parse("Union[int, str]")

        with self.assertRaisesRegex(ValueError, "Union types are not allowed"):
            TypeStringParser.parse("typing.Union[int, str]")

    def test_invalid_union_pipe(self):
        """Test that pipe syntax for Union is rejected."""
        with self.assertRaisesRegex(ValueError, "The Union operator '\\|' is not supported"):
            TypeStringParser.parse("int | str")

    def test_invalid_literals(self):
        """Test that literals are rejected."""
        with self.assertRaisesRegex(ValueError, "Literals like '100' are not valid types"):
            TypeStringParser.parse("list[100]")

        with self.assertRaisesRegex(ValueError, "Literals like 'hello' are not valid types"):
            TypeStringParser.parse("list['hello']")

    def test_invalid_syntax(self):
        """Test that invalid Python syntax is rejected."""
        with self.assertRaisesRegex(ValueError, "Invalid Python type syntax"):
            TypeStringParser.parse("list[")

        with self.assertRaisesRegex(ValueError, "Invalid Python type syntax"):
            TypeStringParser.parse("dict[str")

    def test_invalid_input_type(self):
        """Test that non-string input is rejected."""
        with self.assertRaisesRegex(ValueError, "Input must be a string"):
            TypeStringParser.parse(123)  # type: ignore

    def test_invalid_math_ops(self):
        """Test that mathematical operators are rejected."""
        with self.assertRaisesRegex(ValueError, "Mathematical operators are not valid"):
            TypeStringParser.parse("int + str")


if __name__ == "__main__":
    unittest.main()
