from contextlib import contextmanager
import os
import sqlite3


class DatabaseIntegrityError(Exception):
    pass


class _PostgresConnection:
    def __init__(self, connection, psycopg):
        self._connection = connection
        self._psycopg = psycopg

    def execute(self, query, parameters=()):
        query = query.replace("?", "%s")
        try:
            return self._connection.execute(query, parameters)
        except self._psycopg.IntegrityError as error:
            raise DatabaseIntegrityError from error


def is_postgres(database_target):
    return database_target.startswith(("postgres://", "postgresql://"))


@contextmanager
def connect(database_target):
    if is_postgres(database_target):
        import psycopg
        from psycopg.rows import dict_row

        database_url = database_target.replace("postgres://", "postgresql://", 1)
        try:
            with psycopg.connect(database_url, row_factory=dict_row) as connection:
                yield _PostgresConnection(connection, psycopg)
        except psycopg.IntegrityError as error:
            raise DatabaseIntegrityError from error
        return

    os.makedirs(os.path.dirname(database_target) or ".", exist_ok=True)
    connection = sqlite3.connect(database_target)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        with connection:
            yield connection
    finally:
        connection.close()


@contextmanager
def transaction(database_target):
    try:
        with connect(database_target) as connection:
            yield connection
    except sqlite3.IntegrityError as error:
        raise DatabaseIntegrityError from error
