"""Unit tests for egpseed generate scripts.

This module contains tests for the generate scripts in egpseed that verify
they can execute without raising exceptions when run in read-only mode.
"""

from unittest import TestCase

from egpseed.generate_codons import generate_codons
from egpseed.generate_meta_codons import generate_meta_codons
from egpseed.generate_types import generate_types_def


class TestGenerateScripts(TestCase):
    """Test the generate scripts execute without exceptions."""

    def test_generate_codons_no_write(self) -> None:
        """Test that generate_codons executes without exceptions when write=False.

        This test verifies that the generate_codons function can run successfully
        without actually writing any files, ensuring the core logic executes cleanly.
        """
        try:
            generate_codons(write=False)
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.fail(f"generate_codons(write=False) raised an exception: {e}")

    def test_generate_meta_codons_no_write(self) -> None:
        """Test that generate_meta_codons executes without exceptions when write=False.

        This test verifies that the generate_meta_codons function can run successfully
        without actually writing any files, ensuring the core logic executes cleanly.
        """
        try:
            generate_meta_codons(write=False)
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.fail(f"generate_meta_codons(write=False) raised an exception: {e}")

    def test_generate_types_def_no_write(self) -> None:
        """Test that generate_types_def executes without exceptions when write=False.

        This test verifies that the generate_types_def function can run successfully
        without actually writing any files, ensuring the core logic executes cleanly.
        """
        try:
            generate_types_def(write=False)
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.fail(f"generate_types_def(write=False) raised an exception: {e}")
