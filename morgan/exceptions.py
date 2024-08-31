class MorganError(Exception):
    """Base class for all Morgan exceptions."""

class ConnectionError(MorganError):
    """Raised when a connection to the database cannot be established or is lost."""


class QueryExecutionError(MorganError):
    """Raised when a query execution fails."""


class DisconnectionError(MorganError):
    """Raised when a connection cannot be closed."""


class TransactionError(MorganError):
    """Raised when a transaction cannot be committed or rolled back."""
