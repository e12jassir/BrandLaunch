import sqlite3

from flask import (
    Flask,
    abort,
    current_app,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from config import Config
from database.db import close_connection, get_lead, init_db, insert_lead, list_leads


FORM_FIELDS = ("name", "email", "phone", "service_interest", "message")


def build_form_values(source: dict | None = None) -> dict[str, str]:
    source = source or {}
    return {field: str(source.get(field, "")).strip() for field in FORM_FIELDS}


def validate_lead_form(form_values: dict[str, str]) -> dict[str, str]:
    errors: dict[str, str] = {}
    for field in ("name", "email", "message"):
        if not form_values[field]:
            errors[field] = f"{field} is required"
    return errors


def render_landing(
    *,
    form_values: dict[str, str] | None = None,
    form_errors: dict[str, str] | None = None,
    submission_state: str | None = None,
    database_error: str | None = None,
    status_code: int = 200,
):
    return (
        render_template(
            "landing.html",
            form_values=form_values or build_form_values(),
            form_errors=form_errors or {},
            submission_state=submission_state,
            database_error=database_error,
        ),
        status_code,
    )


def render_admin_inbox(*, status_code: int = 200):
    return render_template("admin.html", leads=list_leads()), status_code


def admin_credentials_configured(app: Flask) -> bool:
    return bool(app.config.get("ADMIN_USERNAME") and app.config.get("ADMIN_PASSWORD"))


def is_admin_authenticated() -> bool:
    return session.get("is_admin_authenticated") is True


def redirect_to_admin_login():
    return redirect(url_for("admin_login"))


def require_admin_session():
    if not is_admin_authenticated():
        return redirect_to_admin_login()
    return None


def render_admin_login(*, error_message: str | None = None, status_code: int = 200):
    missing_config_message = None
    credentials_ready = admin_credentials_configured(current_app)
    if not credentials_ready:
        missing_config_message = "Falta configurar las credenciales de administrador"

    return (
        render_template(
            "admin_login.html",
            credentials_ready=credentials_ready,
            error_message=error_message,
            missing_config_message=missing_config_message,
        ),
        status_code,
    )


def create_app(config_overrides: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(Config.from_env().to_flask_config())

    if config_overrides:
        app.config.update(config_overrides)

    app.teardown_appcontext(close_connection)

    @app.route("/", methods=["GET", "POST"])
    def landing():
        if request.method == "GET":
            return render_landing()

        form_values = build_form_values(request.form.to_dict())
        form_errors = validate_lead_form(form_values)
        if form_errors:
            return render_landing(
                form_values=form_values,
                form_errors=form_errors,
                submission_state="error",
            )

        try:
            insert_lead(
                form_values["name"],
                form_values["email"],
                form_values["message"],
                phone=form_values["phone"] or None,
                service_interest=form_values["service_interest"] or None,
            )
        except sqlite3.OperationalError as exc:
            if "no such table: leads" not in str(exc).lower():
                raise
            return render_landing(
                form_values=form_values,
                submission_state="error",
                database_error="Initialize the database with flask init-db before accepting leads.",
                status_code=500,
            )

        return render_landing(submission_state="success")

    @app.get("/admin")
    def admin():
        if redirect_response := require_admin_session():
            return redirect_response
        return render_admin_inbox()

    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        if request.method == "GET":
            return render_admin_login()

        if not admin_credentials_configured(app):
            return render_admin_login()

        username = str(request.form.get("username", "")).strip()
        password = str(request.form.get("password", ""))
        if (
            username != app.config["ADMIN_USERNAME"]
            or password != app.config["ADMIN_PASSWORD"]
        ):
            return render_admin_login(error_message="Credenciales invalidas")

        session.clear()
        session["is_admin_authenticated"] = True
        return redirect(url_for("admin"))

    @app.post("/admin/logout")
    def admin_logout():
        session.clear()
        return redirect_to_admin_login()

    @app.get("/admin/leads/<int:lead_id>")
    def admin_lead_detail(lead_id: int):
        if redirect_response := require_admin_session():
            return redirect_response
        lead = get_lead(lead_id)
        if lead is None:
            abort(404)
        return render_template("admin_lead_detail.html", lead=lead)

    @app.cli.command("init-db")
    def init_db_command():
        init_db(app)
        print("Initialized the BrandLaunch database.")

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
