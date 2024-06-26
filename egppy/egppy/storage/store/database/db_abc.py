"""Database interface abstract base class."""
from abc import ABC, abstractmethod
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class DBABC(ABC):
    """Database interface abstract base class."""

    @abstractmethod
    def __init__(self, db_config: dict[str, any]) -> None:
        """
        Initialize the database.
        If the database does not exist, create it.

        Args:
            db_config: The configuration of the database.
            See egppy/database/config/schemas/ds_config_schema.yaml database section for details.
        """

    @abstractmethod
    def exists(self) -> bool:
        """
        Check if the database exists.

        Returns:
            True if the database exists, False otherwise.
        """
