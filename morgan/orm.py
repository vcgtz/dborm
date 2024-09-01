from abc import ABC
from typing import Any, Type, TypeVar, Union

from morgan.connection import DatabaseConnection, SQLiteConnection

T = TypeVar('T', bound='Model')


class Model(ABC):
    """Base model class"""
    connection: dict[str, Any] = {}
    attributes: dict[str, Any] = {}
    table: str = None
    db: DatabaseConnection

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)

        cls.connection = {
            "connector": "sqlite",
            "database": "development.db"
        }

        if cls.connection.get("connector") == "sqlite":
            cls.db = SQLiteConnection(database=cls.connection.get("database"))

    @classmethod
    def create_one(cls: Type[T], **kwargs) -> T:
        """Create one single record for the model"""
        instance = cls(**kwargs)
        instance.save()

        return instance

    @classmethod
    def get_all(cls: Type[T]) -> list[T]:
        """Get all records"""
        with cls.db:
            query = f"SELECT * FROM {cls.table}"
            rows = cls.db.fetch_all(query=query)

            if len(rows) == 0:
                return []

            return [cls(**row) for row in rows]

    @classmethod
    def get_by_id(cls: Type[T], id: Any) -> Union[T, None]:
        with cls.db:
            query = f"SELECT * FROM {cls.table} WHERE id = ?"
            row = cls.db.fetch_one(query=query, params=(id,))

            if row:
                return cls(**row)

            return None

    def save(self) -> None:
        """Save into the database the current record"""
        with self.db:
            columns = ", ".join(self.__dict__.keys())
            placeholders = ", ".join("?" * len(self.__dict__))
            query = f"INSERT INTO {self.table} ({columns}) VALUES ({placeholders})"

            self.db.execute(query=query, params=tuple(self.__dict__.values()))

    def delete(self) -> None:
        """Delete from the database the current record"""
        with self.db:
            if not hasattr(self, 'id'):
                raise ValueError("Cannot delete without a primary key.")

            query = f"DELETE FROM {self.table} WHERE id = ?"

            self.db.execute(query=query, params=(self.id,))
