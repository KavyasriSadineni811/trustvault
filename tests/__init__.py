from flask import Flask

from app.config import Config
from app.extensions import (
    db,
    migrate,
    login_manager,
    csrf,
)


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    # --------------------------------------------------------
    # INITIALIZE EXTENSIONS
    # --------------------------------------------------------

    db.init_app(app)

    migrate.init_app(
        app,
        db
    )

    login_manager.init_app(
        app
    )

    csrf.init_app(
        app
    )

    # --------------------------------------------------------
    # LOGIN CONFIGURATION
    # --------------------------------------------------------

    login_manager.login_view = "auth.login"

    # --------------------------------------------------------
    # USER LOADER
    # --------------------------------------------------------

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):

        return db.session.get(
            User,
            int(user_id)
        )

    # --------------------------------------------------------
    # BLUEPRINTS
    # --------------------------------------------------------

    from app.auth import auth_bp
    from app.documents import documents_bp
    from app.admin import admin_bp

    app.register_blueprint(
        auth_bp
    )

    app.register_blueprint(
        documents_bp
    )

    app.register_blueprint(
        admin_bp
    )

    # --------------------------------------------------------
    # HOME
    # --------------------------------------------------------

    @app.route("/")
    def home():

        return "TrustVault is running"

    return app