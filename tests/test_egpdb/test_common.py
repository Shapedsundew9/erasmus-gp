"""Unit tests for egpdb.common module."""

from os.path import dirname, join
from unittest import TestCase

# Standard EGP logging pattern
from egpcommon.egp_log import Logger, egp_logger
from egpdb.common import backoff_generator, connection_str_from_config
from egpdb.configuration import DatabaseConfig

_logger: Logger = egp_logger(name=__name__)

# Location of the password file
PSWD_FILE = join(dirname(__file__), "data", "db_password")


class TestBackoffGenerator(TestCase):
    """Test the backoff_generator function."""

    def test_default_first_value(self) -> None:
        """First value should equal initial_delay (with no fuzz)."""
        gen = backoff_generator(initial_delay=0.125, fuzz=False)
        self.assertAlmostEqual(next(gen), 0.125)

    def test_doubling(self) -> None:
        """Each step should double the previous (without fuzz)."""
        gen = backoff_generator(initial_delay=1.0, backoff_steps=4, fuzz=False)
        expected = [1.0, 2.0, 4.0, 8.0]
        for exp in expected:
            self.assertAlmostEqual(next(gen), exp)

    def test_saturation(self) -> None:
        """After backoff_steps doublings, the value should saturate at the max."""
        gen = backoff_generator(initial_delay=1.0, backoff_steps=3, fuzz=False)
        # Consume the 3 doubling steps: 1, 2, 4
        for _ in range(3):
            next(gen)
        # Saturated value should be 1.0 * 2**3 = 8.0 indefinitely
        for _ in range(10):
            self.assertAlmostEqual(next(gen), 8.0)

    def test_zero_backoff_steps(self) -> None:
        """With zero backoff steps, every value is the saturated max."""
        gen = backoff_generator(initial_delay=0.5, backoff_steps=0, fuzz=False)
        # The saturated value with 0 steps is initial_delay * 2**0 = 0.5
        for _ in range(5):
            self.assertAlmostEqual(next(gen), 0.5)

    def test_fuzz_varies(self) -> None:
        """With fuzz enabled, values should vary within +/-10% of the base."""
        gen = backoff_generator(initial_delay=1.0, backoff_steps=1, fuzz=True)
        values = [next(gen) for _ in range(20)]
        # With 20 samples, at least one should differ from 1.0 exactly
        self.assertTrue(any(abs(v - 1.0) > 0.001 for v in values[:10]))
        # All values should be within the fuzz range (0.9 to 1.1 for base 1.0 first step)
        for v in values[:1]:
            self.assertGreaterEqual(v, 0.9 * 0.9)  # conservative lower bound
            self.assertLessEqual(v, 1.1 * 1.1)  # conservative upper bound

    def test_infinite_iteration(self) -> None:
        """Generator never raises StopIteration."""
        gen = backoff_generator(initial_delay=0.01, backoff_steps=2, fuzz=False)
        for _ in range(1000):
            val = next(gen)
            self.assertIsInstance(val, float)


class TestConnectionStrFromConfig(TestCase):
    """Test the connection_str_from_config function."""

    def setUp(self) -> None:
        """Set up a valid DatabaseConfig."""
        self.config = DatabaseConfig(
            user="testuser",
            password=join(dirname(__file__), "data", "testpassword"),
            host="localhost",
            port=5432,
            dbname="testdb",
        )

    def test_without_password(self) -> None:
        """Connection string without password omits the :password portion."""
        result = connection_str_from_config(self.config, with_password=False)
        self.assertEqual(result, "postgresql://testuser@localhost:5432/testdb")
        self.assertNotIn("testpassword", result)

    def test_with_password(self) -> None:
        """Connection string with password includes the password."""
        result = connection_str_from_config(self.config, with_password=True)
        self.assertEqual(result, "postgresql://testuser:testpassword@localhost:5432/testdb")

    def test_default_no_password(self) -> None:
        """Default call omits password."""
        result = connection_str_from_config(self.config)
        self.assertNotIn(":", result.split("@")[0].split("//")[1])

    def test_different_port(self) -> None:
        """Non-default port is correctly included."""
        self.config.port = 15432
        result = connection_str_from_config(self.config, with_password=False)
        self.assertIn(":15432/", result)

    def test_ip_host(self) -> None:
        """IP address host is correctly included."""
        self.config.host = "192.168.1.100"
        result = connection_str_from_config(self.config, with_password=False)
        self.assertIn("192.168.1.100", result)
