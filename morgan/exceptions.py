"""
Morgan ORM Exception Module
"""

class MorganError(Exception):
    """
    Base class for all Morgan exceptions.

    This is the base class for all custom exceptions in the Morgan ORM. All other
    exceptions in the ORM should inherit from this class to ensure consistency
    and proper exception handling.
    """

class ConnectionError(MorganError):
    """
    Raised when a connection to the database cannot be established or is lost.

    This exception is thrown when the ORM is unable to establish a connection
    to the database or if an existing connection is unexpectedly lost.
    """


class QueryExecutionError(MorganError):
    """
    Raised when a query execution fails.

    This exception is raised when an error occurs during the execution of a SQL
    query, such as syntax errors or violations of database constraints.
    """


class DisconnectionError(MorganError):
    """
    Raised when a connection cannot be closed.

    This exception is raised when the ORM fails to properly close a database
    connection, possibly due to an underlying issue with the connection or
    the database server.
    """


class TransactionError(MorganError):
    """
    Raised when a transaction cannot be committed or rolled back.

    This exception is raised when an error occurs during a transaction, such
    as failure to commit or roll back the transaction, potentially leaving
    the database in an inconsistent state.
    """
