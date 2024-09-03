"""
Morgan ORM Exception Module
"""

class MorganError(Exception):
    pass


class ConnectionError(MorganError):
    pass


class QueryExecutionError(MorganError):
    pass


class DisconnectionError(MorganError):
    pass


class TransactionError(MorganError):
    pass