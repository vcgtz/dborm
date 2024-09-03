"""
Morgan ORM Database Connection Module

This module provides abstract and concrete classes for managing database
connections within the Morgan ORM. It includes an abstract base class for
defining the interface that all database connections must implement, as well
as a specific implementation for SQLite databases.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Union
import sqlite3

from morgan.exceptions import ConnectionError, DisconnectionError, QueryExecutionError


class ConnectionType(Enum):
    """
    Enum representing different types of database connectors supported by Morgan ORM.

    This enumeration is used to specify the type of database connection that the ORM
    should establish. Each member of the enum corresponds to a supported database type.

    Attributes:
        SQLite: Represents a connection to a SQLite database.
        MySQL: Represents a connection to a MySQL database.
        MariaDB: Represents a connection to a MariaDB database.
        PostgreSQL: Represents a connection to a PostgreSQL database.
    """
    SQLite = "sqlite"
    MySQL = "mysql"
    MariaDB = "mariadb"
    PostgreSQL = "postgresql"


class DatabaseConfig:
    """
    Configuration class for setting up database connections in Morgan ORM.

    This class encapsulates all the necessary information required to establish
    a connection to a database. It supports various database types such as SQLite,
    MySQL, MariaDB, and PostgreSQL. The configuration can be done either through
    individual parameters or using a database URL.

    Attributes:
        `database` (str): The name of the database.
        `username` (str): The username for the database connection (optional for SQLite).
        `password` (str): The password for the database connection (optional for SQLite).
        `host` (str): The hostname or IP address of the database server (optional for SQLite).
        `port` (int): The port number to connect to the database server (optional for SQLite).
        `connector` (ConnectionType): The type of database connector (e.g., SQLite, MySQL).
        `database_url` (str): A complete database URL for connection (overrides other settings if provided).
    """
    database: str
    username: str
    password: str
    host: str
    port: int

    connector: ConnectionType
    database_url: str

    def __init__(
            self,
            database: str = None,
            username: str = None,
            password: str = None,
            host: str = None,
            port: int = None,
            connector: ConnectionType = None,
            database_url: str = None
    ):
        """
        Initializes the `DatabaseConfig` with the given connection details.

        Args:
            `database` (Union[str, None]): The name of the database.
            `username` (Union[str, None]): The username for the database connection.
            `password` (Union[str, None]): The password for the database connection.
            `host` (Union[str, None]): The hostname or IP address of the database server.
            `port` (Union[int, None]): The port number to connect to the database server.
            `connector` (Union[ConnectionType, None]): The type of database connector.
            `database_url` (Union[str, None]): A complete database URL for connection. If provided, this overrides other settings.
        """
        self.database = database
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.connector = connector
        self.database_url = database_url


class DatabaseConnection(ABC):
    """
    Abstract base class for database connections.

    This class defines the required interface for any database connection within
    the Morgan ORM. Subclasses must implement methods to connect and disconnect
    from the database, execute queries, and fetch results.
    """

    @abstractmethod
    def connect(self) -> None:
        """
        Connect to the database.

        This method must be implemented to establish a connection to the database.
        """

    @abstractmethod
    def disconnect(self) -> None:
        """
        Disconnect from the database.

        This method must be implemented to properly close the connection to the database.
        """

    @abstractmethod
    def execute(self, query: str, params: Union[dict[str, Any], None] = None) -> None:
        """
        Execute a query on the database.

        Args:
            `query` (str): The SQL query to be executed.
            `params` (Union[dict[str, Any], None], optional): Parameters to bind to the query. Defaults to None.
        """

    @abstractmethod
    def fetch_one(self, query: str, params: Union[dict[str, Any], None] = None) -> Union[dict[str, Any], None]:
        """
        Fetch one row from the database.

        Args:
            `query` (str): The SQL query to be executed.
            `params` (Union[dict[str, Any], None], optional): Parameters to bind to the query. Defaults to None.

        Returns:
            `Union[dict[str, Any], None]`: A dictionary representing the fetched row, or None if no row is found.
        """

    @abstractmethod
    def fetch_all(self, query: str, params: Union[dict[str, Any], None] = None) -> list[dict[str, Any]]:
        """
        Fetch all rows from the database.

        Args:
            `query` (str): The SQL query to be executed.
            `params` (Union[dict[str, Any], None], optional): Parameters to bind to the query. Defaults to None.

        Returns:
            `list[dict[str, Any]]`: A list of dictionaries, each representing a row from the result set.
        """


class SQLiteConnection(DatabaseConnection):
    """
    SQLite database connection.

    This class provides a concrete implementation of DatabaseConnection for
    SQLite databases. It handles connecting to and disconnecting from an SQLite
    database, as well as executing queries and fetching results.

    Attributes:
        `__database` (str): The path to the SQLite database file.
        `__connection` (Union[sqlite3.Connection, None]): The SQLite connection object.
    """

    def __init__(self, database: str) -> None:
        """
        Initialize the SQLiteConnection with the path to the database file.

        Args:
            `database` (str): The path to the SQLite database file.
        """
        self.__database = database
        self.__connection: Union[sqlite3.Connection, None] = None

    def __enter__(self):
        """
        Enter the runtime context related to this object.

        This method allows the use of the connection within a `with` statement,
        automatically connecting to the database at the beginning of the block.
        """
        self.connect()

        return self

    def __exit__(self, type, value, traceback):
        """
        Exit the runtime context related to this object.

        This method ensures that the connection is properly closed at the end of
        a `with` statement block, even if an exception occurs.
        """
        self.disconnect()

    def connect(self) -> None:
        """
        Connect to the SQLite database.

        This method establishes a connection to the specified SQLite database
        file and sets the row factory to return results as dictionaries.

        Raises:
            `ConnectionError`: If the connection to the database fails.
        """
        try:
            self.__connection = sqlite3.connect(self.__database)
            self.__connection.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            raise ConnectionError(f"Failed to connect to the database: {e}") from e

    def disconnect(self) -> None:
        """
        Disconnect from the SQLite database.

        This method closes the connection to the SQLite database.

        Raises:
            `DisconnectionError`: If the disconnection fails.
        """
        if self.__connection is None:
            return

        try:
            self.__connection.close()
        except sqlite3.Error as e:
            raise DisconnectionError(f"Failed to disconnect from database: {e}") from e
        finally:
            self.__connection = None

    def execute(self, query: str, params: Union[dict[str, Any], None] = None) -> None:
        """
        Execute a SQL query on the SQLite database.

        This method executes a SQL query on the database, committing any changes
        made by the query.

        Args:
            `query` (str): The SQL query to be executed.
            `params` (Union[dict[str, Any], None], optional): Parameters to bind to the query. Defaults to None.

        Raises:
            `ConnectionError`: If there is no active database connection.
            `QueryExecutionError`: If the query execution fails.
        """
        if not self.__connection:
            raise ConnectionError("No active database connection")

        try:
            cursor = self.__connection.cursor()
            cursor.execute(query, params or {})
            self.__connection.commit()
        except sqlite3.Error as e:
            raise QueryExecutionError(f"Query execution failed: {e}") from e

    def fetch_one(self, query: str, params: Union[dict[str, Any], None] = None) -> Union[dict[str, Any], None]:
        """
        Fetch one row from the SQLite database.

        This method executes a SQL query and fetches a single row from the result set.

        Args:
            `query` (str): The SQL query to be executed.
            `params` (Union[dict[str, Any], None], optional): Parameters to bind to the query. Defaults to None.

        Returns:
            `Union[dict[str, Any], None]`: A dictionary representing the fetched row, or None if no row is found.

        Raises:
            `ConnectionError`: If there is no active database connection.
            `QueryExecutionError`: If the query execution fails.
        """
        if not self.__connection:
            raise ConnectionError("No active database connection")

        try:
            cursor = self.__connection.cursor()
            cursor.execute(query, params or {})
            row = cursor.fetchone()

            if row:
                return dict(row)

            return None
        except sqlite3.Error as e:
            raise QueryExecutionError(f"Query execution failed: {e}") from e

    def fetch_all(self, query: str, params: Union[dict[str, Any], None] = None) -> list[dict[str, Any]]:
        """
        Fetch all rows from the SQLite database.

        This method executes a SQL query and fetches all rows from the result set.

        Args:
            `query` (str): The SQL query to be executed.
            `params` (Union[dict[str, Any], None], optional): Parameters to bind to the query. Defaults to None.

        Returns:
            `list[dict[str, Any]]`: A list of dictionaries, each representing a row from the result set.

        Raises:
            `ConnectionError`: If there is no active database connection.
            `QueryExecutionError`: If the query execution fails.
        """
        if not self.__connection:
            raise ConnectionError("No active database connection")

        try:
            cursor = self.__connection.cursor()
            cursor.execute(query, params or {})

            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise QueryExecutionError(f"Query execution failed: {e}") from e
