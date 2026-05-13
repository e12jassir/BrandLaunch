import sqlite3

from app import create_app
from database.db import init_db


def seed_lead(database_path, *, name, email, message, created_at, phone=None, service_interest=None):
    with sqlite3.connect(database_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO leads (name, email, phone, service_interest, message, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name, email, phone, service_interest, message, created_at),
        )
        connection.commit()
        return int(cursor.lastrowid)


def build_admin_client(tmp_path):
    database_path = tmp_path / "brandlaunch-admin.sqlite"
    app = create_app({"TESTING": True, "DATABASE_PATH": str(database_path)})

    with app.app_context():
        init_db(app)

    return app.test_client(), database_path


def test_admin_inbox_empty_state_and_deferred_scope_copy(tmp_path):
    client, _database_path = build_admin_client(tmp_path)

    response = client.get("/admin")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Lead inbox" in body
    assert "No leads yet" in body
    assert "internal preview" in body.lower()
    assert "auth" in body.lower()
    assert "search" in body.lower()
    assert "filter" in body.lower()
    assert "export" in body.lower()
    assert "metrics" in body.lower()


def test_admin_inbox_shows_newest_first_summary_and_short_excerpt(tmp_path):
    client, database_path = build_admin_client(tmp_path)
    older_id = seed_lead(
        database_path,
        name="Older Lead",
        email="older@example.com",
        phone="+54 11 4000 0000",
        service_interest="Landing refresh",
        message="Older message should appear after the two newest entries in the inbox.",
        created_at="2026-05-13 10:00:00",
    )
    tied_first_id = seed_lead(
        database_path,
        name="Newest By Id",
        email="newest@example.com",
        phone="+54 11 4111 1111",
        service_interest="Launch system",
        message="This message is intentionally long so the inbox only shows a very short excerpt instead of the full detail body for internal scanning purposes.",
        created_at="2026-05-13 11:00:00",
    )
    tied_second_id = seed_lead(
        database_path,
        name="Newest Same Timestamp",
        email="tie@example.com",
        phone="+54 11 4222 2222",
        service_interest="Offer repositioning",
        message="Tie-breaker record should render first because it has the higher id at the same timestamp.",
        created_at="2026-05-13 11:00:00",
    )

    response = client.get("/admin")
    body = response.get_data(as_text=True)

    first_index = body.index("Newest Same Timestamp")
    second_index = body.index("Newest By Id")
    third_index = body.index("Older Lead")

    assert response.status_code == 200
    assert first_index < second_index < third_index
    assert "Tie-breaker record should render first because it has the higher id at the same" in body
    assert "Tie-breaker record should render first because it has the higher id at the same timestamp." not in body
    assert f'href="/admin/leads/{tied_second_id}"' in body
    assert f'href="/admin/leads/{tied_first_id}"' in body
    assert f'href="/admin/leads/{older_id}"' in body
    assert "Offer repositioning" in body
    assert "Launch system" in body
    assert "Older message should appear after the two newest entries in the inbox." in body


def test_admin_lead_detail_renders_full_read_only_record(tmp_path):
    client, database_path = build_admin_client(tmp_path)
    lead_id = seed_lead(
        database_path,
        name="Ada Lovelace",
        email="ada@example.com",
        phone="+54 11 4333 3333",
        service_interest="Website refresh",
        message="Need a premium homepage with a WhatsApp-first path and tighter offer framing.",
        created_at="2026-05-13 12:00:00",
    )

    response = client.get(f"/admin/leads/{lead_id}")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Lead detail" in body
    assert "Ada Lovelace" in body
    assert "ada@example.com" in body
    assert "+54 11 4333 3333" in body
    assert "Website refresh" in body
    assert "Need a premium homepage with a WhatsApp-first path and tighter offer framing." in body
    assert "nuevo" in body
    assert 'href="/admin"' in body
    assert "Edit lead" not in body
    assert "Delete lead" not in body


def test_admin_lead_detail_returns_404_for_missing_lead(tmp_path):
    client, _database_path = build_admin_client(tmp_path)

    response = client.get("/admin/leads/9999")

    assert response.status_code == 404
