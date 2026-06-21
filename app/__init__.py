from flask import Flask
from flask_migrate import Migrate
from flask_migrate import upgrade

from app.config import Config
from app.models import db


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    Migrate(app, db)

    with app.app_context():
        upgrade()

    from app.routes import register_blueprints
    register_blueprints(app)

    @app.cli.command("init-db")
    def init_db_command() -> None:
        db.create_all()
        print("Initialized the database.")

    return app
