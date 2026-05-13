import sqlite3
from pathlib import Path

from flask import Flask, current_app, g


SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def get_database_path(app: Flask | None = None) -> str:
    flask_app = app or current_app
    return flask_app.config["DATABASE_PATH"]


def get_connection() -> sqlite3.Connection:
    if "database_connection" not in g:
        g.database_connection = sqlite3.connect(get_database_path())
        g.database_connection.row_factory = sqlite3.Row
    return g.database_connection


def close_connection(exception: BaseException | None = None) -> None:
    connection = g.pop("database_connection", None)
    if connection is not None:
        connection.close()


def init_db(app: Flask | None = None) -> None:
    if app is not None:
        database_path = get_database_path(app)
        with sqlite3.connect(database_path) as connection:
            connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        return

    connection = get_connection()
    connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
