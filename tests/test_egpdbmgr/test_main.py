"""Tests for the egpdbmgr main module.

Tests cover command line argument parsing and the init_db_manager
entry point with various argument combinations.
"""

import unittest
from argparse import Namespace

from egpdbmgr.main import parse_cmdline_args


class TestParseCmdlineArgs(unittest.TestCase):
    """Test the parse_cmdline_args function."""

    def test_no_args(self) -> None:
        """Test parsing with no arguments."""
        args: Namespace = parse_cmdline_args([])
        self.assertIsNone(args.config_file)
        self.assertFalse(args.use_default_config)
        self.assertFalse(args.default_config)
        self.assertFalse(args.gallery)

    def test_config_file(self) -> None:
        """Test parsing with -c argument."""
        args: Namespace = parse_cmdline_args(["-c", "test_config.json"])
        self.assertEqual(args.config_file, "test_config.json")
        self.assertFalse(args.use_default_config)
        self.assertFalse(args.default_config)

    def test_config_file_long(self) -> None:
        """Test parsing with --config_file argument."""
        args: Namespace = parse_cmdline_args(["--config_file", "test_config.json"])
        self.assertEqual(args.config_file, "test_config.json")

    def test_use_default_config(self) -> None:
        """Test parsing with -D argument."""
        args: Namespace = parse_cmdline_args(["-D"])
        self.assertTrue(args.use_default_config)
        self.assertFalse(args.default_config)
        self.assertFalse(args.gallery)

    def test_default_config(self) -> None:
        """Test parsing with -d argument."""
        args: Namespace = parse_cmdline_args(["-d"])
        self.assertTrue(args.default_config)
        self.assertFalse(args.use_default_config)
        self.assertFalse(args.gallery)

    def test_gallery(self) -> None:
        """Test parsing with -g argument."""
        args: Namespace = parse_cmdline_args(["-g"])
        self.assertTrue(args.gallery)
        self.assertFalse(args.use_default_config)
        self.assertFalse(args.default_config)

    def test_config_file_with_default(self) -> None:
        """Test parsing with -c and -D arguments.

        -c is not in the mutually exclusive group, so it can be combined with -D.
        """
        args: Namespace = parse_cmdline_args(["-c", "test.json", "-D"])
        self.assertEqual(args.config_file, "test.json")
        self.assertTrue(args.use_default_config)

    # pylint: disable=invalid-name
    def test_mutually_exclusive_d_D(self) -> None:
        """Test that -d and -D are mutually exclusive."""
        with self.assertRaises(SystemExit):
            parse_cmdline_args(["-d", "-D"])

    def test_mutually_exclusive_d_g(self) -> None:
        """Test that -d and -g are mutually exclusive."""
        with self.assertRaises(SystemExit):
            parse_cmdline_args(["-d", "-g"])

    def test_mutually_exclusive_D_g(self) -> None:
        """Test that -D and -g are mutually exclusive."""
        with self.assertRaises(SystemExit):
            parse_cmdline_args(["-D", "-g"])


if __name__ == "__main__":
    unittest.main()
