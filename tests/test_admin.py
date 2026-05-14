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
    app = create_app(
        {
            "TESTING": True,
            "DATABASE_PATH": str(database_path),
            "ADMIN_USERNAME": "nova-admin",
            "ADMIN_PASSWORD": "super-secret",
        }
    )

    with app.app_context():
        init_db(app)

    return app.test_client(), database_path


def test_admin_dashboard_empty_state_and_honest_triage_actions(tmp_path):
    client, _database_path = build_admin_client(tmp_path)

    response = client.post(
        "/admin/login",
        data={"username": "nova-admin", "password": "super-secret"},
        follow_redirects=True,
    )
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Admin overview" in body
    assert "0" in body
    assert "No leads captured yet" in body
    assert 'href="/admin/leads"' in body
    assert "Open inbox" in body
    assert "Latest lead unavailable until the first submission lands." in body
    assert "/admin/leads/" not in body
    assert "Edit lead" not in body
    assert "Delete lead" not in body


def test_admin_dashboard_shows_real_metrics_latest_link_and_recent_preview_order(tmp_path):
    client, database_path = build_admin_client(tmp_path)
    older_id = seed_lead(
        database_path,
        name="Older Lead",
        email="older@example.com",
        phone="+54 11 4000 0000",
        service_interest="Landing refresh",
        message="Older message should appear after the two newest entries in the inbox while still proving the preview does not dump the entire note into the dashboard card.",
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

    response = client.post(
        "/admin/login",
        data={"username": "nova-admin", "password": "super-secret"},
        follow_redirects=True,
    )
    body = response.get_data(as_text=True)

    first_index = body.index("Newest Same Timestamp")
    second_index = body.index("Newest By Id")
    third_index = body.index("Older Lead")

    assert response.status_code == 200
    assert "Admin overview" in body
    assert "Total leads" in body
    assert "3" in body
    assert "New leads" in body
    assert "Latest submission" in body
    assert first_index < second_index < third_index
    assert "Tie-breaker record should render first because it has the higher id at the same" in body
    assert "Tie-breaker record should render first because it has the higher id at the same timestamp." not in body
    assert f'href="/admin/leads/{tied_second_id}"' in body
    assert 'href="/admin/leads"' in body
    assert "Open latest lead" in body
    assert f'href="/admin/leads/{tied_second_id}"' in body
    assert f'href="/admin/leads/{tied_first_id}"' in body
    assert f'href="/admin/leads/{older_id}"' in body
    assert "Offer repositioning" in body
    assert "Launch system" in body
    assert "Older message should appear after the two newest entries in the inbox while sti" in body
    assert "Older message should appear after the two newest entries in the inbox while still proving the preview does not dump the entire note into the dashboard card." not in body


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

    client.post(
        "/admin/login",
        data={"username": "nova-admin", "password": "super-secret"},
        follow_redirects=True,
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
    assert 'href="/admin/leads"' in body
    assert "Edit lead" not in body
    assert "Delete lead" not in body


def test_admin_leads_inbox_keeps_newest_first_listing_on_new_route(tmp_path):
    client, database_path = build_admin_client(tmp_path)
    older_id = seed_lead(
        database_path,
        name="Older Lead",
        email="older@example.com",
        message="Older message should still render in the inbox route.",
        created_at="2026-05-13 10:00:00",
        service_interest="Landing refresh",
    )
    newer_id = seed_lead(
        database_path,
        name="Newer Lead",
        email="newer@example.com",
        message="Newest lead should appear first in the full inbox route.",
        created_at="2026-05-13 11:00:00",
        service_interest="Offer repositioning",
    )

    client.post(
        "/admin/login",
        data={"username": "nova-admin", "password": "super-secret"},
        follow_redirects=True,
    )
    response = client.get("/admin/leads")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Lead inbox" in body
    assert body.index("Newer Lead") < body.index("Older Lead")
    assert f'href="/admin/leads/{newer_id}"' in body
    assert f'href="/admin/leads/{older_id}"' in body


def test_admin_leads_inbox_shows_empty_state_when_authenticated_but_no_leads(tmp_path):
    client, _database_path = build_admin_client(tmp_path)

    client.post(
        "/admin/login",
        data={"username": "nova-admin", "password": "super-secret"},
        follow_redirects=True,
    )
    response = client.get("/admin/leads")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Lead inbox" in body
    assert "No leads yet" in body
    assert "The inbox will populate here after the public landing captures its first valid lead." in body


def test_admin_lead_detail_returns_404_for_missing_lead(tmp_path):
    client, _database_path = build_admin_client(tmp_path)

    client.post(
        "/admin/login",
        data={"username": "nova-admin", "password": "super-secret"},
        follow_redirects=True,
    )
    response = client.get("/admin/leads/9999")

    assert response.status_code == 404


def test_admin_inbox_redirects_to_login_without_session(tmp_path):
    client, _database_path = build_admin_client(tmp_path)

    response = client.get("/admin")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/admin/login")


def test_admin_leads_redirects_to_login_without_session(tmp_path):
    client, _database_path = build_admin_client(tmp_path)

    response = client.get("/admin/leads")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/admin/login")


def test_admin_lead_detail_redirects_to_login_without_session(tmp_path):
    client, database_path = build_admin_client(tmp_path)
    lead_id = seed_lead(
        database_path,
        name="Ada Lovelace",
        email="ada@example.com",
        message="Need help.",
        created_at="2026-05-13 12:00:00",
    )

    response = client.get(f"/admin/leads/{lead_id}")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/admin/login")


def test_admin_login_shows_missing_config_message_when_credentials_are_absent(tmp_path):
    database_path = tmp_path / "brandlaunch-admin.sqlite"
    app = create_app(
        {
            "TESTING": True,
            "DATABASE_PATH": str(database_path),
            "ADMIN_USERNAME": None,
            "ADMIN_PASSWORD": None,
        }
    )

    with app.app_context():
        init_db(app)

    client = app.test_client()
    response = client.get("/admin/login")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Configuration required" in body
    assert "Admin credentials have not been configured yet" in body
    assert "Set the ADMIN_USERNAME and ADMIN_PASSWORD variables to enable this internal access." in body
    assert 'role="status"' in body
    assert 'aria-label="Admin login form"' not in body
    assert "Sign in to admin" not in body


def test_admin_login_rejects_invalid_credentials_inline(tmp_path):
    client, _database_path = build_admin_client(tmp_path)

    response = client.post(
        "/admin/login",
        data={"username": "nova-admin", "password": "wrong-secret"},
    )
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Access denied" in body
    assert "Invalid credentials. Check the username and password, then try again." in body
    assert 'role="alert"' in body
    assert 'aria-label="Admin login form"' in body
    assert 'name="username"' in body
    assert 'name="password"' in body
    assert "Sign in to admin" in body


def test_admin_login_creates_authenticated_session_and_redirects_to_inbox(tmp_path):
    client, _database_path = build_admin_client(tmp_path)

    response = client.post(
        "/admin/login",
        data={"username": "nova-admin", "password": "super-secret"},
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/admin")

    with client.session_transaction() as session:
        assert session["is_admin_authenticated"] is True


def test_admin_logout_clears_session_and_blocks_later_inbox_access(tmp_path):
    client, _database_path = build_admin_client(tmp_path)
    client.post(
        "/admin/login",
        data={"username": "nova-admin", "password": "super-secret"},
    )

    logout_response = client.post("/admin/logout")
    redirected_response = client.get("/admin")

    assert logout_response.status_code == 302
    assert logout_response.headers["Location"].endswith("/admin/login")
    with client.session_transaction() as session:
        assert "is_admin_authenticated" not in session
    assert redirected_response.status_code == 302
    assert redirected_response.headers["Location"].endswith("/admin/login")
