"""Unit tests for the database.py module."""

from unittest import TestCase
from unittest.mock import patch
from copy import deepcopy
from itertools import count
from threading import get_ident

from psycopg2 import OperationalError, ProgrammingError, errors, sql

from egppy.storage.store.database import database
from egppy.storage.store.database.common import backoff_generator
from egppy.storage.store.database.database import (
    _clean_connections,
    _connect_core,
    db_connect,
    db_create,
    db_delete,
    db_disconnect,
    db_disconnect_all,
    db_exists,
    db_reconnect,
    db_transaction,
)
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


_MOCK_CONFIG = {
    "host": "_host",
    "port": "_port",
    "user": "_user",
    "password": "_password",
    "maintenance_db": "_maintenance_db",
    "retries": 100000,
}
_MOCK_DBNAME = "_dbname"
_MOCK_VALUE_1 = 1234
_MOCK_VALUE_2 = 4321
_MOCK_ERROR = 0
_INFINITE_BACKOFFS = 100


class TestDatabase(TestCase):
    """Unit tests for the database.py module."""

    @patch("egppy.storage.store.database.database.connect")
    def test_connect_core_p0(self, mock_connect) -> None:
        """Positive path for _connection_core()."""
        db_disconnect_all()

        class MockConnection:
            """Mock connection class."""

            def __init__(self) -> None:
                """Initialize the connection."""
                self.value = _MOCK_VALUE_1

            def close(self) -> None:
                """Close the connection."""
                self.value = None

        mock_connect.return_value = MockConnection()
        self.assertEqual(
            _connect_core(_MOCK_DBNAME, _MOCK_CONFIG)[0].value, _MOCK_VALUE_1  # type: ignore
        )

    @patch("egppy.storage.store.database.database.connect")
    def test_connect_core_n0(self, mock_connect) -> None:
        """Raise an OperationalError in _connection_core()."""
        db_disconnect_all()

        class MockConnection:
            """Mock connection class that raises OperationalError on initialization."""

            def __init__(self, *_, **__) -> None:
                """Initialize the connection and raise OperationalError."""
                self.value = None
                raise OperationalError

            def close(self) -> None:
                """Close the connection."""
                self.value = None

        mock_connect.side_effect = MockConnection
        self.assertIsNone(_connect_core(_MOCK_DBNAME, _MOCK_CONFIG)[0])

    @patch("egppy.storage.store.database.database.connect")
    def test_db_reconnect_p0(self, mock_connect):
        """Reconnect to the DB with no initial connection."""
        db_disconnect_all()

        class MockConnection:
            """Mock connection class for testing."""

            def __init__(self, *_, **__) -> None:
                """Initialize the connection."""
                self.value = _MOCK_VALUE_1

            def close(self) -> None:
                """Close the connection."""
                self.value = None

            def open(self) -> None:
                """Open the connection."""
                self.value = _MOCK_VALUE_1

        mock_connect.return_value = MockConnection()
        self.assertEqual(
            db_reconnect(_MOCK_DBNAME, _MOCK_CONFIG).value, _MOCK_VALUE_1  # type: ignore
        )

    @patch("egppy.storage.store.database.database.connect")
    def test_db_reconnect_p1(self, mock_connect):
        """Reconnect to the DB with a pre-existing connection."""
        db_disconnect_all()

        def mock_values_iter():
            yield _MOCK_VALUE_1
            yield _MOCK_VALUE_2

        mock_values = mock_values_iter()

        class MockConnection:
            """Mock connection class for testing."""

            def __init__(self) -> None:
                """Initialize the connection."""
                try:
                    self.value = next(mock_values)
                except StopIteration:
                    self.value = None

            def close(self) -> None:
                """Close the connection."""
                self.value = None

            def open(self) -> None:
                """Open the connection."""
                self.value = _MOCK_VALUE_1

        mock_connect.return_value = MockConnection()
        with patch.dict(
            database._connections,  # pylint: disable=protected-access
            {_MOCK_CONFIG["host"]: {_MOCK_DBNAME: {get_ident(): MockConnection()}}},
            clear=True,
        ):
            self.assertEqual(
                db_reconnect(_MOCK_DBNAME, _MOCK_CONFIG).value, _MOCK_VALUE_2  # type: ignore
            )

    def test_db_reconnect_n0(self, monkeypatch):
        """Pre-existing connection close() raises an OperationalError."""
        db_disconnect_all()

        def mock_values_iter():
            yield _MOCK_VALUE_1
            yield _MOCK_VALUE_2

        mock_values = mock_values_iter()

        class MockConnection:
            """Mock connection class for testing."""

            def __init__(self) -> None:
                """Initialize the connection."""
                try:
                    self.value = next(mock_values)
                except StopIteration:
                    self.value = None

            def close(self) -> None:
                """Close the connection and raise OperationalError."""
                raise OperationalError

            def open(self) -> None:
                """Open the connection."""
                self.value = _MOCK_VALUE_1

        def mock_connect(*_, **__) -> MockConnection:
            """Mock connect function."""
            return MockConnection()

        monkeypatch.setattr(database, "connect", mock_connect)
        monkeypatch.setitem(
            database._connections,  # pylint: disable=protected-access
            _MOCK_CONFIG["host"],
            {_MOCK_DBNAME: {get_ident(): MockConnection()}},
        )
        assert db_reconnect(_MOCK_DBNAME, _MOCK_CONFIG).value == _MOCK_VALUE_2  # type: ignore

    def test_db_reconnect_n1(self, monkeypatch):
        """Connection raises OperationalError.

        There is a pre-existing connection.
        The pre-existing connection is successfully closed.
        The 1st reconnection attempt raises an OperationalError.
        The 2nd reconnection attempt succeeds.

        db_reconnect should return the second successful connection after
        one backoff.
        """
        db_disconnect_all()

        def _connection_iter():
            for i in (_MOCK_VALUE_1, _MOCK_ERROR, _MOCK_VALUE_2):
                yield i

        mock_values = _connection_iter()
        sleep_duration = 0.0  # pylint: disable=redefined-outer-name

        class MockConnection:
            """Mock connection class for testing."""

            def __init__(self) -> None:
                """Initialize the connection."""
                try:
                    self.value = next(mock_values)
                except StopIteration:
                    self.value = None
                if self.value == _MOCK_ERROR:
                    raise OperationalError

            def close(self) -> None:
                """Close the connection."""
                self.value = None

        def mock_connect() -> MockConnection:
            """Mock connect function."""
            return MockConnection()

        def mock_sleep(backoff: float) -> None:
            """Mock sleep function."""
            global sleep_duration  # pylint: disable=global-variable-undefined
            sleep_duration += backoff

        monkeypatch.setattr(database, "connect", mock_connect)
        monkeypatch.setattr(database, "sleep", mock_sleep)
        try:
            backoff = next(backoff_generator(fuzz=False))
        except StopIteration:
            backoff = 0
        monkeypatch.setitem(
            database._connections,  # pylint: disable=protected-access
            _MOCK_CONFIG["host"],
            {_MOCK_DBNAME: {get_ident(): MockConnection()}},
        )
        assert db_reconnect(_MOCK_DBNAME, _MOCK_CONFIG).value == _MOCK_VALUE_2  # type: ignore
        assert backoff >= sleep_duration / 1.1 and backoff <= sleep_duration / 0.9

    def test_db_reconnect_n2(self, monkeypatch):
        """Check infinite backoff.

        There is a pre-existing connection.
        The pre-existing connection is successfully closed.
        The _INFINITE_BACKOFFS reconnection attempts raises an OperationalError.
        The _INFINITE_BACKOFFS+1 reconnection attempt succeeds.

        db_reconnect should return the second successful connection after
        _INFINITE_BACKOFFS backoffs.
        """
        db_disconnect_all()

        def _connection_iter():
            connections = [_MOCK_VALUE_1]
            connections.extend([_MOCK_ERROR] * _INFINITE_BACKOFFS)
            connections.append(_MOCK_VALUE_2)
            for i in connections:
                yield i

        mock_values = _connection_iter()
        global sleep_duration  # pylint: disable=global-variable-undefined
        sleep_duration = 0.0

        class MockConnection:
            """Mock connection class for testing."""

            def __init__(self) -> None:
                """Initialize the connection."""
                try:
                    self.value = next(mock_values)
                except StopIteration:
                    self.value = None
                if self.value == _MOCK_ERROR:
                    raise OperationalError

            def close(self) -> None:
                """Close the connection."""
                self.value = None

            def open(self) -> None:
                """Open the connection."""
                self.value = _MOCK_VALUE_1

        def mock_connect(*_, **__):
            """Mock connect function."""
            return MockConnection()

        def mock_sleep(backoff):
            """Mock sleep function."""
            global sleep_duration  # pylint: disable=global-variable-undefined
            sleep_duration += backoff

        monkeypatch.setattr(database, "connect", mock_connect)
        monkeypatch.setattr(database, "sleep", mock_sleep)
        monkeypatch.setitem(
            database._connections,  # pylint: disable=protected-access
            _MOCK_CONFIG["host"],
            {_MOCK_DBNAME: {get_ident(): MockConnection()}},
        )
        backoff_gen = backoff_generator(fuzz=False)
        try:
            total_backoff = sum((next(backoff_gen) for _ in range(_INFINITE_BACKOFFS)))
        except StopIteration:
            total_backoff = 0
        assert db_reconnect(_MOCK_DBNAME, _MOCK_CONFIG).value == _MOCK_VALUE_2  # type: ignore
        assert total_backoff >= sleep_duration / 1.1 and total_backoff <= sleep_duration / 0.9

    def test_db_reconnect_n3(self, monkeypatch):
        """Check error after all retries.

        There is a pre-existing connection.
        The pre-existing connection is successfully closed.
        The new connection errors.
        The number of retries is configured to 0 i.e. no try.
        """
        db_disconnect_all()

        def _connection_iter():
            connections = [_MOCK_VALUE_1]
            connections.append(_MOCK_ERROR)
            connections.append(_MOCK_VALUE_2)
            for i in connections:
                yield i

        mock_values = _connection_iter()

        class MockConnection:
            """Mock connection class for testing."""

            def __init__(self) -> None:
                """Initialize the connection."""
                try:
                    self.value = next(mock_values)
                except StopIteration:
                    self.value = None
                if self.value == _MOCK_ERROR:
                    raise OperationalError

            def close(self) -> None:
                """Close the connection."""
                self.value = None

            def open(self) -> None:
                """Open the connection."""
                self.value = _MOCK_VALUE_1

        def mock_connect(*_, **__) -> MockConnection:
            """Mock connect function."""
            return MockConnection()

        monkeypatch.setattr(database, "connect", mock_connect)
        monkeypatch.setitem(
            database._connections,  # pylint: disable=protected-access
            _MOCK_CONFIG["host"],
            {_MOCK_DBNAME: {get_ident(): MockConnection()}},
        )
        config = deepcopy(_MOCK_CONFIG)
        config["retries"] = 0
        try:
            db_reconnect(_MOCK_DBNAME, config)
        except OperationalError:
            pass
        else:
            assert False

    def test_db_connect_p0(self, monkeypatch):
        """No pre-existing connection test for db_connect()."""
        db_disconnect_all()

        class MockConnection:
            """Mock connection class for testing."""

            def __init__(self) -> None:
                """Initialize the connection."""
                self.value = _MOCK_VALUE_1

            def close(self) -> None:
                """Close the connection."""
                self.value = None

        def mock_connect(*_, **__) -> MockConnection:
            """Mock connect function."""
            return MockConnection()

        monkeypatch.setattr(database, "connect", mock_connect)
        assert db_connect(_MOCK_DBNAME, _MOCK_CONFIG).value == _MOCK_VALUE_1  # type: ignore

    def test_db_connect_p1(self, monkeypatch):
        """With pre-existing connection test for db_connect()."""
        db_disconnect_all()

        def mock_values_iter():
            yield _MOCK_VALUE_1
            yield _MOCK_VALUE_2

        mock_values = mock_values_iter()

        class MockConnection:
            """Mock connection class for testing."""

            def __init__(self) -> None:
                """Initialize the connection."""
                try:
                    self.value = next(mock_values)
                except StopIteration:
                    self.value = None

            def close(self) -> None:
                """Close the connection."""
                self.value = None

            def open(self) -> None:
                """Open the connection."""
                self.value = _MOCK_VALUE_1

        def mock_connect(*_, **__) -> MockConnection:
            """Mock connect function."""
            return MockConnection()

        monkeypatch.setattr(database, "connect", mock_connect)
        assert db_connect(_MOCK_DBNAME, _MOCK_CONFIG).value == _MOCK_VALUE_1  # type: ignore
        assert db_connect(_MOCK_DBNAME, _MOCK_CONFIG).value == _MOCK_VALUE_1  # type: ignore

    def test_db_disconnect_p0(self, monkeypatch):
        """Create a connection and then disconnect it.

        Connection should be closed.
        A new connection should be a new connection object.
        """
        db_disconnect_all()

        def mock_values_iter():
            yield _MOCK_VALUE_1
            yield _MOCK_VALUE_2

        mock_values = mock_values_iter()

        class MockConnection:
            """Mock connection class for testing."""

            def __init__(self) -> None:
                """Initialize the connection."""
                try:
                    self.value = next(mock_values)
                except StopIteration:
                    self.value = None

            def close(self) -> None:
                """Close the connection."""
                self.value = None

            def open(self) -> None:
                """Open the connection."""
                self.value = _MOCK_VALUE_1

        def mock_connect(*_, **__):
            """Mock connect function."""
            return MockConnection()

        monkeypatch.setattr(database, "connect", mock_connect)
        connection = db_connect(_MOCK_DBNAME, _MOCK_CONFIG)
        assert connection.value == _MOCK_VALUE_1  # type: ignore
        db_disconnect(_MOCK_DBNAME, _MOCK_CONFIG)
        assert connection.value is None  # type: ignore
        assert db_connect(_MOCK_DBNAME, _MOCK_CONFIG).value == _MOCK_VALUE_2  # type: ignore

    def test_db_disconnect_n0(self, monkeypatch):
        """Create a connection and then disconnect it with an OperationalError on close().

        A new connection should be a new connection object.
        """
        db_disconnect_all()

        def mock_values_iter():
            yield _MOCK_VALUE_1
            yield _MOCK_VALUE_2

        mock_values = mock_values_iter()

        class MockConnection:
            """Mock connection class for testing."""

            def __init__(self) -> None:
                """Initialize the connection."""
                try:
                    self.value = next(mock_values)
                except StopIteration:
                    self.value = None

            def close(self) -> None:
                """Close the connection."""
                self.value = None

            def open(self) -> None:
                """Open the connection."""
                self.value = _MOCK_VALUE_1

        def mock_connect(*_, **__):
            """Mock connect function."""
            return MockConnection()

        monkeypatch.setattr(database, "connect", mock_connect)
        assert db_connect(_MOCK_DBNAME, _MOCK_CONFIG).value == _MOCK_VALUE_1  # type: ignore
        db_disconnect(_MOCK_DBNAME, _MOCK_CONFIG)
        assert db_connect(_MOCK_DBNAME, _MOCK_CONFIG).value == _MOCK_VALUE_2  # type: ignore

    def test_db_transaction_p0(self, monkeypatch):
        """Execute a read-only SQL statement.

        A single cursor should be returned.
        """
        db_disconnect_all()
        mock_connection_ref = count()
        mock_cursor_ref = count()

        class MockCursor:
            """Mock cursor class for testing."""

            def __init__(self) -> None:
                """Initialize the cursor."""
                try:
                    self.value = next(mock_cursor_ref)
                except StopIteration:
                    self.value = None

            def execute(self, sql_str):
                """Execute a SQL statement."""

            def fetchone(self):
                """Fetch one result."""
                return self.value

        class MockConnection:
            """Mock connection class for testing."""

            def __init__(self) -> None:
                """Initialize the connection."""
                try:
                    self.value = next(mock_connection_ref)
                except StopIteration:
                    self.value = None

            def cursor(self, *_, **__) -> MockCursor:
                """Return a new cursor."""
                return MockCursor()

            def close(self):
                """Close the connection."""
                self.value = None

        def mock_connect(*_, **__) -> MockConnection:
            """Mock connect function."""
            return MockConnection()

        monkeypatch.setattr(database, "connect", mock_connect)
        dbcur = db_transaction(_MOCK_DBNAME, _MOCK_CONFIG, ("SQL0",))
        assert not dbcur.fetchone()

    def test_db_transaction_p1(self, monkeypatch):
        """Test that a write transaction is committed."""
        db_disconnect_all()

        class MockCursor:
            """Mock cursor class for testing."""

            def __init__(self) -> None:
                """Initialize the cursor."""
                self.value = 2

            def execute(self, sql_str):
                """Execute a SQL statement."""

            def fetchone(self):
                """Fetch one result."""
                return self.value

        class MockConnection:
            """Mock connection class for testing."""

            def __init__(self) -> None:
                """Initialize the connection."""
                self.value = 2
                self.committed = False

            def close(self) -> None:
                """Close the connection."""
                self.value = None

            def cursor(self) -> MockCursor:
                """Return a new cursor."""
                self.committed = False
                return MockCursor()

            def commit(self) -> None:
                """Commit the transaction."""
                self.committed = True

        def mock_connect(*_, **__) -> MockConnection:
            """Mock connect function."""
            return MockConnection()

        monkeypatch.setattr(database, "connect", mock_connect)
        dbcur = db_transaction(_MOCK_DBNAME, _MOCK_CONFIG, "SQL0", read=False)
        assert dbcur.fetchone() == 2
        assert db_connect(_MOCK_DBNAME, _MOCK_CONFIG).commit

    def test_db_transaction_n4(self) -> None:
        """All reconnection attempts fail and a ProgrammingError is raised."""
        try:
            db_transaction(_MOCK_DBNAME, _MOCK_CONFIG, ("SQL0",), recons=0)
        except ProgrammingError:
            pass
        else:
            assert False

    def test_db_exists_p0(self, monkeypatch):
        """Test the case when the DB exists."""
        db_disconnect_all()
        mock_connection_ref = count()

        class MockCursor:
            """Mock cursor class for testing."""

            def __init__(self) -> None:
                """Initialize the cursor."""
                self.value = (_MOCK_DBNAME,)

            def __iter__(self):
                return self

            def __next__(self):
                """Return the next value or stop iteration."""
                if self.value is not None:
                    tmp = self.value
                    self.value = None
                    return tmp
                raise StopIteration

            def execute(self, sql_str):
                """Execute a SQL statement."""

        class MockConnection:
            """Mock connection class for testing."""

            def __init__(self) -> None:
                """Initialize the connection."""
                try:
                    self.value = next(mock_connection_ref)
                except StopIteration:
                    self.value = None

            def cursor(self) -> MockCursor:
                """Return a new cursor."""
                return MockCursor()

            def close(self):
                """Close the connection."""
                self.value = None

        def mock_connect() -> MockConnection:
            """Mock connect function."""
            return MockConnection()

        def mock_as_string():
            """Mock as_string function."""
            return "SQL string"

        monkeypatch.setattr(database, "connect", mock_connect)
        monkeypatch.setattr(sql.SQL, "as_string", mock_as_string)
        assert db_exists(_MOCK_DBNAME, _MOCK_CONFIG)

    def test_db_exists_p1(self, monkeypatch) -> None:
        """Test the case when the DB does not exist."""
        db_disconnect_all()
        mock_connection_ref = count()
        # mock_cursor_ref = count()

        class MockCursor:
            """Mock cursor class for testing."""

            def __init__(self) -> None:
                """Initialize the cursor."""
                self.value = (_MOCK_DBNAME,)

            def __iter__(self):
                return self

            def __next__(self):
                """Return the next value or stop iteration."""
                if self.value is not None:
                    tmp = self.value
                    self.value = None
                    return tmp
                raise StopIteration

            def execute(self, sql_str):
                """Execute a SQL statement."""

        class MockConnection:
            """Mock connection class for testing."""

            def __init__(self) -> None:
                """Initialize the connection."""
                try:
                    self.value = next(mock_connection_ref)
                except StopIteration:
                    self.value = None

            def cursor(self):
                """Return a new cursor."""
                return MockCursor()

            def close(self):
                """Close the connection."""
                self.value = None

        def mock_connect():
            """Mock connect function."""
            return MockConnection()

        def mock_as_string():
            """Mock as_string function."""
            return "SQL string"

        monkeypatch.setattr(database, "connect", mock_connect)
        monkeypatch.setattr(sql.SQL, "as_string", mock_as_string)
        assert not db_exists("Does not exist", _MOCK_CONFIG)

    def test_db_exists_n0(self, monkeypatch):
        """Test the case when the maintenance DB connection raises an error."""
        db_disconnect_all()

        def mock_db_connect(*_, **__):
            raise ProgrammingError

        def mock_as_string(*_, **__):
            return "SQL string"

        monkeypatch.setattr(database, "db_connect", mock_db_connect)
        monkeypatch.setattr(sql.SQL, "as_string", mock_as_string)
        try:
            db_exists(_MOCK_DBNAME, _MOCK_CONFIG)
        except ProgrammingError:
            pass
        else:
            assert False

    def test_db_exists_n1(self, monkeypatch):
        """Test the case when the maintenance DB connection raises InsufficientPrivilege."""
        db_disconnect_all()
        pgerr = deepcopy(ProgrammingError)
        pgerr.pgcode = errors.InsufficientPrivilege  # pylint: disable=no-member # type: ignore

        def mock_db_connect(*_, **__):
            raise pgerr

        def mock_as_string(*_, **__):
            return "SQL string"

        monkeypatch.setattr(database, "db_connect", mock_db_connect)
        monkeypatch.setattr(sql.SQL, "as_string", mock_as_string)
        assert db_exists(_MOCK_DBNAME, _MOCK_CONFIG)

    def test_db_create_p0(self, monkeypatch):
        """Create a DB."""
        db_disconnect_all()
        mock_connection_ref = count()
        mock_cursor_ref = count()

        class MockCursor:
            """Mock cursor class for testing."""

            def __init__(self) -> None:
                """Initialize the cursor."""
                try:
                    self.value = next(mock_cursor_ref)
                except StopIteration:
                    self.value = None

            def execute(self, sql_str) -> None:
                """Execute a SQL statement."""

        class MockConnection:
            """Mock connection class for testing."""

            def __init__(self) -> None:
                """Initialize the connection."""
                try:
                    self.value = next(mock_connection_ref)
                except StopIteration:
                    self.value = None
                self.autocommit = False

            def cursor(self, *_, **__) -> MockCursor:
                """Return a new cursor."""
                return MockCursor()

            def commit(self) -> None:
                """Commit the transaction."""

            def close(self) -> None:
                """Close the connection."""
                self.value = None

        def mock_connect(*_, **__) -> MockConnection:
            """Mock connect function."""
            return MockConnection()

        def mock_as_string(*_, **__) -> str:
            """Mock as_string function."""
            return "SQL string"

        monkeypatch.setattr(database, "connect", mock_connect)
        monkeypatch.setattr(sql.Composed, "as_string", mock_as_string)
        db_create(_MOCK_DBNAME, _MOCK_CONFIG)

    def test_db_delete_p0(self, monkeypatch):
        """Delete a DB."""
        db_disconnect_all()
        mock_connection_ref = count()
        mock_cursor_ref = count()

        class MockCursor:
            """Mock cursor class for testing."""

            def __init__(self) -> None:
                """Initialize the cursor."""
                try:
                    self.value = next(mock_cursor_ref)
                except StopIteration:
                    self.value = None

            def execute(self, sql_str) -> None:
                """Execute a SQL statement."""

        class MockConnection:
            """Mock connection class for testing."""

            def __init__(self) -> None:
                """Initialize the connection."""
                try:
                    self.value = next(mock_connection_ref)
                except StopIteration:
                    self.value = None
                self.autocommit = False

            def cursor(self) -> MockCursor:
                """Return a new cursor."""
                return MockCursor()

            def commit(self) -> None:
                """Commit the transaction."""

            def close(self) -> None:
                """Close the connection."""
                self.value = None

        def mock_connect(*_, **__) -> MockConnection:
            """Mock connect function."""
            return MockConnection()

        def mock_as_string(*_, **__) -> str:
            """Mock as_string function."""
            return "SQL string"

        monkeypatch.setattr(database, "connect", mock_connect)
        monkeypatch.setattr(sql.Composed, "as_string", mock_as_string)
        db_delete(_MOCK_DBNAME, _MOCK_CONFIG)

    def test_clean_connections_p0(self, monkeypatch):
        """Add a connection, fake a closed thread and make sure it is removed."""
        db_disconnect_all()

        class MockConnection:
            """Mock connection class for testing."""

            def __init__(self) -> None:
                """Initialize the connection."""
                self.value = _MOCK_VALUE_1

            def close(self) -> None:
                """Close the connection."""
                self.value = None

            def open(self) -> None:
                """Open the connection."""
                self.value = _MOCK_VALUE_1

        def mock_connect() -> MockConnection:
            """Mock connect function."""
            return MockConnection()

        monkeypatch.setattr(database, "connect", mock_connect)
        db_connect(_MOCK_DBNAME, _MOCK_CONFIG)

        #  pylint: disable=protected-access
        monkeypatch.setitem(
            database._connections,
            _MOCK_CONFIG["host"],
            {_MOCK_DBNAME: {1234: None}},
        )
        _clean_connections()
        assert database._connections[_MOCK_CONFIG["host"]][_MOCK_DBNAME].get(1234, None) is None

    def test_clean_connections_n0(self, monkeypatch):
        """Add a connection, fake a closed thread and make sure it is removed."""
        db_disconnect_all()

        class MockConnection:
            """Mock connection class for testing."""

            def __init__(self) -> None:
                self.value = _MOCK_VALUE_1

            def close(self) -> None:
                """Close the connection."""
                raise ProgrammingError

        def mock_connect(*_, **__) -> MockConnection:
            """Mock connect function."""
            return MockConnection()

        monkeypatch.setattr(database, "connect", mock_connect)
        db_connect(_MOCK_DBNAME, _MOCK_CONFIG)

        #  pylint: disable=protected-access
        monkeypatch.setitem(
            database._connections,
            _MOCK_CONFIG["host"],
            {_MOCK_DBNAME: {1234: MockConnection()}},
        )
        _clean_connections()
        assert (
            database._connections[_MOCK_CONFIG["host"]][_MOCK_DBNAME][1234].value == _MOCK_VALUE_1
        )
