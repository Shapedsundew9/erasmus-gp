"""Initialize the worker.

The configuration for the worker can come from either the command line as a configuration file or,
if none is specified, from the JSON REST API. The worker will then initialize the generation and
start the work loop.
"""

from datetime import datetime
from sys import argv, exit as sys_exit
from argparse import ArgumentParser, Namespace
from uuid import UUID, uuid4
from egppy.populations.configuration import PopulationConfig
from egppy.worker.init_generation import init_generation
from egppy.worker.configuration import WorkerConfig
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.common.egp_logo import header, header_lines, gallery
from egppy.problems.genesis import EGP_PROBLEM_CONFIG
from egppy.gc_graph.ep_type import (
    interface_definition,
    ordered_interface_hash,
    unordered_interface_hash,
    VType,
)


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


def parse_cmdline_args(args: list[str]) -> Namespace:
    """Parse the command line arguments."""
    parser: ArgumentParser = ArgumentParser(prog="egp-worker")
    meg = parser.add_mutually_exclusive_group()
    parser.add_argument("-c", "--config_file", help="Path to a JSON configuration file.")
    meg.add_argument(
        "-D",
        "--use_default_config",
        help="Use the default internal configuration. "
        "This option will start work on the most interesting community problem.",
        action="store_true",
    )
    meg.add_argument(
        "-d",
        "--default_config",
        help="Generate a default configuration file. "
        "config.json will be stored in the current directory. All other options ignored.",
        action="store_true",
    )
    meg.add_argument(
        "-l",
        "--population_list",
        help="Update the configuration file with the popluation definitions from the Gene Pool.",
        action="store_true",
    )
    parser.add_argument(
        "-s",
        "--sub_processes",
        help="The number of subprocesses to spawn for evolution. "
        "Default is the number of cores - 1,",
        type=int,
        default=0,
    )
    meg.add_argument(
        "-g",
        "--gallery",
        help="Display the Erasmus GP logo gallery. All other options ignored.",
        action="store_true",
    )
    return parser.parse_args(args)


def init_worker(args: Namespace) -> None:
    """Initialize the worker."""
    # Erasmus header to stdout and logfile
    print(header())
    for line in header_lines(attr="bw"):
        _logger.info(line)

    # Dump the default configuration
    if args.default_config:
        WorkerConfig().dump_config()
        sys_exit(0)

    # Display the text logo art
    if args.gallery:
        print(gallery())
        sys_exit(0)

    # Load & validate worker configuration
    config = WorkerConfig()
    if not args.use_default_config:
        config.load_config(args.config_file)

    # Get the population configurations & set the worker ID
    worker_id: UUID = uuid4()
    _logger.info("Worker ID: %s", worker_id)

    # FIXME: For now we will hardcode all the values regardless of the configuration file
    # EGP_PROBLEM_CONFIG should be parsed as a problem configuration structure
    # but only where it is needed. This information is not needed here.
    ieps, itypes, iidx = interface_definition(EGP_PROBLEM_CONFIG["inputs"], VType.EP_TYPE_STR)
    oeps, otypes, oidx = interface_definition(EGP_PROBLEM_CONFIG["outputs"], VType.EP_TYPE_STR)
    config.populations.configs = [
        PopulationConfig(
            uid=0,
            problem="2" * 64,
            worker_id=worker_id,
            size=100,
            inputs=EGP_PROBLEM_CONFIG["inputs"],
            outputs=EGP_PROBLEM_CONFIG["outputs"],
            ordered_interface_hash=ordered_interface_hash(itypes, otypes, iidx, oidx),
            unordered_interface_hash=unordered_interface_hash(ieps, oeps),
            name=EGP_PROBLEM_CONFIG["name"],
            description=EGP_PROBLEM_CONFIG["description"],
            meta_data=None,
            created=datetime.now(),
            updated=datetime.now(),
            fitness_function=EGP_PROBLEM_CONFIG["fitness_function"],
            survivability_function=EGP_PROBLEM_CONFIG["survivability_function"],
        )
    ]

    init_generation(config)
    _logger.info("Worker shutdown complete.")


if __name__ == "__main__":
    init_worker(parse_cmdline_args(argv[1:]))
