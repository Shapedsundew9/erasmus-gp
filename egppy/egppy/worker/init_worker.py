"""Initialize the worker.

The configuration for the worker can come from either the command line as a configuration file or,
if none is specified, from the JSON REST API. The worker will then initialize the generation and
start the work loop.
"""
from egppy.worker.init_generation import init_generation


def init_worker():
    """Initialize the worker."""
    init_generation()


if __name__ == '__main__':
    init_worker()
