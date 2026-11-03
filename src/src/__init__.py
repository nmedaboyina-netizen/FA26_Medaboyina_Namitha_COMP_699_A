

from pathlib import Path
from flask import Flask

from config import SECRET_KEY
from src.database.db import init_app, init_db

from src.routes.dashboard import bp as dashboard_bp
from src.routes.events import bp as events_bp
from src.routes.constraints import bp as constraints_bp
from src.routes.analysis import bp as analysis_bp
from src.routes.datasets import bp as datasets_bp


# Get the main project directory
BASE_DIR = Path(__file__).resolve().parent.parent


def create_app(test_config=None):

    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
        static_url_path="/static"
    )

    app.config["SECRET_KEY"] = SECRET_KEY

    if test_config:
        app.config.update(test_config)

    # Initialize database
    init_app(app)

    with app.app_context():
        init_db()

    # Register application routes
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(constraints_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(datasets_bp)

    return app
