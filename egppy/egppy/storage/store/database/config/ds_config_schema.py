"""
A Data Store maps directly to a database and is defined by a YAML file that contains:
    - The name of the data store as a human readable arbitrary string.
    - The name of the database
    - A list of YAML files that define the schemas of the tables in the database.
"""
from os.path import abspath, dirname, join
from yaml import safe_load
from jsonschema import validate
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# Schema for the datastore YAML file
filename = join(dirname(abspath(__file__)), "schemas", "ds_config_schema.yaml")
with open(filename, 'r', encoding='utf-8') as file:
    SCHEMA: dict[str, any] = safe_load(file)


def read_ds_config(file_path: str) -> dict[str, any]:
    """
    Read the datastore from a YAML file.

    Args:
        file_path: The path to the YAML file.

    Returns:
        The datastore as a dictionary.
    """
    _logger.info("Loading datastore config file: %s", file_path)
    with open(file_path, 'r', encoding='utf-8') as dsfile:
        datastore_dict = safe_load(dsfile)
    validate(datastore_dict, SCHEMA)
    return datastore_dict
