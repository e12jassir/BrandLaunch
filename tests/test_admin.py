import sqlite3
import re

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


def seed_service(
    database_path,
    *,
    title,
    description,
    created_at,
    starting_price=None,
    icon=None,
    is_active=1,
):
    with sqlite3.connect(database_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO services (title, description, starting_price, icon, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (title, description, starting_price, icon, is_active, created_at),
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


def build_admin_client_without_init(tmp_path):
    database_path = tmp_path / "brandlaunch-admin-missing-init.sqlite"
    app = create_app(
        {
            "TESTING": False,
            "DATABASE_PATH": str(database_path),
            "ADMIN_USERNAME": "nova-admin",
            "ADMIN_PASSWORD": "super-secret",
        }
    )

    return app.test_client(), database_path


def login_admin(client):
    csrf_token = fetch_csrf_token(client, "/admin/login")
    return client.post(
        "/admin/login",
        data={"username": "nova-admin", "password": "super-secret", "csrf_token": csrf_token},
        follow_redirects=True,
    )


def extract_csrf_token(body: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', body)
    assert match is not None
    return match.group(1)


def fetch_csrf_token(client, path: str) -> str:
    response = client.get(path)
    assert response.status_code == 200
    return extract_csrf_token(response.get_data(as_text=True))


def test_admin_dashboard_empty_state_and_honest_triage_actions(tmp_path):
    client, _database_path = build_admin_client(tmp_path)

    response = login_admin(client)
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

    response = login_admin(client)
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

    login_admin(client)
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

    login_admin(client)
    response = client.get("/admin/leads")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Lead inbox" in body
    assert body.index("Newer Lead") < body.index("Older Lead")
    assert f'href="/admin/leads/{newer_id}"' in body
    assert f'href="/admin/leads/{older_id}"' in body


def test_admin_leads_inbox_shows_empty_state_when_authenticated_but_no_leads(tmp_path):
    client, _database_path = build_admin_client(tmp_path)

    login_admin(client)
    response = client.get("/admin/leads")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Lead inbox" in body
    assert "No leads yet" in body
    assert "The inbox will populate here after the public landing captures its first valid lead." in body


def test_admin_lead_detail_returns_404_for_missing_lead(tmp_path):
    client, _database_path = build_admin_client(tmp_path)

    login_admin(client)
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


def test_admin_services_routes_redirect_to_login_without_session(tmp_path):
    client, database_path = build_admin_client(tmp_path)
    service_id = seed_service(
        database_path,
        title="Launch Sprint",
        description="Focused landing page planning.",
        starting_price="From USD 900",
        icon="LS",
        created_at="2026-05-13 09:00:00",
    )

    list_response = client.get("/admin/services")
    new_response = client.get("/admin/services/new")
    edit_response = client.get(f"/admin/services/{service_id}/edit")
    toggle_response = client.post(f"/admin/services/{service_id}/toggle")

    for response in (list_response, new_response, edit_response, toggle_response):
        assert response.status_code == 302
        assert response.headers["Location"].endswith("/admin/login")


def test_admin_services_list_stays_compact_and_supports_toggle_feedback(tmp_path):
    client, database_path = build_admin_client(tmp_path)
    first_id = seed_service(
        database_path,
        title="Strategy Session",
        description="Sharper offer framing for service businesses.",
        starting_price="From USD 600",
        icon="SS",
        created_at="2026-05-13 09:00:00",
    )
    second_id = seed_service(
        database_path,
        title="Landing Build",
        description="Premium landing design and implementation.",
        starting_price="From USD 1400",
        icon="LB",
        created_at="2026-05-13 10:00:00",
        is_active=0,
    )

    login_admin(client)
    response = client.get("/admin/services?status=updated")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert body.index("Strategy Session") < body.index("Landing Build")
    assert 'href="/admin/services/new"' in body
    assert f'href="/admin/services/{first_id}/edit"' in body
    assert f'href="/admin/services/{second_id}/edit"' in body
    assert f'action="/admin/services/{first_id}/toggle"' in body
    assert f'action="/admin/services/{second_id}/toggle"' in body
    assert "Service updated." in body
    assert "Active" in body
    assert "Inactive" in body
    assert "Delete service" not in body
    assert "Reorder services" not in body
    assert "Upload image" not in body
    assert "Category manager" not in body


def test_admin_services_create_invalid_submission_renders_errors_without_write(tmp_path):
    client, database_path = build_admin_client(tmp_path)
    login_admin(client)
    csrf_token = fetch_csrf_token(client, "/admin/services/new")

    response = client.post(
        "/admin/services/new",
        data={
            "title": "   ",
            "description": "   ",
            "starting_price": " From USD 900 ",
            "icon": " LS ",
            "csrf_token": csrf_token,
        },
    )
    body = response.get_data(as_text=True)

    with sqlite3.connect(database_path) as connection:
        service_count = connection.execute("SELECT COUNT(*) FROM services").fetchone()[0]

    assert response.status_code == 200
    assert service_count == 3
    assert "Title is required" in body
    assert "Description is required" in body
    assert 'value="From USD 900"' in body
    assert 'value="LS"' in body


def test_admin_services_create_without_initialized_db_fails_clearly(tmp_path):
    client, database_path = build_admin_client_without_init(tmp_path)
    login_admin(client)
    csrf_token = fetch_csrf_token(client, "/admin/services/new")

    response = client.post(
        "/admin/services/new",
        data={
            "title": "Positioning Sprint",
            "description": "Compact offer strategy for higher-quality inquiries.",
            "starting_price": "From USD 850",
            "icon": "PS",
            "csrf_token": csrf_token,
        },
    )
    body = response.get_data(as_text=True)

    assert response.status_code == 500
    assert "Initialize the database with flask init-db before managing services." in body

    with sqlite3.connect(database_path) as connection:
        service_table = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'services'"
        ).fetchone()

    assert service_table is None


def test_admin_services_create_edit_and_toggle_success_flows(tmp_path):
    client, database_path = build_admin_client(tmp_path)
    login_admin(client)
    create_csrf = fetch_csrf_token(client, "/admin/services/new")

    create_response = client.post(
        "/admin/services/new",
        data={
            "title": "  Positioning Sprint  ",
            "description": "  Compact offer strategy for higher-quality inquiries.  ",
            "starting_price": "  From USD 850  ",
            "icon": "  PS  ",
            "csrf_token": create_csrf,
        },
    )

    with sqlite3.connect(database_path) as connection:
        created_service = connection.execute(
            "SELECT id, title, description, starting_price, icon, is_active FROM services"
            " ORDER BY created_at DESC, id DESC LIMIT 1"
        ).fetchone()

    assert create_response.status_code == 302
    assert create_response.headers["Location"].endswith("/admin/services?status=created")
    assert created_service[1:] == (
        "Positioning Sprint",
        "Compact offer strategy for higher-quality inquiries.",
        "From USD 850",
        "PS",
        1,
    )

    edit_csrf = fetch_csrf_token(client, f"/admin/services/{created_service[0]}/edit")
    edit_response = client.post(
        f"/admin/services/{created_service[0]}/edit",
        data={
            "title": "Positioning Sprint + Wireframe",
            "description": "Sharper positioning plus a clearer conversion path.",
            "starting_price": "From USD 1100",
            "icon": "PW",
            "csrf_token": edit_csrf,
        },
    )

    list_csrf = fetch_csrf_token(client, "/admin/services")
    toggle_response = client.post(
        f"/admin/services/{created_service[0]}/toggle",
        data={"csrf_token": list_csrf},
    )

    with sqlite3.connect(database_path) as connection:
        updated_service = connection.execute(
            "SELECT title, description, starting_price, icon, is_active FROM services WHERE id = ?",
            (created_service[0],),
        ).fetchone()

    assert edit_response.status_code == 302
    assert edit_response.headers["Location"].endswith("/admin/services?status=updated")
    assert toggle_response.status_code == 302
    assert toggle_response.headers["Location"].endswith("/admin/services?status=updated")
    assert updated_service == (
        "Positioning Sprint + Wireframe",
        "Sharper positioning plus a clearer conversion path.",
        "From USD 1100",
        "PW",
        0,
    )


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
    csrf_token = fetch_csrf_token(client, "/admin/login")

    response = client.post(
        "/admin/login",
        data={"username": "nova-admin", "password": "wrong-secret", "csrf_token": csrf_token},
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
    csrf_token = fetch_csrf_token(client, "/admin/login")

    response = client.post(
        "/admin/login",
        data={"username": "nova-admin", "password": "super-secret", "csrf_token": csrf_token},
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/admin")

    with client.session_transaction() as session:
        assert session["is_admin_authenticated"] is True


def test_admin_logout_clears_session_and_blocks_later_inbox_access(tmp_path):
    client, _database_path = build_admin_client(tmp_path)
    login_admin(client)

    logout_csrf = fetch_csrf_token(client, "/admin")
    logout_response = client.post("/admin/logout", data={"csrf_token": logout_csrf})
    redirected_response = client.get("/admin")

    assert logout_response.status_code == 302
    assert logout_response.headers["Location"].endswith("/admin/login")
    with client.session_transaction() as session:
        assert "is_admin_authenticated" not in session
    assert redirected_response.status_code == 302
    assert redirected_response.headers["Location"].endswith("/admin/login")


def test_admin_login_rejects_missing_csrf_token(tmp_path):
    client, _database_path = build_admin_client(tmp_path)

    response = client.post(
        "/admin/login",
        data={"username": "nova-admin", "password": "super-secret"},
    )

    assert response.status_code == 400


def test_admin_services_create_rejects_missing_csrf_token(tmp_path):
    client, _database_path = build_admin_client(tmp_path)
    login_admin(client)

    response = client.post(
        "/admin/services/new",
        data={
            "title": "Positioning Sprint",
            "description": "Compact offer strategy for higher-quality inquiries.",
            "starting_price": "From USD 850",
            "icon": "PS",
        },
    )

    assert response.status_code == 400
