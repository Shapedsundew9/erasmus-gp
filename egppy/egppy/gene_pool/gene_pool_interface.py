"""The Gene Pool Interface."""

from egpdb.configuration import DatabaseConfig

from egppy.populations.configuration import PopulationConfig


class GenePoolInterface:
    """Gene Pool Interface.

    A Gene Pool Interface is used to interact with the Gene Pool.
    It takes a configuration file describing the Gene Pool database connection
    and provides methods to pull and push Genetic Codes to and from it.
    """

    def __init__(self, config: DatabaseConfig) -> None:
        """Initialize the Gene Pool Interface."""
        self.config = config.copy()

    def initial_generation_query(self, pconfig: PopulationConfig) -> list[bytes]:
        """Query the Gene Pool for the initial generation of this population."""
        # Place holder for the actual implementation
        return []
