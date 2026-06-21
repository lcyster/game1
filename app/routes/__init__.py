from flask import Flask

from app.routes.health import health_blueprint
from app.routes.pages import pages_blueprint
from app.routes.api import api_blueprint


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(pages_blueprint)
    app.register_blueprint(api_blueprint)
    app.register_blueprint(health_blueprint)
