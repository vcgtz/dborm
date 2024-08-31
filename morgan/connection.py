from abc import ABC, abstractmethod
from typing import Any, Union
import sqlite3

from morgan.exceptions import ConnectionError, DisconnectionError, QueryExecutionError


class DatabaseConnection(ABC):
    """Abstract class for database connections."""

    @abstractmethod
    def connect(self) -> None:
        """Connect to the database."""

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the database."""

    @abstractmethod
    def execute(self, query: str, params: Union[dict[str, Any], None] = None) -> None:
        """Execute a query on the database."""

    @abstractmethod
    def fetch_one(self, query: str, params: Union[dict[str, Any], None] = None) -> Union[dict[str, Any], None]:
        """Fetch one row from the database."""

    @abstractmethod
    def fetch_all(self, query: str, params: Union[dict[str, Any], None] = None) -> list[dict[str, Any]]:
        """Fetch all rows from the database."""


class SQLiteConnection(DatabaseConnection):
    """SQLite database connection."""

    def __init__(self, database: str) -> None:
        self._database = database
        self._connection: Union[sqlite3.Connection, None] = None

    def connect(self) -> None:
        try:
            self._connection = sqlite3.connect(self._database)
            self._connection.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            raise ConnectionError(f"Failed to connect to the database: {e}") from e

    def disconnect(self) -> None:
        try:
            self._connection.close()
        except sqlite3.Error as e:
            raise DisconnectionError(f"Failed to disconnect from database: {e}") from e

    def execute(self, query: str, params: Union[dict[str, Any], None] = None) -> None:
        if not self._connection:
            raise ConnectionError("No active database connection")

        try:
            cursor = self._connection.cursor()
            cursor.execute(query, params or {})
            self._connection.commit()
        except sqlite3.Error as e:
            raise QueryExecutionError(f"Query execution failed: {e}") from e

    def fetch_one(self, query: str, params: Union[dict[str, Any], None] = None) -> Union[dict[str, Any], None]:
        if not self._connection:
            raise ConnectionError("No active database connection")

        try:
            cursor = self._connection.cursor()
            cursor.execute(query, params or {})
            row = cursor.fetchone()

            if row:
                return dict(row)

            return None
        except sqlite3.Error as e:
            raise QueryExecutionError(f"Query execution failed: {e}") from e

    def fetch_all(self, query: str, params: Union[dict[str, Any], None] = None) -> list[dict[str, Any]]:
        if not self._connection:
            raise ConnectionError("No active database connection")

        try:
            cursor = self._connection.cursor()
            cursor.execute(query, params or {})

            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise QueryExecutionError(f"Query execution failed: {e}") from e
