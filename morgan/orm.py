from abc import ABC
from typing import Any, Type, TypeVar, Union

from morgan.connection import DatabaseConnection, SQLiteConnection

T = TypeVar('T', bound='Model')


class QueryBuilder:
    def __init__(self, model: Type[T]):
        self.model = model
        self.filters = []
        self.exclusions = []
        self.or_conditions = []


    def where(self, **conditions) -> "QueryBuilder":
        self.filters.append(("AND", conditions))

        return self

    def and_where(self, **conditions) -> "QueryBuilder":
        return self.where(**conditions)

    def or_where(self, **conditions) -> "QueryBuilder":
        self.or_conditions.append(conditions)

        return self

    def where_not(self, **conditions) -> "QueryBuilder":
        self.exclusions.append(conditions)

        return self

    def all(self) -> list[T]:
        where_clause, params = self._build_query()
        query = f"SELECT * FROM {self.model.table}"

        if where_clause:
            query += f" WHERE {where_clause}"

        print(query)

        with self.model.db:
            rows = self.model.db.fetch_all(query=query, params=params)
            return [self.model(**row) for row in rows]

    def first(self) -> Union[T, None]:
        where_clause, params = self._build_query()
        query = f"SELECT * FROM {self.model.table}"

        if where_clause:
            query += f" WHERE {where_clause}"
        query += " LIMIT 1"

        with self.model.db:
            row = self.model.db.fetch_one(query=query, params=params)
            if row:
                return self.model(**row)

            return None

    def _build_query(self) -> str:
        where_clauses = []
        params = []

        # Normal conditions
        for i, (logic, conditions) in enumerate(self.filters):
            clause = " AND ".join(f"{key} = ?" for key in conditions.keys())
            if i == 0:
                where_clauses.append(f"({clause})")
            else:
                where_clauses.append(f"{logic} ({clause})")

            params.extend(conditions.values())

        # Exclusions
        for conditions in self.exclusions:
            clause = " AND ".join(f"{key} != ?"for key in conditions.keys())
            where_clauses.append(f"AND ({clause})")

            params.extend(conditions.values())

        # Or conditions
        if self.or_conditions:
            or_clauses = []

            for conditions in self.or_conditions:
                clause = " OR ".join(f"{key} = ?" for key in conditions.keys())
                or_clauses.append(f"({clause})")
                params.extend(conditions.values())

            if where_clauses:
                where_clauses.append(f"AND ({' OR '.join(or_clauses)})")
            else:
                where_clauses.append(f"({' OR '.join(or_clauses)})")

        where_clause = " ".join(where_clauses)

        return where_clause, params


class Model(ABC):
    """Base model class"""
    connection: dict[str, Any] = {}
    attributes: dict[str, Any] = {}
    table: str = None
    db: DatabaseConnection

    # ==========================================================================
    # Section for class methods
    # ==========================================================================
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
    def get_by_id(cls: Type[T], id: Any) -> Union[T, None]:
        with cls.db:
            query = f"SELECT * FROM {cls.table} WHERE id = ?"
            row = cls.db.fetch_one(query=query, params=(id,))

            if row:
                return cls(**row)

            return None

    @classmethod
    def where(cls: Type[T], **kwargs) -> QueryBuilder:
        return QueryBuilder(cls).where(**kwargs)

    @classmethod
    def and_where(cls: Type[T], **kwargs) -> QueryBuilder:
        return QueryBuilder(cls).where(**kwargs)

    @classmethod
    def or_where(cls: Type[T], **kwargs) -> QueryBuilder:
        return QueryBuilder(cls).or_where(**kwargs)

    @classmethod
    def where_not(cls: Type[T], **kwargs) -> QueryBuilder:
        return QueryBuilder(cls).where_not(**kwargs)

    @classmethod
    def all(cls: Type[T], ** kwargs) -> list[T]:
        return QueryBuilder(cls).all()

    @classmethod
    def first(cls: Type[T], ** kwargs) -> T:
        return QueryBuilder(cls).first()


    # ==========================================================================
    # Section for instance methods
    # ==========================================================================
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

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
