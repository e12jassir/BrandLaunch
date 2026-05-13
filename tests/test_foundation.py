import os
import sqlite3
import subprocess
from pathlib import Path

from app import create_app
from database.db import init_db


def test_public_home_uses_nova_studio_digital_metadata_and_shared_landmarks(client):
    response = client.get("/")

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Nova Studio Digital" in body
    assert "real client results" not in body.lower()
    assert "<title>Nova Studio Digital" in body
    assert 'meta name="description" content="Nova Studio Digital builds high-touch websites' in body
    assert 'href="#main-content"' in body
    assert '<header class="site-header"' in body
    assert 'aria-label="Primary navigation"' in body
    assert '<main id="main-content"' in body
    assert body.count("<h1") == 1


def test_admin_placeholder_names_deferred_workflows(client):
    response = client.get("/admin")

    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "auth" in body
    assert "dashboard" in body
    assert "CRUD" in body
    assert "deferred" in body


def test_missing_env_uses_safe_development_defaults(monkeypatch):
    monkeypatch.delenv("FLASK_ENV", raising=False)
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.delenv("DATABASE_PATH", raising=False)

    app = create_app({"TESTING": True})

    assert app.config["ENV_NAME"] == "development"
    assert app.config["SECRET_KEY"] == "dev-secret-key-change-me"
    assert app.config["DATABASE_PATH"] == "brandlaunch.sqlite"


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
    for path in ("/", "/admin"):
        body = client.get(path).get_data(as_text=True)
        assert '<meta name="viewport"' in body
        assert 'aria-label="Primary navigation"' in body
        assert "<main" in body
        assert "<footer" in body
        assert "styles.css" in body
        assert "app.js" in body


def test_small_viewport_static_contract_keeps_placeholder_pages_usable():
    css = Path("static/css/styles.css").read_text(encoding="utf-8")
    app = create_app({"TESTING": True})
    client = app.test_client()

    for path in ("/", "/admin"):
        body = client.get(path).get_data(as_text=True)
        assert '<meta name="viewport" content="width=device-width, initial-scale=1"' in body

    assert "width: min(1120px, calc(100% - 2rem));" in css
    assert "@media (max-width: 760px)" in css
    assert "grid-template-columns: 1fr;" in css
    assert "overflow-wrap: anywhere;" in css
    assert "padding: 1.5rem;" in css


def test_public_landing_stays_presentation_only_while_admin_remains_deferred(client):
    landing_body = client.get("/").get_data(as_text=True).lower()
    admin_body = client.get("/admin").get_data(as_text=True).lower()

    assert "real client results" not in landing_body
    assert "action=" not in landing_body
    assert 'method="post"' not in landing_body
    assert "auth" in admin_body
    assert "dashboard" in admin_body
    assert "crud" in admin_body
    assert "deferred" in admin_body


def test_progressive_script_stays_inert_without_needed_enhancements():
    script = Path("static/js/app.js").read_text(encoding="utf-8")

    assert "js-ready" not in script
    assert script.strip() in {"", "// No landing enhancement needed."}


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
        "admin auth",
        "CRUD",
        "CSV export",
        "analytics",
        "email",
        "deployment",
        "Nova Studio Digital",
        "WhatsApp-first",
        "public premium landing",
    ):
        assert expected in readme
