import sqlite3
from pathlib import Path

from flask import Flask, current_app, g


SCHEMA_PATH = Path(__file__).with_name("schema.sql")
LEADS_ORDER_BY = "ORDER BY created_at DESC, id DESC"
SERVICES_ORDER_BY = "ORDER BY created_at ASC, id ASC"
MESSAGE_EXCERPT_SQL = """
CASE
    WHEN length(trim(coalesce(message, ''))) > 80
        THEN substr(trim(coalesce(message, '')), 1, 80) || '…'
    ELSE trim(coalesce(message, ''))
END
"""
DEMO_SERVICES = (
    {
        "title": "Offer Positioning Sprint",
        "description": "Sharpen the service promise, page structure, and primary CTA before the build starts.",
        "starting_price": "From USD 600",
        "icon": "OP",
    },
    {
        "title": "Premium Landing Build",
        "description": "Design and ship a polished landing page that makes the next step feel easier to take.",
        "starting_price": "From USD 1400",
        "icon": "LB",
    },
    {
        "title": "Conversion Refinement",
        "description": "Tighten copy, hierarchy, and contact flow after the first version is live.",
        "starting_price": "From USD 900",
        "icon": "CR",
    },
)


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
            seed_demo_services_if_empty(connection)
        return

    connection = get_connection()
    connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    seed_demo_services_if_empty(connection)


def seed_demo_services_if_empty(connection: sqlite3.Connection) -> None:
    service_count = connection.execute("SELECT COUNT(*) FROM services").fetchone()[0]
    if service_count:
        return

    connection.executemany(
        """
        INSERT INTO services (title, description, starting_price, icon)
        VALUES (:title, :description, :starting_price, :icon)
        """,
        DEMO_SERVICES,
    )
    connection.commit()


def insert_lead(
    name: str,
    email: str,
    message: str,
    phone: str | None = None,
    service_interest: str | None = None,
) -> int:
    connection = get_connection()
    cursor = connection.execute(
        """
        INSERT INTO leads (name, email, phone, service_interest, message)
        VALUES (?, ?, ?, ?, ?)
        """,
        (name, email, phone, service_interest, message),
    )
    connection.commit()
    return int(cursor.lastrowid)


def list_leads() -> list[sqlite3.Row]:
    connection = get_connection()
    try:
        return connection.execute(
            f"""
            SELECT
                id,
                name,
                email,
                phone,
                service_interest,
                status,
                created_at,
                {MESSAGE_EXCERPT_SQL} AS message_excerpt
            FROM leads
            {LEADS_ORDER_BY}
            """
        ).fetchall()
    except sqlite3.OperationalError as exc:
        if "no such table: leads" not in str(exc).lower():
            raise
        return []


def get_lead_dashboard_summary() -> dict[str, int | str | None]:
    connection = get_connection()
    try:
        summary = connection.execute(
            """
            SELECT
                COUNT(*) AS total_leads,
                SUM(CASE WHEN status = 'nuevo' THEN 1 ELSE 0 END) AS new_leads,
                MAX(created_at) AS latest_created_at
            FROM leads
            """
        ).fetchone()
        latest_lead = connection.execute(
            f"""
            SELECT id
            FROM leads
            {LEADS_ORDER_BY}
            LIMIT 1
            """
        ).fetchone()
    except sqlite3.OperationalError as exc:
        if "no such table: leads" not in str(exc).lower():
            raise
        return {
            "total_leads": 0,
            "new_leads": 0,
            "latest_created_at": None,
            "latest_lead_id": None,
        }

    return {
        "total_leads": int(summary["total_leads"] or 0),
        "new_leads": int(summary["new_leads"] or 0),
        "latest_created_at": summary["latest_created_at"],
        "latest_lead_id": None if latest_lead is None else int(latest_lead["id"]),
    }


def list_recent_leads(limit: int = 3) -> list[sqlite3.Row]:
    connection = get_connection()
    try:
        return connection.execute(
            f"""
            SELECT
                id,
                name,
                email,
                service_interest,
                status,
                created_at,
                {MESSAGE_EXCERPT_SQL} AS message_excerpt
            FROM leads
            {LEADS_ORDER_BY}
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    except sqlite3.OperationalError as exc:
        if "no such table: leads" not in str(exc).lower():
            raise
        return []


def get_lead(lead_id: int) -> sqlite3.Row | None:
    connection = get_connection()
    try:
        return connection.execute(
            """
            SELECT id, name, email, phone, service_interest, message, status, created_at
            FROM leads
            WHERE id = ?
            """,
            (lead_id,),
        ).fetchone()
    except sqlite3.OperationalError as exc:
        if "no such table: leads" not in str(exc).lower():
            raise
        return None


def list_services(include_inactive: bool = False) -> list[sqlite3.Row]:
    connection = get_connection()
    where_clause = "" if include_inactive else "WHERE is_active = 1"
    try:
        return connection.execute(
            f"""
            SELECT id, title, description, starting_price, icon, is_active, created_at
            FROM services
            {where_clause}
            {SERVICES_ORDER_BY}
            """
        ).fetchall()
    except sqlite3.OperationalError as exc:
        if "no such table: services" not in str(exc).lower():
            raise
        return []


def get_service(service_id: int) -> sqlite3.Row | None:
    connection = get_connection()
    try:
        return connection.execute(
            """
            SELECT id, title, description, starting_price, icon, is_active, created_at
            FROM services
            WHERE id = ?
            """,
            (service_id,),
        ).fetchone()
    except sqlite3.OperationalError as exc:
        if "no such table: services" not in str(exc).lower():
            raise
        return None


def create_service(
    title: str,
    description: str,
    *,
    starting_price: str | None = None,
    icon: str | None = None,
) -> int:
    connection = get_connection()
    cursor = connection.execute(
        """
        INSERT INTO services (title, description, starting_price, icon)
        VALUES (?, ?, ?, ?)
        """,
        (title, description, starting_price, icon),
    )
    connection.commit()
    return int(cursor.lastrowid)


def update_service(
    service_id: int,
    title: str,
    description: str,
    *,
    starting_price: str | None = None,
    icon: str | None = None,
) -> None:
    connection = get_connection()
    connection.execute(
        """
        UPDATE services
        SET title = ?, description = ?, starting_price = ?, icon = ?
        WHERE id = ?
        """,
        (title, description, starting_price, icon, service_id),
    )
    connection.commit()


def toggle_service_active(service_id: int) -> None:
    connection = get_connection()
    connection.execute(
        """
        UPDATE services
        SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END
        WHERE id = ?
        """,
        (service_id,),
    )
    connection.commit()
