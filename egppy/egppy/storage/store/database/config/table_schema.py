"""
Table schemas are YAML files that define the structure of tables in a database (datastore).
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
filename = join(dirname(abspath(__file__)), "schemas", "table_schema.yaml")
with open(filename, 'r', encoding='utf-8') as file:
    SCHEMA: dict[str, any] = safe_load(file)


def read_table_schema(file_path: str) -> dict[str, any]:
    """
    Read the table schema from a YAML file.

    Args:
        file_path: The path to the YAML file.

    Returns:
        The table schema as a dictionary.
    """
    _logger.info("Loading table schema file: %s", file_path)
    with open(file_path, 'r', encoding='utf-8') as table_file:
        table_schema_dict = safe_load(table_file)
    validate(table_schema_dict, SCHEMA)
    return table_schema_dict
