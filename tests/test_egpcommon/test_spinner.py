"""
Unit tests for the Spinner class in egpcommon.spinner.

This module contains a suite of tests to verify the correct behavior of the Spinner class,
which provides a simple command-line spinner for indicating progress. The tests cover
initialization, thread management, output handling, and edge cases such as stopping the
spinner without a running thread.

Tested features include:
- Initial state of the Spinner instance.
- Proper starting and stopping of the spinner thread.
- Output handling and message display.
- Daemon status of the spinner thread.
- Handling of multiple start/stop cycles.
- Default message behavior.

Mocks are used to avoid actual console output and delays during testing.
"""

import threading
import time
from unittest import TestCase, mock
from egpcommon.spinner import Spinner


class TestSpinner(TestCase):
    """
    Unit tests for the Spinner class.

    This test suite verifies the behavior of the Spinner class, including its
    initialization, thread management, output, and message handling.
    """

    def setUp(self) -> None:
        """Set up a Spinner instance for testing."""
        self.spinner = Spinner("Testing...")

    def test_initial_state(self) -> None:
        """Test the initial state of the Spinner instance."""
        self.assertEqual(self.spinner.message, "Testing...")
        self.assertFalse(self.spinner.running)
        self.assertIsNone(self.spinner.spinner_thread)
        self.assertEqual(self.spinner.spinner_chars, ["|", "/", "-", "\\"])

    def test_spin_stops_when_running_false(self) -> None:
        """Test that the spinner stops spinning when 'running' is set to False."""
        # Patch sys.stdout.write and time.sleep to avoid actual output and delay
        with (
            mock.patch("sys.stdout.write"),
            mock.patch("sys.stdout.flush"),
            mock.patch("time.sleep", return_value=None),
        ):
            self.spinner.running = True
            # Run _spin in a thread and stop after a short time
            # pylint:disable=protected-access
            t = threading.Thread(target=self.spinner._spin)
            t.start()
            time.sleep(0.2)
            self.spinner.running = False
            t.join(timeout=1)
            self.assertFalse(self.spinner.running)

    def test_start_creates_and_starts_thread(self) -> None:
        """Test that starting the spinner creates and starts a thread."""
        with mock.patch.object(self.spinner, "_spin") as mock_spin:
            self.spinner.start()
            self.assertTrue(self.spinner.running)
            self.assertIsInstance(self.spinner.spinner_thread, threading.Thread)
            self.spinner.running = False
            assert isinstance(self.spinner.spinner_thread, threading.Thread)
            self.spinner.spinner_thread.join(timeout=1)
            # The thread should have started and called _spin
            mock_spin.assert_called()

    def test_stop_joins_thread_and_prints_final_message(self) -> None:
        """Test that stopping the spinner joins the thread and prints the final message."""
        with mock.patch("sys.stdout.write") as mock_write, mock.patch("sys.stdout.flush"):
            self.spinner.running = True
            self.spinner.spinner_thread = threading.Thread(target=lambda: None)
            self.spinner.spinner_thread.start()
            self.spinner.stop("Finished!")
            self.assertFalse(self.spinner.running)
            mock_write.assert_any_call("\rFinished!\n")

    def test_stop_without_thread(self) -> None:
        """Test stopping the spinner when no thread exists."""
        with mock.patch("sys.stdout.write") as mock_write, mock.patch("sys.stdout.flush"):
            self.spinner.spinner_thread = None
            self.spinner.running = False
            self.spinner.stop("Done!")
            mock_write.assert_any_call("\rDone!\n")

    def test_spinner_thread_is_daemon(self) -> None:
        """Test that the spinner thread is set as a daemon thread."""
        with mock.patch.object(self.spinner, "_spin"):
            self.spinner.start()
            assert isinstance(self.spinner.spinner_thread, threading.Thread)
            self.assertTrue(self.spinner.spinner_thread.daemon)
            self.spinner.running = False
            self.spinner.spinner_thread.join(timeout=1)

    def test_spinner_with_default_message(self) -> None:
        """Test the spinner with the default message."""
        s = Spinner()
        self.assertEqual(s.message, "Processing...")

    def test_multiple_starts_and_stops(self) -> None:
        """Test multiple starts and stops of the spinner."""
        with mock.patch.object(self.spinner, "_spin"):
            self.spinner.start()
            t1 = self.spinner.spinner_thread
            self.spinner.stop("Stopped 1")
            self.spinner.start()
            t2 = self.spinner.spinner_thread
            self.assertNotEqual(t1, t2)
            self.spinner.stop("Stopped 2")
