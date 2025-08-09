"""A simple console spinner to indicate processing status."""

import sys
import threading
import time


class Spinner:
    """A simple console spinner to indicate processing status."""

    def __init__(self, message="Processing...") -> None:
        self.spinner_chars = ["|", "/", "-", "\\"]
        self.message = message
        self.running = False
        self.spinner_thread = None

    def _spin(self):
        """Internal method to run the spinner animation."""
        ii = 0
        while self.running:
            # Print the spinner character and the message, then move cursor back
            sys.stdout.write(f"\r{self.message} {self.spinner_chars[ii % len(self.spinner_chars)]}")
            sys.stdout.flush()  # Ensure the output is immediately written to the console
            ii += 1
            time.sleep(0.1)  # Control the speed of the spin

    def start(self):
        """Starts the spinner animation in a separate thread."""
        self.running = True
        self.spinner_thread = threading.Thread(target=self._spin)
        self.spinner_thread.daemon = (
            True  # Allow the main program to exit even if spinner is running
        )
        self.spinner_thread.start()

    def stop(self, final_message: str = "Done.") -> None:
        """Stops the spinner animation and prints a final message.

        Replaces the spinner on the same line with '<message><final_message>'.
        """
        self.running = False
        if self.spinner_thread and self.spinner_thread.is_alive():
            self.spinner_thread.join()  # Wait for the spinner thread to finish
        # Clear the current line and replace the spinner with the final message appended to the base message.
        # Using ANSI escape code (ESC[2K) to clear the line ensures no leftover characters remain.
        sys.stdout.write("\r\033[2K" + self.message + final_message + "\n")
        sys.stdout.flush()


# --- Example Usage ---

if __name__ == "__main__":
    print("Starting a simulated long-running task...")

    # Create a spinner instance
    spinner = Spinner("Calculating results...")

    try:
        spinner.start()  # Start the spinner

        # Simulate some long-running task
        for i in range(1, 6):
            time.sleep(1)  # Simulate 1 second of work
            print(f"\nCompleted step {i}/5")  # Example of other output during spin (requires care)
            # Re-start spinner message after other output
            # This is important if you print anything else to the console
            # while the spinner is running.
            if spinner.running:  # Check if spinner is still active
                sys.stdout.write(
                    f"\r{spinner.message} "
                    f"{spinner.spinner_chars[(i-1) % len(spinner.spinner_chars)]}"
                )
                sys.stdout.flush()

        spinner.stop("Task complete!")  # Stop the spinner with a success message

        print("Script finished successfully.")

        # Example with a different message and shorter duration
        print("\nStarting another short task...")
        spinner2 = Spinner("Loading data...")
        spinner2.start()
        time.sleep(2)  # Simulate 2 seconds
        spinner2.stop("Data loaded!")

        # Example of stopping due to an error
        print("\nSimulating an error during a task...")
        spinner3 = Spinner("Processing files...")
        spinner3.start()
        try:
            time.sleep(3)
            raise ValueError("Something went wrong!")
        except ValueError as e:
            spinner3.stop(f"Error: {e}")
            sys.exit(1)  # Exit with an error code

    except KeyboardInterrupt:
        spinner.stop("Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:  # pylint:disable=broad-exception-caught
        spinner.stop(f"An unexpected error occurred: {e}")
        sys.exit(1)
