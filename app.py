from flask import Flask, render_template

from config import Config
from database.db import close_connection, init_db


def create_app(config_overrides: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(Config.from_env().to_flask_config())

    if config_overrides:
        app.config.update(config_overrides)

    app.teardown_appcontext(close_connection)

    @app.get("/")
    def landing():
        return render_template("landing.html")

    @app.get("/admin")
    def admin():
        return render_template("admin.html")

    @app.cli.command("init-db")
    def init_db_command():
        init_db(app)
        print("Initialized the BrandLaunch database.")

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
