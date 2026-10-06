import os

from flask import Flask

from application.extensions import db, csrf


def create_app(config=None):
    app = Flask(__name__)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY"),
        SQLALCHEMY_DATABASE_URI="sqlite:///Transazioni.db",
    )

    if config is not None:
        app.config.update(config)

    if not app.config["SECRET_KEY"]:
        raise RuntimeError(
            "The SECRET_KEY environment variable is not configured."
        )

    db.init_app(app)
    csrf.init_app(app)

    from application.routes import main_bp

    app.register_blueprint(main_bp)

    return app