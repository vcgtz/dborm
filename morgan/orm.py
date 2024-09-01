"""
Morgan ORM Module

This module includes classes for buiding queries like such as `SQLQueryBuilder`
and `QueryBuilder`. Also, it containes the base clase for model creation.
"""

from abc import ABC
from typing import Any, TypeVar, Union

from morgan.connection import DatabaseConnection, SQLiteConnection


T = TypeVar('T', bound='Model')


class SQLQueryBuilder(ABC):
    """
    A base class for constructing SQL queries.

    This class provides methods to build SQL queries by specifying columns,
    conditions, ordering, limits, and offsets. The queries are generated as
    strings that can be executed by a database connection.

    Attributes:
        `__table` (str): The name of the table to query.
        `__columns` (list[str]): The columns to be selected in the query.
        `__where` (list[str]): The WHERE conditions for the query.
        `__order_by` (list[str]): The ORDER BY clauses for the query.
        `__limit` (int): The LIMIT clause for the query.
        `__offset` (int): The OFFSET clause for the query.
        `__params` (list[Any]): The parameters to be used in the query conditions.
    """

    def __init__(self, table: str):
        """
        Initializes the `SQLQueryBuilder` with the name of the table to query.

        Args:
            `table` (str): The name of the table to perform the query on.
        """

        self.__table = table
        self.__columns = []
        self.__where = []
        self.__order_by = []
        self.__limit = None
        self.__offset = None
        self.__params: list[Any] = []

    def select(self, *columns: str) -> "SQLQueryBuilder":
        """
        Specifies the columns to be selected in the query.

        Args:
            `columns` (str): The names of the columns to select.

        Returns:
            `SQLQueryBuilder`: The instance of the query builder.
        """
        self.__columns.extend(columns)

        return self

    def where(self, condition: str, *params: Any) -> "SQLQueryBuilder":
        """
        Adds a WHERE condition to the query.

        Args:
            `condition` (str): The condition string for the WHERE clause.
            `params` (Any): The parameters to be used in the condition.

        Returns:
            `SQLQueryBuilder`: The instance of the query builder.
        """
        self.__where.append(condition)
        self.__params.extend(params)

        return self

    def order_by(self, column: str, direction: str = "ASC") -> "SQLQueryBuilder":
        """
        Adds an ORDER BY clause to the query.

        Args:
            `column` (str): The column to order by.
            `direction` (str, optional): The direction of sorting, either "ASC" (default) or "DESC".

        Returns:
            `SQLQueryBuilder`: The instance of the query builder.
        """
        self.__order_by.append(f"{column} {direction}")

        return self

    def limit(self, limit: int) -> "SQLQueryBuilder":
        """
        Sets the LIMIT clause for the query.

        Args:
            `limit` (int): The maximum number of rows to return.

        Returns:
            `SQLQueryBuilder`: The instance of the query builder.
        """
        self.__limit = limit

        return self

    def offset(self, offset: int) -> "SQLQueryBuilder":
        """
        Sets the OFFSET clause for the query.

        Args:
            `offset` (int): The number of rows to skip before starting to return rows.

        Returns:
            `SQLQueryBuilder`: The instance of the query builder.
        """
        self.__offset = offset

        return self

    def get_query(self) -> tuple[str, list[Any]]:
        """
        Generates the SQL query string and the corresponding parameters.

        Returns:
            `tuple[str, list[Any]]`: A tuple containing the SQL query string and the list of parameters.
        """
        columns = ", ".join(self.__columns) if self.__columns else "*"
        query = f"SELECT {columns} FROM {self.__table}"

        if self.__where:
            query += f" WHERE {" AND ".join(self.__where)}"

        if self.__order_by:
            query += f" ORDER BY {", ".join(self.__order_by)}"

        if self.__limit:
            query += f" LIMIT {self.__limit}"

        if self.__offset:
            query += f" OFFSET {self.__offset}"

        return query, self.__params


class QueryBuilder(SQLQueryBuilder):
    """
    Extends `SQLQueryBuilder` to execute SQL queries and return model instances.

    This class adds the functionality to execute the SQL queries generated
    by `SQLQueryBuilder` and return the results as instances of a specified
    model class. It handles the database connection and the instantiation
    of model objects from the query results.

    Attributes:
        `__model` (Type[T]): The model class to instantiate for each result row.
        `__db` (DatabaseConnection): The database connection to use for executing the query.
    """

    def __init__(self, table: str, model: type[T] = None, db_connection: DatabaseConnection = None):
        """
        Initializes the QueryBuilder with a model class and a database connection.

        Args:
            `table` (str): The name of the table to perform the query on.
            `model` (Type[T], optional): The model class to instantiate for each result row. Defaults to None.
            `db_connection` (DatabaseConnection, optional): The database connection to use for executing the query. Defaults to None.
        """
        super().__init__(table)

        self.__model = model
        self.__db = db_connection

    def get(self) -> list[T]:
        """
        Executes the SQL query and returns the result as a list of model instances.

        This method runs the SQL query generated by `SQLQueryBuilder`, fetches
        the results from the database, and instantiates the specified model
        class for each row in the result set.

        Returns:
            `list[T]`: A list of instances of the model class, each representing a row in the result set.
        """
        query, params = self.get_query()

        with self.__db:
            rows = self.__db.fetch_all(query=query, params=params)

        return [self.__model(**row) for row in rows]


class Model(ABC):
    """
    Base model class providing common functionality for ORM models.

    This class serves as the base class for all models in the ORM. It provides
    methods to query the database, retrieve records, and instantiate model
    objects from database rows. Each model should inherit from this class and
    specify its corresponding database table, primary key, and connection settings.

    Attributes:
        `table` (str): The name of the database table associated with the model.
        `connection` (dict[str, Any]): The database connection configuration.
        `attributes` (dict[str, Any]): The attributes and their values for an instance of the model.
        `primary_key` (str): The name of the primary key column. Defaults to "id".
        `__db` (DatabaseConnection): The database connection object.
    """
    table: str = None
    connection: dict[str, Any] = {}
    attributes: dict[str, Any] = {}
    primary_key: str = "id"

    __db: DatabaseConnection

    def __init__(self, **kwargs):
        """
        Initializes a new instance of the model with the provided attributes.

        This constructor sets the attributes of the model instance using the
        keyword arguments provided.

        Args:
            `**kwargs`: Arbitrary keyword arguments representing model attributes.
        """
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __init_subclass__(cls, **kwargs) -> None:
        """
        Initializes a subclass of Model.

        This method is automatically called when a new subclass is created. It
        sets up the database connection for the subclass based on its connection
        configuration.

        Args:
            `**kwargs`: Arbitrary keyword arguments.
        """
        super().__init_subclass__(**kwargs)

        cls.connection = {
            "connector": "sqlite",
            "database": "development.db"
        }

        if cls.connection.get("connector") == "sqlite":
            cls.__db = SQLiteConnection(database=cls.connection.get("database"))

    @classmethod
    def query(cls: type[T]) -> QueryBuilder:
        """
        Returns a `QueryBuilder` instance for the model's table.

        This method initializes a `QueryBuilder` configured to operate on the
        model's associated table.

        Returns:
            `QueryBuilder`: A new QueryBuilder instance for the model's table.
        """
        return QueryBuilder(cls.table, cls, cls.__db)

    @classmethod
    def where(cls: type[T], condition: str, *params: Any) -> QueryBuilder:
        """
        Starts a query with a WHERE clause.

        This method begins a new query by adding a WHERE clause with the specified
        condition and parameters.

        Args:
            `condition` (str): The condition for the WHERE clause.
            `*params` (Any): The parameters to bind to the condition.

        Returns:
            `QueryBuilder`: The QueryBuilder instance with the applied condition.
        """
        return cls.query().where(condition, *params)

    @classmethod
    def all(cls: type[T]) -> list[T]:
        """
        Retrieves all records from the model's table.

        This method queries the model's table and returns all records as instances
        of the model.

        Returns:
            `list[T]`: A list of model instances representing all records in the table.
        """
        with cls.__db:
            query, params = QueryBuilder(cls.table).get_query()
            rows = cls.__db.fetch_all(query=query, params=params)

            return [cls(**row) for row in rows]

    @classmethod
    def get_by_pk(cls: type[T], pk: Any) -> Union[T, None]:
        """
        Retrieves a single record by its primary key.

        This method fetches a single record from the model's table using the
        specified primary key. If the record is found, it is returned as an
        instance of the model. Otherwise, None is returned.

        Args:
            `pk` (Any): The primary key value to search for.

        Returns:
            `Union[T, None]`: An instance of the model if found, otherwise None.
        """
        with cls.__db:
            query, params = QueryBuilder(cls.table) \
                .where(f"{cls.primary_key} = ?", pk) \
                .limit(1) \
                .get_query()

            row = cls.__db.fetch_one(query=query, params=params)

            if row:
                return cls(**row)

            return None
