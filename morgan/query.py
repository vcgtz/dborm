from typing import Any


class QueryBuilder:
    """Query Builder"""

    def __init__(self, table: str):
        self.__table = table
        self.__columns = []
        self.__where = []
        self.__order_by = []
        self.__limit = None
        self.__offset = None
        self.__params: list[Any] = []

    def select(self, *columns: str) -> "QueryBuilder":
        self.__columns.extend(columns)

        return self

    def where(self, condition: str, *params: Any) -> "QueryBuilder":
        self.__where.append(condition)
        self.__params.extend(params)

        return self

    def order_by(self, column: str, direction: str = "ASC") -> "QueryBuilder":
        self.__order_by.append(f"{column} {direction}")

        return self

    def limit(self, limit: int) -> "QueryBuilder":
        self.__limit = limit

        return self

    def offset(self, offset: int) -> "QueryBuilder":
        self.__offset = offset

        return self

    def get(self) -> tuple[str, list[Any]]:
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
