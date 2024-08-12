"""Store typing definitions."""
from re import Pattern
from re import compile as regex_compile
from egppy.common.common import DictTypeAccessor, Validator
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class DatabaseConfig(Validator, DictTypeAccessor):
    """Configuration for databases in EGP.
    
    Must set from the JSON or internal types and validate the values.
    Getting the values returns the internal types.
    The to_json() method returns the JSON types.
    """

    _dbname_regex_str: str = r"[a-zA-Z][a-zA-Z0-9_-]{0,62}"
    _dbname_regex: Pattern[str] = regex_compile(_dbname_regex_str)
    _user_regex: Pattern[str] = _dbname_regex

    def __init__(self,
        dbname: str = "postgres",
        host: str = "localhost",
        password: str = "Password123!",
        port: int = 5432,
        maintenance_db: str = "postgres",
        retires: int = 3,
        user: str = "postgres"
    ) -> None:
        """Initialize the class."""
        setattr(self, "dbname", dbname)
        setattr(self, "host", host)
        setattr(self, "password", password)
        setattr(self, "port", port)
        setattr(self, "maintenance_db", maintenance_db)
        setattr(self, "retires", retires)
        setattr(self, "user", user)

    @property
    def dbname(self) -> str:
        """Get the dbname."""
        return self._dbname

    @dbname.setter
    def dbname(self, value: str) -> None:
        """The name of the database."""
        self._is_string("dbname", value)
        self._is_regex("dbname", value, self._dbname_regex)
        self._dbname = value

    @property
    def host(self) -> str:
        """Get the host."""
        return self._host

    @host.setter
    def host(self, value: str) -> None:
        """The host of the database."""
        self._is_string("host", value)
        self._is_ip_or_hostname("host", value)
        self._host = value

    @property
    def password(self) -> str:
        """Get the password."""
        return self._password

    @password.setter
    def password(self, value: str) -> None:
        """The password for the database."""
        self._is_password("password", value)
        self._password = value

    @property
    def port(self) -> int:
        """Get the port."""
        return self._port

    @port.setter
    def port(self, value: int) -> None:
        """The port of the database."""
        self._is_int("port", value)
        self._in_range("port", value, 1024, 65535)
        self._port = value

    @property
    def maintenance_db(self) -> str:
        """Get the maintenance database."""
        return self._maintenance_db

    @maintenance_db.setter
    def maintenance_db(self, value: str) -> None:
        """The maintenance database."""
        self._is_string("maintenance_db", value)
        self._is_regex("maintenance_db", value, self._dbname_regex)
        self._maintenance_db = value

    @property
    def retires(self) -> int:
        """Get the retires."""
        return self._retires

    @retires.setter
    def retires(self, value: int) -> None:
        """The number of retires."""
        self._is_int("retires", value)
        self._in_range("retires", value, 1, 10)
        self._retires = value

    def to_json(self) -> dict:
        """Get the configuration as a JSON object."""
        return {
            "dbname": self.dbname,
            "host": self.host,
            "password": self.password,
            "port": self.port,
            "maintenance_db": self.maintenance_db,
            "retires": self.retires,
            "user": self.user
        }

    @property
    def user(self) -> str:
        """Get the user."""
        return self._user

    @user.setter
    def user(self, value: str) -> None:
        """The user for the database."""
        self._is_string("user", value)
        self._is_regex("user", value, self._user_regex)
        self._user = value
