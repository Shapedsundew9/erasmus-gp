"""The EGP Database Manager main module.

The EGP Database Manager main function is the entry point for the EGP Database Manager.
It is launched from the command line and is responsible for parsing command line arguments.

Command line arguments:
    # -h, --help: Display help message
    # -v, --version: Display version information
    # -c <config_file>, --config <config_file>: Use the specified configuration file

"""

from argparse import ArgumentParser, Namespace
from sys import argv
from sys import exit as sys_exit

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger
from egpcommon.egp_logo import gallery, header, header_lines

from egpdbmgr.configuration import DBManagerConfig
from egpdbmgr.db_manager import initialize, operations

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# EGP Database Manager header
# From ptfiglet: print(figlet_format("EGP DB Manager"))
# NB: Needs monospace font to display correctly
_HEADER = "\n".join(
    (
        " _____ ____ ____    ____  ____    __  __                                   ",
        "| ____/ ___|  _ \\  |  _ \\| __ )  |  \\/  | __ _ _ __   __ _  __ _  ___ _ __ ",
        "|  _|| |  _| |_) | | | | |  _ \\  | |\\/| |/ _` | '_ \\ / _` |/ _` |/ _ \\ '__|",
        "| |__| |_| |  __/  | |_| | |_) | | |  | | (_| | | | | (_| | (_| |  __/ |   ",
        "|_____\\____|_|     |____/|____/  |_|  |_|\\__,_|_| |_|\\__,_|\\__, |\\___|_|   ",
        "                                                           |___/           ",
    )
)


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
        "-g",
        "--gallery",
        help="Display the Erasmus GP logo gallery. All other options ignored.",
        action="store_true",
    )
    return parser.parse_args(args)


def init_db_manager(args: Namespace) -> None:
    """Initialize the DB Manager."""
    # Erasmus header to stdout and logfile
    print(header())
    print(_HEADER)
    for line in header_lines(attr="bw"):
        _logger.info(line)

    # Dump the default configuration
    if args.default_config:
        DBManagerConfig().dump_config()
        sys_exit(0)

    # Display the text logo art
    if args.gallery:
        print(gallery())
        sys_exit(0)

    # Load the configuration
    config = DBManagerConfig()
    if args.config_file:
        config.load_config(args.config_file)
    elif not args.use_default_config:
        _logger.error("No configuration file specified.")
        sys_exit(1)

    if not initialize(config):
        operations(config)
    else:
        _logger.info("Successfully initialized. Restart required. Exiting with code 10.")
        sys_exit(10)
    _logger.info("DB Manager operations completed. Exiting with code 0.")


if __name__ == "__main__":
    init_db_manager(parse_cmdline_args(argv[1:]))
