"""Store typing definitions."""

from os.path import expanduser, normpath
from re import Pattern
from re import compile as regex_compile
from typing import Any, Callable

from egpcommon.common import DictTypeAccessor
from egpcommon.common_obj import CommonObj
from egpcommon.egp_log import Logger, egp_logger
from egpcommon.validator import Validator

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


class DatabaseConfig(Validator, DictTypeAccessor, CommonObj):
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
        host: str = "localhost",
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
        if not self._is_string("dbname", value):
            raise ValueError(f"dbname must be a string, but is {type(value)}")
        if not self._is_regex("dbname", value, self._dbname_regex):
            raise ValueError(f"dbname must match regex {self._dbname_regex_str}, but is {value}")
        self._dbname = value

    @property
    def host(self) -> str:
        """Get the host."""
        return self._host

    @host.setter
    def host(self, value: str) -> None:
        """The host of the database."""
        if not self._is_string("host", value):
            raise ValueError(f"host must be a string, but is {type(value)}")
        if not self._is_ip_or_hostname("host", value):
            raise ValueError(f"host must be an IP or hostname, but is {value}")
        self._host = value

    @property
    def maintenance_db(self) -> str:
        """Get the maintenance database."""
        return self._maintenance_db

    @maintenance_db.setter
    def maintenance_db(self, value: str) -> None:
        """The maintenance database."""
        if not self._is_string("maintenance_db", value):
            raise ValueError(f"maintenance_db must be a string, but is {type(value)}")
        if not self._is_regex("maintenance_db", value, self._dbname_regex):
            raise ValueError(
                f"maintenance_db must match regex {self._dbname_regex_str}, but is {value}"
            )
        self._maintenance_db = value

    @property
    def password(self) -> str:
        """Get the password."""
        with open(self._password, "r", encoding="utf-8") as f:
            return f.read().strip()

    @password.setter
    def password(self, value: str) -> None:
        """The file that contains the password for the database."""
        if not self._is_filename("password", value):
            raise ValueError(f"password must be a filename, but is {value}")
        value = expanduser(normpath(value))
        if not self._is_accessible("password", value):
            raise ValueError(f"password file is not accessible: {value}")
        self._password = value

    @property
    def port(self) -> int:
        """Get the port."""
        return self._port

    @port.setter
    def port(self, value: int) -> None:
        """The port of the database."""
        if not self._is_int("port", value):
            raise ValueError(f"port must be an int, but is {type(value)}")
        if not self._in_range("port", value, 1024, 65535):
            raise ValueError(f"port must be between 1024 and 65535, but is {value}")
        self._port = value

    @property
    def retries(self) -> int:
        """Get the retries."""
        return self._retries

    @retries.setter
    def retries(self, value: int) -> None:
        """The number of retries."""
        if not self._is_int("retries", value):
            raise ValueError(f"retries must be an int, but is {type(value)}")
        if not self._in_range("retries", value, 1, 10):
            raise ValueError(f"retries must be between 1 and 10, but is {value}")
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
        if not self._is_string("user", value):
            raise ValueError(f"user must be a string, but is {type(value)}")
        if not self._is_regex("user", value, self._user_regex):
            raise ValueError(f"user must match regex {self._user_regex}, but is {value}")
        self._user = value


class ColumnSchema(Validator, DictTypeAccessor, CommonObj):
    """Table schema column definition.

    Must set from the JSON or internal types and validate the values.
    Getting the values returns the internal types.
    The to_json() method returns the JSON types.
    """

    __slots__ = (
        "_db_type",
        "_volatile",
        "_default",
        "_description",
        "_nullable",
        "_primary_key",
        "_index",
        "_unique",
        "_alignment",
    )
    # Useful for filtering keys in a dict of ColumnSchema parameters
    parameters: set[str] = {
        "db_type",
        "volatile",
        "default",
        "description",
        "nullable",
        "primary_key",
        "index",
        "unique",
        "alignment",
    }

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
        alignment: int = 1,
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
        setattr(self, "alignment", alignment)
        self.verify()

    @property
    def alignment(self) -> int:
        """Get the alignment."""
        return self._alignment

    @alignment.setter
    def alignment(self, value: int) -> None:
        """Set the alignment."""
        if not self._is_int("alignment", value):
            raise ValueError(f"alignment must be an int, but is {type(value)}")
        self._alignment = value

    @property
    def db_type(self) -> str:
        """Get the db_type."""
        return self._db_type

    @db_type.setter
    def db_type(self, value: str) -> None:
        """The Postgresql type expression."""
        if not self._is_not_none("db_type", value):
            raise ValueError("db_type cannot be None")
        if not self._is_printable_string("db_type", value):
            raise ValueError(f"db_type must be a printable string, but is {value}")
        if not self._is_length("db_type", value, 1, 64):
            raise ValueError(f"db_type length must be between 1 and 64, but is {len(value)}")
        self._db_type = value

    @property
    def default(self) -> str | None:
        """Get the default."""
        return self._default

    @default.setter
    def default(self, value: str | None) -> None:
        """Default value of the column specified as an SQL string after 'DEFAULT '."""
        if value is not None:
            if not self._is_string("default", value):
                raise ValueError(f"default must be a string, but is {type(value)}")
        self._default = value

    @property
    def description(self) -> str | None:
        """Get the description."""
        return self._description

    @description.setter
    def description(self, value: str | None) -> None:
        """Description of the table."""
        if value is not None:
            if not self._is_printable_string("description", value):
                raise ValueError(f"description must be a printable string, but is {value}")
            if not self._is_length("description", value, 1, 256):
                raise ValueError(
                    f"description length must be between 1 and 256, but is {len(value)}"
                )
        self._description = value

    @property
    def index(self) -> str | None:
        """Get the index."""
        return self._index

    @index.setter
    def index(self, value: str | None) -> None:
        """Column is indexed with the selected algorithm."""
        if value is not None:
            if not self._is_one_of("index", value, ("btree", "hash", "gist", "gin")):
                raise ValueError(
                    f"index must be one of ('btree', 'hash', 'gist', 'gin'), but is {value}"
                )
        self._index = value

    @property
    def nullable(self) -> bool:
        """Get the nullable."""
        return self._nullable

    @nullable.setter
    def nullable(self, value: bool) -> None:
        """If True the column can contain NULL values."""
        if not self._is_bool("nullable", value):
            raise ValueError(f"nullable must be a bool, but is {type(value)}")
        self._nullable = value

    @property
    def primary_key(self) -> bool:
        """Get the primary_key."""
        return self._primary_key

    @primary_key.setter
    def primary_key(self, value: bool) -> None:
        """Column is the primary key and automatically indexed if True."""
        if not self._is_bool("primary_key", value):
            raise ValueError(f"primary_key must be a bool, but is {type(value)}")
        self._primary_key = value

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
    def unique(self) -> bool:
        """Get the unique."""
        return self._unique

    @unique.setter
    def unique(self, value: bool) -> None:
        """Entries in the column are unique and automatically indexed if True."""
        if not self._is_bool("unique", value):
            raise ValueError(f"unique must be a bool, but is {type(value)}")
        self._unique = value

    def verify(self) -> None:
        """Check the schema column."""
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
        super().verify()

    @property
    def volatile(self) -> bool:
        """Get the volatile."""
        return self._volatile

    @volatile.setter
    def volatile(self, value: bool) -> None:
        """Application hint that the column may be updated after initialisation when True."""
        if not self._is_bool("volatile", value):
            raise ValueError(f"volatile must be a bool, but is {type(value)}")
        self._volatile = value


ConversionFunc = Callable | None
# ('column_name', encode_into_db_func, decode_from_db_func)
Conversion = tuple[str, ConversionFunc, ConversionFunc]
Conversions = tuple[Conversion, ...]
PtrMap = dict[str, str]
TableSchema = dict[str, ColumnSchema]


class TableConfig(Validator, DictTypeAccessor, CommonObj):
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
        self.verify()

    @property
    def conversions(self) -> Conversions:
        """Get the conversions."""
        return self._conversions

    @conversions.setter
    def conversions(self, value: Conversions) -> None:
        """Conversions."""
        if not self._is_tuple("conversions", value):
            raise ValueError("conversions must be a tuple")
        for v in value:
            if isinstance(v, tuple):
                if not self._is_tuple("conversions", v):
                    raise ValueError("conversion must be a tuple")
                if not self._is_length("conversions", v, 3, 3):
                    raise ValueError("conversion tuple must have 3 elements")
                if not self._is_printable_string("conversions", v[0]):
                    raise ValueError(
                        f"conversion column name must be a printable string, but is {v[0]}"
                    )
                if v[1] is not None:
                    if not self._is_callable("conversions", v[1]):
                        raise ValueError(
                            f"conversion encode function must be callable, but is {type(v[1])}"
                        )
                if v[2] is not None:
                    if not self._is_callable("conversions", v[2]):
                        raise ValueError(
                            f"conversion decode function must be callable, but is {type(v[2])}"
                        )
            else:
                if not self._is_callable("conversions", v):
                    raise ValueError(f"conversion must be callable, but is {type(v)}")
        self._conversions = value

    @property
    def create_db(self) -> bool:
        """Get the create_db."""
        return self._create_db

    @create_db.setter
    def create_db(self, value: bool) -> None:
        """Create the database."""
        if not self._is_bool("create_db", value):
            raise ValueError(f"create_db must be a bool, but is {type(value)}")
        self._create_db = value

    @property
    def create_table(self) -> bool:
        """Get the create_table."""
        return self._create_table

    @create_table.setter
    def create_table(self, value: bool) -> None:
        """Create the table."""
        if not self._is_bool("create_table", value):
            raise ValueError(f"create_table must be a bool, but is {type(value)}")
        self._create_table = value

    @property
    def data_file_folder(self) -> str:
        """Get the data_file_folder."""
        return self._data_file_folder

    @data_file_folder.setter
    def data_file_folder(self, value: str) -> None:
        """The data file folder."""
        if not self._is_path("data_file_folder", value):
            raise ValueError(f"data_file_folder must be a path, but is {value}")
        if not self._is_length("data_file_folder", value, 0, 1024):
            raise ValueError(
                f"data_file_folder length must be between 0 and 1024, but is {len(value)}"
            )
        self._data_file_folder = expanduser(normpath(value))

    @property
    def data_files(self) -> list[str]:
        """Get the data_files."""
        return self._data_files

    @data_files.setter
    def data_files(self, value: list[str]) -> None:
        """The data files."""
        if not self._is_list("data_files", value):
            raise ValueError(f"data_files must be a list, but is {type(value)}")
        for v in value:
            if not self._is_filename("data_files", v):
                raise ValueError(f"data_files value must be a filename, but is {v}")
        self._data_files = value

    @property
    def database(self) -> DatabaseConfig:
        """Get the database."""
        return self._database

    @database.setter
    def database(self, value: DatabaseConfig | dict[str, Any]) -> None:
        """Normalized DB configuration."""
        if isinstance(value, dict):
            value = DatabaseConfig(**value)
        if not self._is_instance("database", value, DatabaseConfig):
            raise ValueError(f"database must be a DatabaseConfig, but is {type(value)}")
        self._database = value

    @property
    def delete_db(self) -> bool:
        """Get the delete_db."""
        return self._delete_db

    @delete_db.setter
    def delete_db(self, value: bool) -> None:
        """Delete the database."""
        if not self._is_bool("delete_db", value):
            raise ValueError(f"delete_db must be a bool, but is {type(value)}")
        self._delete_db = value

    @property
    def delete_table(self) -> bool:
        """Get the delete_table."""
        return self._delete_table

    @delete_table.setter
    def delete_table(self, value: bool) -> None:
        """Delete the table."""
        if not self._is_bool("delete_table", value):
            raise ValueError(f"delete_table must be a bool, but is {type(value)}")
        self._delete_table = value

    @property
    def ptr_map(self) -> PtrMap:
        """Get the ptr_map."""
        return self._ptr_map

    @ptr_map.setter
    def ptr_map(self, value: PtrMap) -> None:
        """Pointer map."""
        if not self._is_dict("ptr_map", value):
            raise ValueError(f"ptr_map must be a dict, but is {type(value)}")
        for k, v in value.items():
            if not self._is_printable_string("ptr_map", k):
                raise ValueError(f"ptr_map key must be a printable string, but is {k}")
            if not self._is_printable_string("ptr_map", v):
                raise ValueError(f"ptr_map value must be a printable string, but is {v}")
            if not self._is_length("ptr_map", k, 1, 64):
                raise ValueError(f"ptr_map key length must be between 1 and 64, but is {len(k)}")
            if not self._is_length("ptr_map", v, 1, 64):
                raise ValueError(f"ptr_map value length must be between 1 and 64, but is {len(v)}")
        self._ptr_map = value

    @property
    def schema(self) -> TableSchema:
        """Get the schema."""
        return self._schema

    @schema.setter
    def schema(self, value: TableSchema | dict[str, dict[str, Any]]) -> None:
        """Table schema."""
        if not self._is_dict("schema", value):
            raise ValueError(f"schema must be a dict, but is {type(value)}")
        _value: TableSchema = {}
        for k, v in value.items():
            _value[k] = ColumnSchema(**v) if isinstance(v, dict) else v
        self._schema = _value

    @property
    def table(self) -> str:
        """Get the table."""
        return self._table

    @table.setter
    def table(self, value: str) -> None:
        """The table name."""
        if not self._is_printable_string("table", value):
            raise ValueError(f"table must be a printable string, but is {value}")
        if not self._is_length("table", value, 1, 64):
            raise ValueError(f"table length must be between 1 and 64, but is {len(value)}")
        self._table = value

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

    def verify(self) -> None:
        """Check the table configuration."""
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
            if not (self.create_table or self.wait_for_table):
                raise ValueError("Delete DB requires create table or wait for table.")
        if self.delete_table:
            if not self.create_table:
                raise ValueError("Delete table requires create table.")
            if self.wait_for_table:
                raise ValueError("Delete table requires wait for table to be False.")
        if not (not (self.create_db and self.wait_for_db)):
            # Original: self.value_error(not (self.create_db and self.wait_for_db), "Create DB requires wait for DB to be False.")
            raise ValueError("Create DB requires wait for DB to be False.")
        if not (not (self.create_table and self.wait_for_table)):
            # Original: self.value_error(not (self.create_table and self.wait_for_table), "Create table requires wait for table to be False.")
            raise ValueError("Create table requires wait for table to be False.")
        super().verify()

    @property
    def wait_for_db(self) -> bool:
        """Get the wait_for_db."""
        return self._wait_for_db

    @wait_for_db.setter
    def wait_for_db(self, value: bool) -> None:
        """Wait for the database."""
        if not self._is_bool("wait_for_db", value):
            raise ValueError(f"wait_for_db must be a bool, but is {type(value)}")
        self._wait_for_db = value

    @property
    def wait_for_table(self) -> bool:
        """Get the wait_for_table."""
        return self._wait_for_table

    @wait_for_table.setter
    def wait_for_table(self, value: bool) -> None:
        """Wait for the table."""
        if not self._is_bool("wait_for_table", value):
            raise ValueError(f"wait_for_table must be a bool, but is {type(value)}")
        self._wait_for_table = value
