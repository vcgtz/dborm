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
    SQLite = "sqlite"
    MySQL = "mysql"
    MariaDB = "mariadb"
    PostgreSQL = "postgresql"


class DatabaseConfig:
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
        self.database = database
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.connector = connector
        self.database_url = database_url


class DatabaseConnection(ABC):

    @abstractmethod
    def connect(self) -> None:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @abstractmethod
    def execute(self, query: str, params: Union[dict[str, Any], None] = None) -> None:
        pass

    @abstractmethod
    def fetch_one(self, query: str, params: Union[dict[str, Any], None] = None) -> Union[dict[str, Any], None]:
        pass

    @abstractmethod
    def fetch_all(self, query: str, params: Union[dict[str, Any], None] = None) -> list[dict[str, Any]]:
        pass



class SQLiteConnection(DatabaseConnection):

    def __init__(self, database: str) -> None:
        self.__database = database
        self.__connection: Union[sqlite3.Connection, None] = None

    def __enter__(self):
        self.connect()

        return self

    def __exit__(self, type, value, traceback):
        self.disconnect()

    def connect(self) -> None:
        try:
            self.__connection = sqlite3.connect(self.__database)
            self.__connection.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            raise ConnectionError(f"Failed to connect to the database: {e}") from e

    def disconnect(self) -> None:
        if self.__connection is None:
            return

        try:
            self.__connection.close()
        except sqlite3.Error as e:
            raise DisconnectionError(f"Failed to disconnect from database: {e}") from e
        finally:
            self.__connection = None

    def execute(self, query: str, params: Union[dict[str, Any], None] = None) -> None:
        if not self.__connection:
            raise ConnectionError("No active database connection")

        try:
            cursor = self.__connection.cursor()
            cursor.execute(query, params or {})
            self.__connection.commit()
        except sqlite3.Error as e:
            raise QueryExecutionError(f"Query execution failed: {e}") from e

    def fetch_one(self, query: str, params: Union[dict[str, Any], None] = None) -> Union[dict[str, Any], None]:
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
        if not self.__connection:
            raise ConnectionError("No active database connection")

        try:
            cursor = self.__connection.cursor()
            cursor.execute(query, params or {})

            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise QueryExecutionError(f"Query execution failed: {e}") from e
