import unittest

from egppy.physics.psql_types import PsqlInt, PsqlIntegral, PsqlNumber, PsqlType


class TestPsqlIntSimple(unittest.TestCase):
    """A simple unit test for the PsqlInt type."""

    def test_psql_int_inheritance_and_instantiation(self):
        """
        Tests that PsqlInt has the correct base classes and can be instantiated.
        """
        # Test class hierarchy
        self.assertTrue(issubclass(PsqlInt, PsqlIntegral))
        self.assertTrue(issubclass(PsqlInt, PsqlNumber))
        self.assertTrue(issubclass(PsqlInt, PsqlType))

        # Test instantiation with a literal value
        try:
            psql_int_literal = PsqlInt(123, is_literal=True)
            self.assertEqual(psql_int_literal.value, 123)
        except Exception as e:
            self.fail(f"PsqlInt instantiation with a literal failed with {e}")

        # Test instantiation as a column
        try:
            psql_int_column = PsqlInt("my_column", is_column=True)
            self.assertEqual(psql_int_column.value, "my_column")
        except Exception as e:
            self.fail(f"PsqlInt instantiation as a column failed with {e}")


if __name__ == "__main__":
    unittest.main()
