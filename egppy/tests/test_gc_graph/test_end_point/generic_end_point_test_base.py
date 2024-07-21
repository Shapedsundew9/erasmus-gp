"""Unit tests for the GenericEndpoint class."""
import unittest
from egppy.gc_graph.egp_typing import ROWS
from egppy.gc_graph.end_point.end_point import GenericEndPoint


class GenericEndPointTestBase(unittest.TestCase):
    """Test cases for the GenericEndPoint class."""

    # Override this in subclasses.
    endpoint_type = GenericEndPoint

    @classmethod
    def get_test_cls(cls) -> type:
        """Get the TestCase class."""
        return cls

    @classmethod
    def running_in_test_base_class(cls) -> bool:
        """Pass the test if the Test class class is the Test Base class."""
        # Alternative is to skip:
        # raise unittest.SkipTest('Base class test not run')
        return cls.get_test_cls().__name__.endswith('TestBase')

    @classmethod
    def get_endpoint_cls(cls) -> type:
        """Get the Value class."""
        return cls.endpoint_type

    def setUp(self) -> None:
        """
        Set up the test case by initializing the row, index, and endpoint.
        """
        self.row1 = ROWS[0]
        self.row2 = ROWS[1]
        self.idx1 = 0
        self.idx2 = 1
        self.endpoint = self.get_endpoint_cls()(self.row1, self.idx1)

    def test_get_idx(self) -> None:
        """
        Test the get_idx() method of the endpoint.
        """
        if self.running_in_test_base_class():
            return
        self.assertEqual(self.endpoint.get_idx(), self.idx1)

    def test_get_row(self) -> None:
        """
        Test the get_row() method of the endpoint.
        """
        if self.running_in_test_base_class():
            return
        self.assertEqual(self.endpoint.get_row(), self.row1)

    def test_set_idx(self) -> None:
        """
        Test the set_idx() method of the endpoint.
        """
        if self.running_in_test_base_class():
            return
        new_idx = 1
        self.endpoint.set_idx(new_idx)
        self.assertEqual(self.endpoint.get_idx(), new_idx)

    def test_set_row(self) -> None:
        """
        Test the set_row() method of the endpoint.
        """
        if self.running_in_test_base_class():
            return
        self.endpoint.set_row(self.row2)
        self.assertEqual(self.endpoint.get_row(), self.row2)

    def test_repr(self) -> None:
        """
        Test the __repr__() method of the endpoint.
        """
        if self.running_in_test_base_class():
            return
        print(repr(self.endpoint))
        print(f"_row={self.row1}")
        self.assertEqual(f"_row={self.row1}" in repr(self.endpoint), True)

    def test_json_obj(self) -> None:
        """
        Test the json_obj() method of the endpoint.
        """
        if self.running_in_test_base_class():
            return
        json = self.endpoint.json_obj()
        self.assertEqual(self.row1, json["_row"])
        self.assertEqual(self.idx1, json["_idx"])

    def test_key_base(self) -> None:
        """
        Test the key_base() method of the endpoint.
        """
        if self.running_in_test_base_class():
            return
        self.assertEqual(self.endpoint.key_base(), f"{self.row1}{self.idx1}")

    def test_verify(self) -> None:
        """
        Test the verify() method of the endpoint.
        """
        if self.running_in_test_base_class():
            return
        self.assertIsNone(self.endpoint.verify())
