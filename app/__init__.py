
from flask import Flask, redirect, url_for
from flask_login import current_user

from app.config import Config

from app.extensions import (
    db,
    migrate,
    login_manager,
    csrf,
)


# ============================================================
# CREATE APPLICATION
# ============================================================

def create_app(config_class=Config):

    app = Flask(__name__)

    # --------------------------------------------------------
    # LOAD CONFIGURATION
    # --------------------------------------------------------

    app.config.from_object(config_class)

    # --------------------------------------------------------
    # INITIALIZE EXTENSIONS
    # --------------------------------------------------------

    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)

    csrf.init_app(app)

    # --------------------------------------------------------
    # LOGIN CONFIGURATION
    # --------------------------------------------------------

    login_manager.login_view = "auth.login"

    # --------------------------------------------------------
    # USER LOADER
    # --------------------------------------------------------

    @login_manager.user_loader
    def load_user(user_id):

        from app.models import User

        return db.session.get(
            User,
            int(user_id)
        )

    # --------------------------------------------------------
    # REGISTER AUTH BLUEPRINT
    # --------------------------------------------------------

    from app.auth import auth_bp

    app.register_blueprint(
        auth_bp,
        url_prefix="/auth"
    )

    # --------------------------------------------------------
    # REGISTER DOCUMENTS BLUEPRINT
    # --------------------------------------------------------

    from app.documents import documents_bp

    app.register_blueprint(
        documents_bp,
        url_prefix="/documents"
    )

    # --------------------------------------------------------
    # REGISTER ADMIN BLUEPRINT
    # --------------------------------------------------------

    from app.admin import admin_bp

    app.register_blueprint(
        admin_bp,
        url_prefix="/admin"
    )

    # --------------------------------------------------------
    # HOME ROUTE
    # --------------------------------------------------------

    @app.route("/")
    def home():

        # ----------------------------------------------------
        # NOT LOGGED IN
        # ----------------------------------------------------

        if not current_user.is_authenticated:

            return redirect(
                url_for(
                    "auth.login"
                )
            )

        # ----------------------------------------------------
        # ADMIN
        # ----------------------------------------------------

        if current_user.role == "admin":

            return redirect(
                url_for(
                    "admin.dashboard"
                )
            )

        # ----------------------------------------------------
        # OWNER / VIEWER
        # ----------------------------------------------------

        if current_user.role in [
            "owner",
            "viewer",
        ]:

            return redirect(
                url_for(
                    "documents.list_documents"
                )
            )

        # ----------------------------------------------------
        # UNKNOWN ROLE
        # ----------------------------------------------------

        return (
            "Invalid user role.",
            403
        )

    # --------------------------------------------------------
    # RETURN APPLICATION
    # --------------------------------------------------------

    return app
