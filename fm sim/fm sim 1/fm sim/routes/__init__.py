from flask import Flask

from .main import main_bp


def register_routes(app: Flask) -> None:
    app.register_blueprint(main_bp)

