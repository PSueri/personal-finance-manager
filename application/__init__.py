import os

import click
from flask import Flask

from application.extensions import csrf, db, migrate
from application.money import format_cents


def create_app(config=None):
    app = Flask(__name__)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY"),
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            "DATABASE_URL",
            "sqlite:///Transazioni_cents.db",
        ),
    )

    if config is not None:
        app.config.update(config)

    if not app.config["SECRET_KEY"]:
        raise RuntimeError("The SECRET_KEY environment variable is not configured.")

    db.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    app.jinja_env.filters["money"] = format_cents

    from application.routes import main_bp

    app.register_blueprint(main_bp)

    @app.cli.command("init-db")
    def init_db():
        """Create missing database tables."""
        db.create_all()
        click.echo("Database tables created.")

    return app
