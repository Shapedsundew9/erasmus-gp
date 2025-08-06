"""Store typing definitions."""

from os.path import expanduser, normpath
from re import Pattern
from re import compile as regex_compile
from typing import Any, Callable

from egpcommon.common import DictTypeAccessor
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger
from egpcommon.validator import Validator

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

    # pylint: disable=fixme
    # TODO: Split dbname from postgres host
    # TODO: Split maintenance db user from standard DB user

    _dbname_regex_str: str = r"[a-zA-Z][a-zA-Z0-9_-]{0,62}"
    _dbname_regex: Pattern[str] = regex_compile(_dbname_regex_str)
    _user_regex: Pattern[str] = _dbname_regex

    def __init__(
        self,
        dbname: str = "erasmus_db",
        host: str = "postgres",
        password: str = "/run/secrets/db_password",
        port: int = 5432,
        maintenance_db: str = "postgres",
        retries: int = 3,
        user: str = "postgres",
    ) -> None:
        """Initialize the class."""
        setattr(self, "dbname", dbname)
        setattr(self, "host", host)
        setattr(self, "password", password)
        setattr(self, "port", port)
        setattr(self, "maintenance_db", maintenance_db)
        setattr(self, "retries", retries)
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
        with open(self._password, "r", encoding="utf-8") as f:
            return f.read().strip()

    @password.setter
    def password(self, value: str) -> None:
        """The file that contains the password for the database."""
        self._is_filename("password", value)
        value = expanduser(normpath(value))
        self._is_accessible("password", value)
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
    def retries(self) -> int:
        """Get the retries."""
        return self._retries

    @retries.setter
    def retries(self, value: int) -> None:
        """The number of retries."""
        self._is_int("retries", value)
        self._in_range("retries", value, 1, 10)
        self._retries = value

    def to_json(self) -> dict:
        """Get the configuration as a JSON object."""
        return {
            "dbname": self.dbname,
            "host": self.host,
            # NOTE: Returns the path to the file not the actual password.
            "password": self._password,
            "port": self.port,
            "maintenance_db": self.maintenance_db,
            "retries": self.retries,
            "user": self.user,
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


class ColumnSchema(Validator, DictTypeAccessor):
    """Table schema column definition.

    Must set from the JSON or internal types and validate the values.
    Getting the values returns the internal types.
    The to_json() method returns the JSON types.
    """

    def __init__(
        self,
        db_type: str = "VARCHAR",
        volatile: bool = False,
        default: str | None = None,
        description: str | None = None,
        nullable: bool = False,
        primary_key: bool = False,
        index: str | None = None,
        unique: bool = False,
    ) -> None:
        """Initialize the class.

        Args
        ----
        db_type : Postgresql type expression.
        volatile : Application hint that the column may be updated after initialisation when True.
        default : Default value of the column specified as an SQL string after 'DEFAULT '
                  in the CREATE TABLE statement.
        description : Description of the table.
        nullable : If True the column can contain NULL values.
        primary_key : Column is the primary key and automatically indexed if True.
                      Primary key columns cannot have NULL entries.
        index : Column is indexed with the selected algorithm. PRIMARY KEY or UNIQUE columns cannot
                be additionally indexed.
        unique : Entries in the column are unique and automatically indexed if True.
                 Cannot also be primary keys.
        """
        setattr(self, "db_type", db_type)
        setattr(self, "volatile", volatile)
        setattr(self, "default", default)
        setattr(self, "description", description)
        setattr(self, "nullable", nullable)
        setattr(self, "primary_key", primary_key)
        setattr(self, "index", index)
        setattr(self, "unique", unique or primary_key)
        self.consistency()

    def consistency(self) -> None:
        """Check the consistency of the schema column."""
        if self.primary_key:
            if self.nullable:
                raise ValueError("Primary key columns cannot have NULL entries.")
            if not self.unique:
                raise RuntimeError("Primary key columns must also be unique.")
        if self.index is not None:
            if self.primary_key:
                raise ValueError("Primary key columns cannot be additionally indexed.")
            if self.unique:
                raise ValueError("Unique columns cannot be additionally indexed.")

    def to_json(self) -> dict:
        """Get the configuration as a JSON object."""
        return {
            "db_type": self.db_type,
            "volatile": self.volatile,
            "default": self.default,
            "description": self.description,
            "nullable": self.nullable,
            "primary_key": self.primary_key,
            "index": self.index,
            "unique": self.unique,
        }

    @property
    def db_type(self) -> str:
        """Get the db_type."""
        return self._db_type

    @db_type.setter
    def db_type(self, value: str) -> None:
        """The Postgresql type expression."""
        self._is_not_none("db_type", value)
        self._is_printable_string("db_type", value)
        self._is_length("db_type", value, 1, 64)
        self._db_type = value

    @property
    def volatile(self) -> bool:
        """Get the volatile."""
        return self._volatile

    @volatile.setter
    def volatile(self, value: bool) -> None:
        """Application hint that the column may be updated after initialisation when True."""
        self._is_bool("volatile", value)
        self._volatile = value

    @property
    def default(self) -> str | None:
        """Get the default."""
        return self._default

    @default.setter
    def default(self, value: str | None) -> None:
        """Default value of the column specified as an SQL string after 'DEFAULT '."""
        if value is not None:
            self._is_string("default", value)
            self._is_length("default", value, 1, 64)
        self._default = value

    @property
    def description(self) -> str | None:
        """Get the description."""
        return self._description

    @description.setter
    def description(self, value: str | None) -> None:
        """Description of the table."""
        if value is not None:
            self._is_printable_string("description", value)
            self._is_length("description", value, 1, 256)
        self._description = value

    @property
    def nullable(self) -> bool:
        """Get the nullable."""
        return self._nullable

    @nullable.setter
    def nullable(self, value: bool) -> None:
        """If True the column can contain NULL values."""
        self._is_bool("nullable", value)
        self._nullable = value

    @property
    def primary_key(self) -> bool:
        """Get the primary_key."""
        return self._primary_key

    @primary_key.setter
    def primary_key(self, value: bool) -> None:
        """Column is the primary key and automatically indexed if True."""
        self._is_bool("primary_key", value)
        self._primary_key = value

    @property
    def index(self) -> str | None:
        """Get the index."""
        return self._index

    @index.setter
    def index(self, value: str | None) -> None:
        """Column is indexed with the selected algorithm."""
        if value is not None:
            self._is_one_of("index", value, ("btree", "hash", "gist", "gin"))
        self._index = value

    @property
    def unique(self) -> bool:
        """Get the unique."""
        return self._unique

    @unique.setter
    def unique(self, value: bool) -> None:
        """Entries in the column are unique and automatically indexed if True."""
        self._is_bool("unique", value)
        self._unique = value


ConversionFunc = Callable | None
# ('column_name', encode_into_db_func, decode_from_db_func)
Conversion = tuple[str, ConversionFunc, ConversionFunc]
Conversions = tuple[Conversion, ...]
PtrMap = dict[str, str]
TableSchema = dict[str, ColumnSchema]


class TableConfig(Validator, DictTypeAccessor):
    """Table configuration."""

    def __init__(
        self,
        database: DatabaseConfig | dict[str, Any] | None = None,
        table: str = "default_table",
        schema: TableSchema | dict[str, dict[str, Any]] | None = None,
        ptr_map: PtrMap | None = None,
        data_file_folder: str = ".",
        data_files: list[str] | None = None,
        delete_db: bool = False,
        delete_table: bool = False,
        create_db: bool = False,
        create_table: bool = False,
        wait_for_db: bool = False,
        wait_for_table: bool = False,
        conversions: Conversions = tuple(),
    ) -> None:
        """Initialize the class.

        Args
        ----
        database : Definition of the database location and user to access the table.
        table : The name of the table.
        schema : The schema of the table.
        ptr_map : Defines relationships between fields for tables consisting of graph node rows.
        data_file_folder : The folder containing the data files to populate the table on creation.
        data_files : The data files to populate the table on creation.
        delete_db : If the DB exists DROP it. Requires create_db to be True and wait_for_db to be
                    False as well as either create_table or wait_for_table to be True.
        delete_table : If the table exists DROP it. Requires create_table to be True and
                       wait_for_table be False.
        create_db : If the DB does not exist create it. wait_for_db must be False.
        create_table : If the table does not exist create it. wait_for_table must be False.
        wait_for_db : If the DB does not exist keep trying to connect until it does.
                      create_db must be False and delete_db must be False.
        wait_for_table : If the table does not exist keep trying to connect until it does.
                         create_table must be False and delete_table must be False.
        conversions : Conversion functions from DB type to application type and back.

        Note that the ptr_map is a dictionary of key:value pairs where the key is a field in the
        schema and the value is a field in the schema. The key field is a pointer to the value
        field. A value cannot be the same as a key as this would be a circular reference.
        """
        if isinstance(database, dict):
            assert (
                "database" not in database
            ), "Did you remember to unpack the configuration dictionary?"
        setattr(self, "database", database if database is not None else DatabaseConfig())
        setattr(self, "table", table)
        setattr(self, "schema", schema if schema is not None else {})
        setattr(self, "ptr_map", ptr_map if ptr_map is not None else {})
        setattr(self, "data_file_folder", data_file_folder)
        setattr(self, "data_files", data_files if data_files is not None else [])
        setattr(self, "delete_db", delete_db)
        setattr(self, "delete_table", delete_table)
        setattr(self, "create_db", create_db)
        setattr(self, "create_table", create_table)
        setattr(self, "wait_for_db", wait_for_db)
        setattr(self, "wait_for_table", wait_for_table)
        setattr(self, "conversions", conversions)
        self.consistency()

    def consistency(self) -> None:
        """Check the consistency of the table configuration."""
        for k, v in self.ptr_map.items():  # pylint error? pylint: disable=no-member
            if k not in self.schema:
                raise ValueError(f"Pointer map key '{k}' not in schema.")
            if v not in self.schema:
                raise ValueError(f"Pointer map value '{v}' not in schema.")
            if v in self.ptr_map:
                raise ValueError(f"Pointer map value '{v}' is also a key. Circular reference.")
        if self.delete_db:
            if not self.create_db:
                raise ValueError("Delete DB requires create DB.")
            if self.wait_for_db:
                raise ValueError("Delete DB requires wait for DB to be False.")
            if not self.create_table and not self.wait_for_table:
                raise ValueError("Delete DB requires create table or wait for table.")
        if self.delete_table:
            if not self.create_table:
                raise ValueError("Delete table requires create table.")
            if self.wait_for_table:
                raise ValueError("Delete table requires wait for table to be False.")
        if self.create_db and self.wait_for_db:
            raise ValueError("Create DB requires wait for DB to be False.")
        if self.create_table and self.wait_for_table:
            raise ValueError("Create table requires wait for table to be False.")

    def to_json(self) -> dict:
        """Get the configuration as a JSON object."""
        return {
            "database": self.database.to_json(),
            "table": self.table,
            "schema": {k: v.to_json() for k, v in self.schema.items()},
            "ptr_map": self.ptr_map,
            "data_file_folder": self.data_file_folder,
            "data_files": self.data_files,
            "delete_db": self.delete_db,
            "delete_table": self.delete_table,
            "create_db": self.create_db,
            "create_table": self.create_table,
            "wait_for_db": self.wait_for_db,
            "wait_for_table": self.wait_for_table,
            "conversions": self.conversions,
        }

    @property
    def database(self) -> DatabaseConfig:
        """Get the database."""
        return self._database

    @database.setter
    def database(self, value: DatabaseConfig | dict[str, Any]) -> None:
        """Normalized DB configuration."""
        if isinstance(value, dict):
            value = DatabaseConfig(**value)
        self._is_instance("database", value, DatabaseConfig)
        self._database = value

    @property
    def table(self) -> str:
        """Get the table."""
        return self._table

    @table.setter
    def table(self, value: str) -> None:
        """The table name."""
        self._is_printable_string("table", value)
        self._is_length("table", value, 1, 64)
        self._table = value

    @property
    def schema(self) -> TableSchema:
        """Get the schema."""
        return self._schema

    @schema.setter
    def schema(self, value: TableSchema | dict[str, dict[str, Any]]) -> None:
        """Table schema."""
        self._is_dict("schema", value)
        _value: TableSchema = {}
        for k, v in value.items():
            _value[k] = ColumnSchema(**v) if isinstance(v, dict) else v
        self._schema = _value

    @property
    def ptr_map(self) -> PtrMap:
        """Get the ptr_map."""
        return self._ptr_map

    @ptr_map.setter
    def ptr_map(self, value: PtrMap) -> None:
        """Pointer map."""
        self._is_dict("ptr_map", value)
        for k, v in value.items():
            self._is_printable_string("ptr_map", k)
            self._is_printable_string("ptr_map", v)
            self._is_length("ptr_map", k, 1, 64)
            self._is_length("ptr_map", v, 1, 64)
        self._ptr_map = value

    @property
    def data_file_folder(self) -> str:
        """Get the data_file_folder."""
        return self._data_file_folder

    @data_file_folder.setter
    def data_file_folder(self, value: str) -> None:
        """The data file folder."""
        self._is_path("data_file_folder", value)
        self._is_length("data_file_folder", value, 0, 1024)
        self._data_file_folder = expanduser(normpath(value))

    @property
    def data_files(self) -> list[str]:
        """Get the data_files."""
        return self._data_files

    @data_files.setter
    def data_files(self, value: list[str]) -> None:
        """The data files."""
        self._is_list("data_files", value)
        for v in value:
            self._is_filename("data_files", v)
        self._data_files = value

    @property
    def delete_db(self) -> bool:
        """Get the delete_db."""
        return self._delete_db

    @delete_db.setter
    def delete_db(self, value: bool) -> None:
        """Delete the database."""
        self._is_bool("delete_db", value)
        self._delete_db = value

    @property
    def delete_table(self) -> bool:
        """Get the delete_table."""
        return self._delete_table

    @delete_table.setter
    def delete_table(self, value: bool) -> None:
        """Delete the table."""
        self._is_bool("delete_table", value)
        self._delete_table = value

    @property
    def create_db(self) -> bool:
        """Get the create_db."""
        return self._create_db

    @create_db.setter
    def create_db(self, value: bool) -> None:
        """Create the database."""
        self._is_bool("create_db", value)
        self._create_db = value

    @property
    def create_table(self) -> bool:
        """Get the create_table."""
        return self._create_table

    @create_table.setter
    def create_table(self, value: bool) -> None:
        """Create the table."""
        self._is_bool("create_table", value)
        self._create_table = value

    @property
    def wait_for_db(self) -> bool:
        """Get the wait_for_db."""
        return self._wait_for_db

    @wait_for_db.setter
    def wait_for_db(self, value: bool) -> None:
        """Wait for the database."""
        self._is_bool("wait_for_db", value)
        self._wait_for_db = value

    @property
    def wait_for_table(self) -> bool:
        """Get the wait_for_table."""
        return self._wait_for_table

    @wait_for_table.setter
    def wait_for_table(self, value: bool) -> None:
        """Wait for the table."""
        self._is_bool("wait_for_table", value)
        self._wait_for_table = value

    @property
    def conversions(self) -> Conversions:
        """Get the conversions."""
        return self._conversions

    @conversions.setter
    def conversions(self, value: Conversions) -> None:
        """Conversions."""
        self._is_tuple("conversions", value)
        for v in value:
            if isinstance(v, tuple):
                self._is_tuple("conversions", v)
                self._is_length("conversions", v, 3, 3)
                self._is_printable_string("conversions", v[0])
                if v[1] is not None:
                    self._is_callable("conversions", v[1])
                if v[2] is not None:
                    self._is_callable("conversions", v[2])
            else:
                self._is_callable("conversions", v)
        self._conversions = value
