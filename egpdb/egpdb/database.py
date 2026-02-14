"""postgresql database management.

Only one connection per database is maintained following the design principle
of a single threaded process.
"""

# TODO: Look into VACUUM & ANALYZE  pylint: disable=fixme
# See https://bbengfort.github.io/2017/12/psycopg2-transactions/


from copy import deepcopy
from random import choice
from string import ascii_letters
from threading import enumerate as thread_enumerate
from threading import get_ident
from time import sleep
from typing import Any, Generator

from psycopg2 import InterfaceError, OperationalError, ProgrammingError, connect, errors, sql
from psycopg2.extensions import cursor as TupleCursor
from psycopg2.extensions import register_adapter
from psycopg2.extras import DictCursor, Json, NamedTupleCursor, register_default_json, register_uuid

from egpcommon.egp_log import Logger, egp_logger
from egpcommon.text_token import TextToken, register_token_code
from egpdb.common import backoff_generator

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


# psycopg2 registrations
register_uuid()
register_default_json()
register_adapter(dict, Json)


# Global connection tracking
# {host: {dbname: {thread_ident: connection | None}}}
_connections: dict[str, dict[str, dict[int, Any]]] = {}


register_token_code(
    "W04000",
    "Backing off connection re-attempt {attempts} for database {dbname}"
    " with config {config} for {backoff} seconds.",
)
register_token_code(
    "W04001",
    "Unable to connect to database {dbname} with config {config}. Error: {error}.",
)
register_token_code(
    "W04002",
    "Transaction attempt {attempt} of {total}: Unable to {rw} database"
    " {dbname} with error code: {code} error: {error}.",
)
register_token_code(
    "W04003",
    "{attempts} transactions failed. Dropping database {dbname}"
    " connection and re-establishing. {reconnection} of {total}.",
)
register_token_code(
    "W04004",
    "Insufficient privileges for user {user} to read maintenance DB {mdb}. Assuming {db} exists.",
)
register_token_code(
    "W04005",
    "Failed to close connection to database {dbname} on host {host}"
    " created by terminated thread {ident}. Error: {error}",
)
register_token_code(
    "W04006",
    "Failed to close connection to database {dbname} on host {host}. Error: {error}",
)
register_token_code(
    "E04000",
    "Transaction cannot complete to database {dbname}. See previous log lines for details.",
)
register_token_code("I04000", "Connected to postgresql database {dbname} with config {config}.")
register_token_code("I04001", "Database {dbname} with config {config} {exists} exist.")
register_token_code("I04002", "Database {dbname} with config {config} created.")
register_token_code("I04003", "Database {dbname} with config {config} deleted.")


def cursor_name_generator() -> Generator[str, Any, None]:
    """Generate a unique name for every cursor."""
    count = 0
    while True:
        yield _CURSOR_NAME_PREFIX + str(count)
        count += 1


_CURSOR_NAME: Generator[str, Any, None] = cursor_name_generator()
_ITERSIZE = 10000
_CURSOR_NAME_PREFIX: str = "".join(choice(ascii_letters) for i in range(8)) + "_"
_INITIAL_DELAY = 0.125
_BACKOFF_STEPS = 13
_BACKOFF_FUZZ = True
_DB_TRANSACTION_ATTEMPTS = 3
_DB_RECONNECTIONS = 3
_DB_EXISTS_SQL = sql.SQL("SELECT datname FROM pg_database")
_DB_CREATE_SQL = sql.SQL("CREATE DATABASE {}")
_DB_DELETE_SQL = sql.SQL("DROP DATABASE IF EXISTS {}")
_CTYPE: dict[str, Any] = {
    "tuple": TupleCursor,
    "namedtuple": NamedTupleCursor,
    "dict": DictCursor,
}


def _clean_connections() -> None:
    """If threads no longer exist close any connections they may have had."""
    idents: list[int | None] = [
        thread.ident for thread in (x for x in thread_enumerate() if x is not None)
    ]
    for host, dbs in _connections.items():
        for dbname, threads in dbs.items():
            for ident, connection in tuple(threads.items()):
                if ident not in idents:
                    try:
                        if connection is not None:
                            connection.close()
                    except (ProgrammingError, OperationalError, InterfaceError) as exc:
                        _logger.warning(
                            TextToken(
                                {
                                    "W04005": {
                                        "host": host,
                                        "dbname": dbname,
                                        "ident": ident,
                                        "error": str(exc),
                                    }
                                }
                            )
                        )
                    else:
                        del threads[ident]


def _connect_core(dbname: str, config: dict[str, Any]) -> tuple[Any | None, Exception | None]:
    """Connect to the specified database.

    Internal function to make one attempt at a connection to
    the specified database.

    Args
    ----
    dbname: Name of the database to connect to.
    config: Database server details. Must have keys:
        'host' (str): Fully qualified host name of the DB server.
        'port' (int): Port to access database server on.
        'user' (str): Username to login with.
        'password' (str): Password to login with.

    Returns
    -------
    A tuple of (connection, error) where connection is a psycopg2
    connection object or None on failure, and error is the exception
    that occurred or None on success.
    """
    host = config["host"]
    port = config["port"]
    user = config["user"]
    password = config["password"]
    err = None
    connection = None
    try:
        # deepcode ignore MissingClose: Code design to keep connection open
        connection = connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=dbname,
            connect_timeout=2,
        )
    except (InterfaceError, OperationalError) as exc:
        connection = None
        _logger.warning(
            TextToken({"W04001": {"dbname": dbname, "config": config, "error": (err := exc)}})
        )
    else:
        err = None
        _logger.info(TextToken({"I04000": {"dbname": dbname, "config": config}}))
    return connection, err


def _get_connection(dbname: str, host: str) -> Any:
    dbs = _connections.setdefault(host, {})
    threads = dbs.setdefault(dbname, {})
    return threads.setdefault(get_ident(), None)


def db_connect(dbname: str, config: dict[str, Any]) -> Any:
    """Connect to the specified database.

    If a connection already exists then it is reused. If not a new one is created
    and returned.

    Args
    ----
    dbname: Name of the database to connect to.
    config: Database server details. Must have keys:
        'host' (str): Fully qualified host name of the DB server.
        'port' (int): Port to access database server on.
        'user' (str): Username to login with.
        'password' (str): Password to login with.

    Returns
    -------
    A psycopg2 connection object with an open connection.
    """
    connection = _get_connection(dbname, config["host"])
    if connection is None:
        connection = db_reconnect(dbname, config)
        _connections[config["host"]][dbname][get_ident()] = connection
        _clean_connections()
    return connection


def db_create(dbname: str, config: dict[str, Any]) -> None:
    """Connect to the maintenance database to create dbname.

    The connection to the maintenance DB is closed after dbname
    is created.

    Args
    ----
    dbname: Name of the database to create.
    config: Database server details. Must have keys:
        'host' (str): Fully qualified host name of the DB server.
        'port' (int): Port to access database server on.
        'user' (str): Username to login with for maintenance DB.
        'password' (str): Password to login with for maintenance DB.
        'maintenance_db' (str): Name of the maintenance DB.
    """
    sql_str = _DB_CREATE_SQL.format(sql.Identifier(dbname))
    connection = db_connect(config["maintenance_db"], config)
    connection.autocommit = True
    _logger.info(sql_str.as_string(connection))
    db_transaction(config["maintenance_db"], config, sql_str, read=False, recons=1)
    _logger.info(TextToken({"I04002": {"dbname": config["maintenance_db"], "config": config}}))
    db_disconnect(config["maintenance_db"], config)


def db_delete(dbname: str, config: dict[str, Any]) -> None:
    """Connect to the maintenance database to delete dbname.

    The connection to the maintenance DB is closed after dbname
    is deleted.

    Args
    ----
    dbname: Name of the database to delete.
    config: Database server details. Must have keys:
        'host' (str): Fully qualified host name of the DB server.
        'port' (int): Port to access database server on.
        'user' (str): Username to login with for maintenance DB.
        'password' (str): Password to login with for maintenance DB.
        'maintenance_db' (str): Name of the maintenance DB.
    """
    sql_str = _DB_DELETE_SQL.format(sql.Identifier(dbname))
    db_disconnect(dbname, config)
    connection = db_connect(config["maintenance_db"], config)
    connection.autocommit = True
    _logger.info(sql_str.as_string(connection))
    db_transaction(config["maintenance_db"], config, sql_str, read=False, recons=1)
    _logger.info(TextToken({"I04003": {"dbname": dbname, "config": config}}))
    db_disconnect(config["maintenance_db"], config)


def db_disconnect(dbname: str, config: dict[str, Any]) -> None:
    """Disconnect from the specified database.

    If a connection does not exist this function is a no-op.

    Args
    ----
    dbname: Name of the database to disconnect from.
    config: Database server details. Must have keys:
        'host' (str): Fully qualified host name of the DB server.
    """
    connection = _get_connection(dbname, config["host"])
    if connection is not None:
        try:
            connection.close()
        except (InterfaceError, OperationalError, ProgrammingError) as exc:
            _logger.warning(
                TextToken(
                    {
                        "W04006": {
                            "host": config["host"],
                            "dbname": dbname,
                            "error": str(exc),
                        }
                    }
                )
            )
        else:
            _connections[config["host"]][dbname][get_ident()] = None


def db_disconnect_all() -> None:
    """Disconnect all connections.

    Iterates over all tracked connections, closes them, and
    clears all internal state from the _connections dict.
    """
    for host, db_dict in tuple(_connections.items()):
        for dbname in db_dict.keys():
            db_disconnect(dbname, {"host": host})
        del _connections[host]


def db_exists(dbname: str, config: dict[str, Any]) -> bool:
    """Connect to the maintenance database to see if dbname exists.

    If the user has insufficient privileges to read from the maintenance
    DB then return True.

    The connection to the maintenance DB is closed after the existence of
    dbname is determined.

    Args
    ----
    dbname: Name of the database to check for existence.
    config: Database server details. Must have keys:
        'host' (str): Fully qualified host name of the DB server.
        'port' (int): Port to access database server on.
        'user' (str): Username to login with for maintenance DB.
        'password' (str): Password to login with for maintenance DB.
        'maintenance_db' (str): Name of the maintenance DB.

    Returns
    -------
    True if dbname exists, False otherwise.
    """
    try:
        connection = db_connect(config["maintenance_db"], config)
    except ProgrammingError as exc:
        if exc.pgcode == errors.InsufficientPrivilege:  # pylint: disable=no-member
            _logger.warning(
                TextToken(
                    {
                        "W04004": {
                            "user": config["user"],
                            "mdb": config["maintenance_db"],
                            "db": dbname,
                        }
                    }
                )
            )
            return True
        raise exc
    _logger.info(_DB_EXISTS_SQL.as_string(connection))
    retval = (dbname,) in db_transaction(config["maintenance_db"], config, _DB_EXISTS_SQL)
    _logger.info(
        TextToken(
            {
                "I04001": {
                    "dbname": config["maintenance_db"],
                    "config": config,
                    "exists": ("DOES NOT", "DOES")[retval],
                }
            }
        )
    )
    db_disconnect(config["maintenance_db"], config)
    return retval


def db_reconnect(dbname: str, config: dict[str, Any]) -> Any:
    """Reconnect to the specified database.

    If a connection already exists and is open, close it and establish
    a new connection. The new connection is stored for reuse via the
    db_connect() function.
    If a connection cannot be established, step through an increasing
    backoff delay and try again up to config['retries'] attempts.

    Args
    ----
    dbname: Name of the database to connect to.
    config: Database server details. Must have keys:
        'host' (str): Fully qualified host name of the DB server.
        'port' (int): Port to access database server on.
        'user' (str): Username to login with.
        'password' (str): Password to login with.
        'retries' (int): Number of times to retry a failed connection.

    Returns
    -------
    A psycopg2 connection object with an open connection.
    """
    connection = _get_connection(dbname, config["host"])
    if connection is not None:
        db_disconnect(dbname, config)
    backoff_gen = backoff_generator(_INITIAL_DELAY, _BACKOFF_STEPS, _BACKOFF_FUZZ)
    attempts = 0
    connection, error = _connect_core(dbname, config)
    while connection is None and attempts < config["retries"]:
        try:
            backoff = next(backoff_gen)
        except StopIteration:
            break
        attempts += 1
        _logger.warning(
            TextToken(
                {
                    "W04000": {
                        "attempts": attempts,
                        "dbname": dbname,
                        "config": config,
                        "backoff": backoff,
                    }
                }
            )
        )
        sleep(backoff)
        connection, error = _connect_core(dbname, config)
    if error is not None:
        raise error
    if connection is None:
        raise RuntimeError("Something went horribly wrong!")
    _connections[config["host"]][dbname][get_ident()] = connection
    return connection


def db_transaction(
    dbname: str,
    config: dict[str, Any],
    sql_str: Any,
    read: bool = True,
    recons: int = _DB_RECONNECTIONS,
    ctype: str = "tuple",
) -> Any:
    """Execute an SQL statement with retry and reconnection logic.

    If read is False the SQL statement will be committed in a single transaction.
    If an error occurs the transaction will be rolled back.
    If read is True a server-side named cursor is used for efficient iteration.

    If an InterfaceError or OperationalError occurs the transaction will be reattempted
    using backoff for _DB_TRANSACTION_ATTEMPTS attempts. If it is still failing
    the database connection will be re-established and the transaction attempts tried again with
    increasing backoff. The whole process will be done for `recons` reconnections
    after which the caught error is raised.

    Args
    ----
    dbname: Name of the database to connect to.
    config: Database server details. Must have keys:
        'host' (str): Fully qualified host name of the DB server.
        'port' (int): Port to access database server on.
        'user' (str): Username to login with.
        'password' (str): Password to login with.
    sql_str: A valid SQL string or psycopg2 sql.Composed object.
    read: If False transaction will be committed.
    recons: >= 1. The number of reconnection attempts before erroring out.
    ctype: Cursor type - one of 'tuple', 'namedtuple', 'dict'.

    Returns
    -------
    A psycopg2 cursor object.
    """
    token2 = {
        "rw": ("write", "read")[read],
        "dbname": dbname,
        "total": _DB_TRANSACTION_ATTEMPTS,
        "error": None,
    }
    token3 = deepcopy(token2)
    token3["attempts"] = _DB_TRANSACTION_ATTEMPTS
    token3["total"] = recons
    backoff_gen = backoff_generator(_INITIAL_DELAY, _BACKOFF_STEPS, _BACKOFF_FUZZ)
    cursor_type = _CTYPE[ctype]
    for reconnection in range(1, recons + 1):
        for transaction_attempt in range(1, _DB_TRANSACTION_ATTEMPTS + 1):
            token2["attempt"] = transaction_attempt
            connection = db_connect(dbname, config)
            if read:
                try:
                    cursor_name = next(_CURSOR_NAME)
                except StopIteration:
                    _logger.error("Cursor name generator exhausted.")
                    raise
                cursor = connection.cursor(
                    name=cursor_name, cursor_factory=cursor_type, withhold=True
                )
                cursor.itersize = _ITERSIZE
            else:
                cursor = connection.cursor(cursor_factory=cursor_type)
            try:
                cursor.execute(sql_str)
            except (InterfaceError, OperationalError) as exc:
                if not read:
                    connection.rollback()
                token2["code"] = exc.pgcode
                token2["error"] = exc
                _logger.warning(TextToken({"W04002": token2}))
                try:
                    sleep(next(backoff_gen))
                except StopIteration:
                    _logger.error("Backoff generator exhausted.")
                    raise
                break
            connection.commit()
            return cursor
        token3["reconnection"] = reconnection
        _logger.warning(TextToken({"W04003": token3}))
        db_reconnect(dbname, config)
    _logger.error(TextToken({"E04000": {"dbname": dbname}}))
    raise ProgrammingError
