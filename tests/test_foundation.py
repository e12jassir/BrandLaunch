import os
import sqlite3
import subprocess
from pathlib import Path

from app import create_app
from database.db import init_db


def test_public_home_uses_service_business_metadata_and_shared_landmarks(client):
    response = client.get("/")

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Landing premium para negocios de servicios" in body
    assert "real client results" not in body.lower()
    assert "<title>Landing premium para negocios de servicios" in body
    assert 'meta name="description" content="Landing premium para negocios de servicios' in body
    assert 'href="#main-content"' in body
    assert '<header class="site-header"' in body
    assert 'aria-label="Primary navigation"' in body
    assert '<main id="main-content"' in body
    assert body.count("<h1") == 1


def test_admin_login_keeps_shared_layout_and_auth_boundaries(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATABASE_PATH": str(tmp_path / "brandlaunch-foundation.sqlite"),
            "ADMIN_USERNAME": "nova-admin",
            "ADMIN_PASSWORD": "super-secret",
        }
    )
    response = app.test_client().get("/admin/login")

    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Acceso administrativo" in body
    assert "Ingreso interno para revisar contactos y seguimiento comercial." in body
    assert "Operación interna" in body
    assert "Solo la cuenta administradora configurada puede entrar." in body
    assert "Usuario administrador" in body
    assert "Clave de acceso" in body
    assert "Entrar al panel interno" in body
    assert "Acceso interno de BrandLaunch para revisión administrativa." in body
    assert "Authenticate before reviewing leads" not in body
    assert "Username" not in body
    assert "Password" not in body
    assert "lead inbox" not in body.lower()


def test_missing_env_uses_safe_development_defaults(monkeypatch):
    monkeypatch.delenv("FLASK_ENV", raising=False)
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.delenv("DATABASE_PATH", raising=False)
    monkeypatch.delenv("ADMIN_USERNAME", raising=False)
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)

    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "dev-secret-key-change-me",
            "DATABASE_PATH": "brandlaunch.sqlite",
            "ADMIN_USERNAME": None,
            "ADMIN_PASSWORD": None,
        }
    )

    assert app.config["ENV_NAME"] == "development"
    assert app.config["SECRET_KEY"] == "dev-secret-key-change-me"
    assert app.config["DATABASE_PATH"] == "brandlaunch.sqlite"
    assert app.config["ADMIN_USERNAME"] is None
    assert app.config["ADMIN_PASSWORD"] is None


def test_env_admin_credentials_override_defaults(monkeypatch):
    monkeypatch.setenv("ADMIN_USERNAME", "nova-admin")
    monkeypatch.setenv("ADMIN_PASSWORD", "super-secret")

    app = create_app({"TESTING": True})

    assert app.config["ADMIN_USERNAME"] == "nova-admin"
    assert app.config["ADMIN_PASSWORD"] == "super-secret"


def test_admin_login_route_is_available_from_the_public_side(client):
    response = client.get("/admin/login")

    assert response.status_code == 200


def test_admin_route_requires_login_when_no_admin_session_exists(client):
    response = client.get("/admin")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/admin/login")


def test_database_initialization_is_repeatable(tmp_path):
    database_path = tmp_path / "brandlaunch.sqlite"
    app = create_app({"TESTING": True, "DATABASE_PATH": str(database_path)})

    with app.app_context():
        init_db(app)
        init_db(app)

    with sqlite3.connect(database_path) as connection:
        table_names = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }

    assert {"leads", "services", "testimonials", "site_settings"}.issubset(
        table_names
    )


def test_pages_use_shared_layout_and_assets(client):
    for path in ("/", "/admin/login"):
        body = client.get(path).get_data(as_text=True)
        assert '<meta name="viewport"' in body
        assert 'aria-label="Primary navigation"' in body
        assert "<main" in body
        assert "<footer" in body
        assert "styles.css" in body
        assert "app.js" in body


def test_small_viewport_static_contract_keeps_foundation_pages_usable():
    css = Path("static/css/styles.css").read_text(encoding="utf-8")
    app = create_app(
        {
            "TESTING": True,
            "ADMIN_USERNAME": None,
            "ADMIN_PASSWORD": None,
        }
    )
    client = app.test_client()

    for path in ("/", "/admin/login"):
        body = client.get(path).get_data(as_text=True)
        assert '<meta name="viewport" content="width=device-width, initial-scale=1"' in body

    assert "width: min(1120px, calc(100% - 2rem));" in css
    assert "@media (max-width: 760px)" in css
    assert "grid-template-columns: 1fr;" in css
    assert "overflow-wrap: anywhere;" in css
    assert "padding: 1.5rem;" in css
    admin_body = client.get("/admin/login").get_data(as_text=True)
    assert "admin-login-shell" in admin_body
    assert "admin-login-card" in admin_body
    assert "admin-login-status" in admin_body
    assert ".admin-login-shell" in css
    assert ".admin-login-card" in css
    assert ".admin-login-form" in css
    assert ".admin-login-status" in css
    assert ".admin-login-status--pending" in css
    assert ".admin-login-status--error" in css
    assert "min-height: calc(100vh - 12rem);" in css
    assert "width: min(100%, 32rem);" in css


def test_public_landing_stays_presentation_only_while_admin_requires_login(tmp_path):
    app = create_app({
        "TESTING": True,
        "DATABASE_PATH": str(tmp_path / "brandlaunch-invalid.sqlite"),
    })

    with app.app_context():
        init_db(app)

    client = app.test_client()
    response = client.post(
        "/",
        data={
            "name": "",
            "email": "",
            "phone": "+54 11 5555 5555",
            "service_interest": "Landing page",
            "message": "",
        },
    )
    body = response.get_data(as_text=True)

    with sqlite3.connect(app.config["DATABASE_PATH"]) as connection:
        lead_count = connection.execute("SELECT COUNT(*) FROM leads").fetchone()[0]

    admin_response = client.get("/admin")

    assert response.status_code == 200
    assert lead_count == 0
    assert "El nombre es obligatorio" in body
    assert "El email es obligatorio" in body
    assert "Contanos brevemente que necesitas" in body
    assert 'value="+54 11 5555 5555"' in body
    assert 'value="Landing page"' in body
    assert admin_response.status_code == 302
    assert admin_response.headers["Location"].endswith("/admin/login")


def test_valid_post_persists_lead_and_renders_thank_you_state(tmp_path):
    database_path = tmp_path / "brandlaunch-leads.sqlite"
    app = create_app({"TESTING": True, "DATABASE_PATH": str(database_path)})

    with app.app_context():
        init_db(app)

    client = app.test_client()
    response = client.post(
        "/",
        data={
            "name": "Ada Lovelace",
            "email": "ada@example.com",
            "phone": "+54 11 4444 4444",
            "service_interest": "Website refresh",
            "message": "I want a premium landing that still pushes WhatsApp first.",
        },
    )
    body = response.get_data(as_text=True)

    with sqlite3.connect(database_path) as connection:
        lead = connection.execute(
            "SELECT name, email, phone, service_interest, message, status, created_at FROM leads"
        ).fetchone()

    assert response.status_code == 200
    assert "Listo — recibimos tu brief." in body
    assert 'href="https://wa.me/15550000000?text=Hi%20Nova%20Studio%20Digital"' in body
    assert lead[:6] == (
        "Ada Lovelace",
        "ada@example.com",
        "+54 11 4444 4444",
        "Website refresh",
        "I want a premium landing that still pushes WhatsApp first.",
        "nuevo",
    )
    assert lead[6] is not None


def test_post_without_initialized_database_fails_clearly(tmp_path):
    database_path = tmp_path / "missing-init.sqlite"
    app = create_app({"TESTING": True, "DATABASE_PATH": str(database_path)})
    client = app.test_client()

    response = client.post(
        "/",
        data={
            "name": "Ada Lovelace",
            "email": "ada@example.com",
            "message": "Need help.",
        },
    )

    assert response.status_code == 500
    assert "Inicializa la base con flask init-db antes de recibir leads." in response.get_data(
        as_text=True
    )


def test_progressive_script_stays_inert_without_needed_enhancements():
    script = Path("static/js/app.js").read_text(encoding="utf-8")

    assert "js-ready" not in script
    assert script.strip() in {"", "// No landing enhancement needed."}


def test_readme_remains_untouched_by_landing_refinement_slice():
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "Start in WhatsApp and we will map the first landing direction together." not in readme
    assert "Sitios premium para vender mejor por WhatsApp." not in readme


def test_documented_venv_flask_init_db_cli_creates_schema(tmp_path):
    database_path = tmp_path / "brandlaunch-cli.sqlite"
    readme = Path("README.md").read_text(encoding="utf-8")

    assert ".venv/bin/flask --app app init-db" in readme

    result = subprocess.run(
        [".venv/bin/flask", "--app", "app", "init-db"],
        check=False,
        cwd=Path.cwd(),
        env={**os.environ, "DATABASE_PATH": str(database_path)},
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "Initialized the BrandLaunch database." in result.stdout

    with sqlite3.connect(database_path) as connection:
        table_names = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }

    assert {"leads", "services", "testimonials", "site_settings"}.issubset(
        table_names
    )


def test_readme_documents_foundation_workflow_and_limits():
    readme = Path("README.md").read_text(encoding="utf-8")

    for expected in (
        ".venv/bin/python -m pip install -r requirements.txt",
        ".venv/bin/flask --app app init-db",
        ".venv/bin/flask --app app run",
        ".venv/bin/pytest",
        ".venv/bin/ruff check .",
        "/admin/login",
        "/admin/leads/<id>",
        "admin auth",
        "read-only",
        "CSV export",
        "analytics",
        "email",
        "deployment",
        "Nova Studio Digital",
        "WhatsApp-first",
        "public premium landing",
    ):
        assert expected in readme
