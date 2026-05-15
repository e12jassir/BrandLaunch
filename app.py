import sqlite3
import secrets

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
from database.db import (
    close_connection,
    create_service,
    get_service,
    get_lead,
    get_lead_dashboard_summary,
    init_db,
    insert_lead,
    list_services,
    list_leads,
    list_recent_leads,
    toggle_service_active,
    update_service,
)


FORM_FIELDS = ("name", "email", "phone", "service_interest", "message")
SERVICE_FORM_FIELDS = ("title", "description", "starting_price", "icon")
SERVICE_STATUS_MESSAGES = {
    "created": "Service created.",
    "updated": "Service updated.",
}
SERVICES_SETUP_ERROR = "Initialize the database with flask init-db before managing services."


def build_form_values(source: dict | None = None) -> dict[str, str]:
    source = source or {}
    return {field: str(source.get(field, "")).strip() for field in FORM_FIELDS}


def build_service_form_values(source: dict | None = None) -> dict[str, str]:
    source = source or {}
    values: dict[str, str] = {}
    for field in SERVICE_FORM_FIELDS:
        if hasattr(source, "get"):
            raw_value = source.get(field, "")
        elif hasattr(source, "keys") and field in source.keys():
            raw_value = source[field]
        else:
            raw_value = ""
        values[field] = str(raw_value or "").strip()
    return values


def validate_lead_form(form_values: dict[str, str]) -> dict[str, str]:
    errors: dict[str, str] = {}
    for field in ("name", "email", "message"):
        if not form_values[field]:
            errors[field] = f"{field} is required"
    return errors


def validate_service_form(form_values: dict[str, str]) -> dict[str, str]:
    errors: dict[str, str] = {}
    if not form_values["title"]:
        errors["title"] = "Title is required"
    if not form_values["description"]:
        errors["description"] = "Description is required"
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
            services=list_services(include_inactive=False),
            form_values=form_values or build_form_values(),
            form_errors=form_errors or {},
            submission_state=submission_state,
            database_error=database_error,
        ),
        status_code,
    )


def render_admin_dashboard(*, status_code: int = 200):
    return (
        render_template(
            "admin.html",
            summary=get_lead_dashboard_summary(),
            recent_leads=list_recent_leads(),
        ),
        status_code,
    )


def render_admin_inbox(*, status_code: int = 200):
    return render_template("admin_leads.html", leads=list_leads()), status_code


def render_admin_services(*, status: str | None = None, status_code: int = 200):
    return (
        render_template(
            "admin_services.html",
            services=list_services(include_inactive=True),
            status_message=SERVICE_STATUS_MESSAGES.get(status),
            database_error=None,
        ),
        status_code,
    )


def render_admin_service_form(
    *,
    form_mode: str,
    service: dict | None = None,
    form_values: dict[str, str] | None = None,
    form_errors: dict[str, str] | None = None,
    database_error: str | None = None,
    status_code: int = 200,
):
    service_values = service or {}
    return (
        render_template(
            "admin_service_form.html",
            form_mode=form_mode,
            service=service,
            form_values=form_values or build_service_form_values(service_values),
            form_errors=form_errors or {},
            database_error=database_error,
        ),
        status_code,
    )


def render_admin_services_error(*, message: str, status_code: int = 500):
    return (
        render_template(
            "admin_services.html",
            services=list_services(include_inactive=True),
            status_message=None,
            database_error=message,
        ),
        status_code,
    )


def is_missing_services_table_error(exc: sqlite3.OperationalError) -> bool:
    return "no such table: services" in str(exc).lower()


def admin_credentials_configured(app: Flask) -> bool:
    return bool(app.config.get("ADMIN_USERNAME") and app.config.get("ADMIN_PASSWORD"))


def is_admin_authenticated() -> bool:
    return session.get("is_admin_authenticated") is True


def redirect_to_admin_login():
    return redirect(url_for("admin_login"))


def get_csrf_token() -> str:
    token = session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token
    return token


def require_csrf_token():
    session_token = session.get("csrf_token")
    request_token = str(request.form.get("csrf_token", ""))
    if not session_token or not request_token or request_token != session_token:
        abort(400)


def require_admin_session():
    if not is_admin_authenticated():
        return redirect_to_admin_login()
    return None


def render_admin_login(*, error_message: str | None = None, status_code: int = 200):
    missing_config_message = None
    credentials_ready = admin_credentials_configured(current_app)
    if not credentials_ready:
        missing_config_message = "Admin credentials have not been configured yet"

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

    @app.context_processor
    def inject_csrf_token():
        return {"csrf_token": get_csrf_token()}

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
        return render_admin_dashboard()

    @app.get("/admin/leads")
    def admin_leads():
        if redirect_response := require_admin_session():
            return redirect_response
        return render_admin_inbox()

    @app.get("/admin/services")
    def admin_services():
        if redirect_response := require_admin_session():
            return redirect_response
        return render_admin_services(status=request.args.get("status"))

    @app.route("/admin/services/new", methods=["GET", "POST"])
    def admin_services_new():
        if redirect_response := require_admin_session():
            return redirect_response

        if request.method == "GET":
            return render_admin_service_form(form_mode="create")

        require_csrf_token()

        form_values = build_service_form_values(request.form.to_dict())
        form_errors = validate_service_form(form_values)
        if form_errors:
            return render_admin_service_form(
                form_mode="create",
                form_values=form_values,
                form_errors=form_errors,
            )

        try:
            create_service(
                form_values["title"],
                form_values["description"],
                starting_price=form_values["starting_price"] or None,
                icon=form_values["icon"] or None,
            )
        except sqlite3.OperationalError as exc:
            if not is_missing_services_table_error(exc):
                raise
            return render_admin_service_form(
                form_mode="create",
                form_values=form_values,
                database_error=SERVICES_SETUP_ERROR,
                status_code=500,
            )
        return redirect(url_for("admin_services", status="created"))

    @app.route("/admin/services/<int:service_id>/edit", methods=["GET", "POST"])
    def admin_services_edit(service_id: int):
        if redirect_response := require_admin_session():
            return redirect_response

        service = get_service(service_id)
        if service is None:
            abort(404)

        if request.method == "GET":
            return render_admin_service_form(form_mode="edit", service=service)

        require_csrf_token()

        form_values = build_service_form_values(request.form.to_dict())
        form_errors = validate_service_form(form_values)
        if form_errors:
            return render_admin_service_form(
                form_mode="edit",
                service=service,
                form_values=form_values,
                form_errors=form_errors,
            )

        try:
            update_service(
                service_id,
                form_values["title"],
                form_values["description"],
                starting_price=form_values["starting_price"] or None,
                icon=form_values["icon"] or None,
            )
        except sqlite3.OperationalError as exc:
            if not is_missing_services_table_error(exc):
                raise
            return render_admin_service_form(
                form_mode="edit",
                service=service,
                form_values=form_values,
                database_error=SERVICES_SETUP_ERROR,
                status_code=500,
            )
        return redirect(url_for("admin_services", status="updated"))

    @app.post("/admin/services/<int:service_id>/toggle")
    def admin_services_toggle(service_id: int):
        if redirect_response := require_admin_session():
            return redirect_response

        require_csrf_token()

        service = get_service(service_id)
        if service is None:
            abort(404)

        try:
            toggle_service_active(service_id)
        except sqlite3.OperationalError as exc:
            if not is_missing_services_table_error(exc):
                raise
            return render_admin_services_error(message=SERVICES_SETUP_ERROR, status_code=500)
        return redirect(url_for("admin_services", status="updated"))

    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        if request.method == "GET":
            return render_admin_login()

        require_csrf_token()

        if not admin_credentials_configured(app):
            return render_admin_login()

        username = str(request.form.get("username", "")).strip()
        password = str(request.form.get("password", ""))
        if (
            username != app.config["ADMIN_USERNAME"]
            or password != app.config["ADMIN_PASSWORD"]
        ):
            return render_admin_login(error_message="Invalid credentials")

        session.clear()
        session["is_admin_authenticated"] = True
        return redirect(url_for("admin"))

    @app.post("/admin/logout")
    def admin_logout():
        require_csrf_token()
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
