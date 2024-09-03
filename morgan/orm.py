"""
Morgan ORM Module

This module includes classes for building queries like such as `SQLQueryBuilder`
and `QueryBuilder`. Also, it contains the base class for model creation.
"""

from abc import ABC
from typing import Any, TypeVar, Union

from morgan.connection import DatabaseConnection, SQLiteConnection, ConnectionType, DatabaseConfig

T = TypeVar('T', bound='Model')


class SQLQueryBuilder(ABC):

    def __init__(self, table: str):
        self.__table = table
        self.__columns = []
        self.__values = []
        self.__where = []
        self.__order_by = []
        self.__limit = None
        self.__offset = None
        self.__params: list[Any] = []

        self._operation = "SELECT"
        self.__set_clause: Union[str, None] = None

    def select(self, *columns: str) -> "SQLQueryBuilder":
        self._operation = "SELECT"
        self.__columns.extend(columns)

        return self

    def insert(self, **kwargs) -> "SQLQueryBuilder":
        self._operation = "INSERT"
        self.__columns = list(kwargs.keys())
        self.__values = list(kwargs.values())
        self.__params = self.__values

        return self

    def insert_many(self, records: list[dict[str, Any]]) -> "SQLQueryBuilder":
        if not records:
            raise ValueError("No records provided for insert_many")

        self._operation = "INSERT"
        self.__columns = list(records[0].keys())

        values = []
        for record in records:
            if set(record.keys()) != set(self.__columns):
                raise ValueError("All records must have the same columns")
            values.extend(record.values())

        self.__params = values

        return self

    def update(self, set_clause: str, *params: Any) -> "SQLQueryBuilder":
        self._operation = "UPDATE"
        self.__set_clause = set_clause
        self.__params = list(params) + self.__params

        return self

    def delete(self) -> "SQLQueryBuilder":
        self._operation = "DELETE"

        return self

    def where(self, condition: str, *params: Any) -> "SQLQueryBuilder":
        self.__where.append(condition)
        self.__params.extend(params)

        return self

    def order_by(self, column: str, direction: str = "ASC") -> "SQLQueryBuilder":
        self.__order_by.append(f"{column} {direction}")

        return self

    def limit(self, limit: int) -> "SQLQueryBuilder":
        self.__limit = limit

        return self

    def offset(self, offset: int) -> "SQLQueryBuilder":
        self.__offset = offset

        return self

    def get_query(self) -> tuple[str, list[Any]]:
        if self._operation == "SELECT":
            columns = ", ".join(self.__columns) if self.__columns else "*"
            query = f"SELECT {columns} FROM {self.__table}"
        elif self._operation == "UPDATE":
            if not self.__set_clause:
                raise ValueError("No SET clause provided for the UPDATE operation.")
            query = f"UPDATE {self.__table} SET {self.__set_clause}"
        elif self._operation == "DELETE":
            query = f"DELETE FROM {self.__table}"
        elif self._operation == "INSERT":
            columns = ", ".join(self.__columns)
            placeholders = ", ".join(["?" for _ in self.__columns])
            query = f"INSERT INTO {self.__table} ({columns}) VALUES "
            query += ", ".join([f"({placeholders})" for _ in range(len(self.__params) // len(self.__columns))])
        else:
            raise ValueError(f"Unsupported operation: {self._operation}")

        if self.__where:
            query += f" WHERE {" AND ".join(self.__where)}"

        if self.__order_by and self._operation == "SELECT":
            query += f" ORDER BY {", ".join(self.__order_by)}"

        if self.__limit is not None and self._operation == "SELECT":
            query += f" LIMIT {self.__limit}"

        if self.__offset is not None and self._operation == "SELECT":
            query += f" OFFSET {self.__offset}"

        return query, self.__params


class QueryBuilder(SQLQueryBuilder):
    def __init__(self, table: str, model: type[T] = None, db_connection: DatabaseConnection = None):
        super().__init__(table)

        self.__model = model
        self.__db = db_connection

    def get(self) -> list[T]:
        query, params = self.get_query()

        with self.__db:
            rows = self.__db.fetch_all(query=query, params=params)

        return [self.__model(**row) for row in rows]

    def exec(self) -> None:
        if self._operation not in ["INSERT", "UPDATE", "DELETE"]:
            raise ValueError("exec() can only be used with UPDATE or DELETE operations.")

        query, params = self.get_query()

        with self.__db:
            self.__db.execute(query=query, params=params)


class Model(ABC):
    table: str = None
    db_config: DatabaseConfig = None
    attributes: dict[str, Any] = {}
    primary_key: str = "id"

    __db: DatabaseConnection

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)


        if cls.db_config.connector == ConnectionType.SQLite:
            cls.__db = SQLiteConnection(database=cls.db_config.database_url)

    @classmethod
    def create_one(cls: type[T], **kwargs) -> T:
        QueryBuilder(cls.table, db_connection=cls.__db).insert(**kwargs).exec()

        last_id = cls.__db.get_last_inserted_id()
        instance = cls(**kwargs)

        if last_id and cls.primary_key:
            setattr(instance, cls.primary_key, last_id)

        return instance

    @classmethod
    def create_many(cls: type[T], records: list[dict[str, Any]]) -> Union[int, None]:
        if not records:
            return None

        QueryBuilder(cls.table, db_connection=cls.__db).insert_many(records).exec()

        return len(records)

    @classmethod
    def query(cls: type[T]) -> QueryBuilder:
        return QueryBuilder(cls.table, cls, cls.__db)

    @classmethod
    def where(cls: type[T], condition: str, *params: Any) -> QueryBuilder:
        return cls.query().where(condition, *params)

    @classmethod
    def all(cls: type[T]) -> list[T]:
        with cls.__db:
            query, params = QueryBuilder(cls.table).get_query()
            rows = cls.__db.fetch_all(query=query, params=params)

            return [cls(**row) for row in rows]

    @classmethod
    def get_by_pk(cls: type[T], pk: Any) -> Union[T, None]:
        with cls.__db:
            query, params = QueryBuilder(cls.table) \
                .where(f"{cls.primary_key} = ?", pk) \
                .limit(1) \
                .get_query()

            row = cls.__db.fetch_one(query=query, params=params)

            if row:
                return cls(**row)

            return None

    def save(self) -> None:
        if hasattr(self, self.primary_key) and getattr(self, self.primary_key):
            set_clause = ", ".join([f"{key} = ?" for key in self.__dict__ if key != self.primary_key])
            params = [value for key, value in self.__dict__.items() if key != self.primary_key]

            pk_value = getattr(self, self.primary_key)

            QueryBuilder(self.table, db_connection=self.__db) \
                .where(f"{self.primary_key} = ?", pk_value) \
                .update(set_clause, *params) \
                .exec()
        else:
            columns = ", ".join(self.__dict__.keys())
            placeholders = ", ".join(["?" for _ in self.__dict__.keys()])
            params = list(self.__dict__.values())

            query = f"INSERT INTO {self.table} ({columns}) VALUES ({placeholders})"
            with self.__db:
                self.__db.execute(query, params)

            if self.primary_key in self.__dict__:
                setattr(self, self.primary_key, self.__db.get_last_inserted_id())

    def delete(self) -> None:
        if hasattr(self, self.primary_key) and getattr(self, self.primary_key):
            QueryBuilder(self.table, db_connection=self.__db) \
                .where(f"{self.primary_key} = ?", getattr(self, self.primary_key)) \
                .delete() \
                .exec()
        else:
            raise ValueError("Cannot delete a record without a primary key.")