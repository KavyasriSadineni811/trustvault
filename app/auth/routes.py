from flask import (
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
)

from werkzeug.security import check_password_hash

from app.auth import auth_bp
from app.auth.forms import LoginForm
from app.extensions import db
from app.models import User


# ============================================================
# LOGIN
# ============================================================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    # --------------------------------------------------------
    # ALREADY LOGGED IN
    # --------------------------------------------------------

    if current_user.is_authenticated:

        if current_user.role == "admin":
            return redirect(
                url_for("admin.dashboard")
            )

        return redirect(
            url_for("documents.list_documents")
        )

    # --------------------------------------------------------
    # LOGIN FORM
    # --------------------------------------------------------

    form = LoginForm()

    if form.validate_on_submit():

        email = (
            form.email.data
            .strip()
            .lower()
        )

        password = form.password.data

        # ----------------------------------------------------
        # FIND USER
        # ----------------------------------------------------

        user = db.session.scalar(
            db.select(User).where(
                User.email == email
            )
        )

        # ----------------------------------------------------
        # CHECK USER + PASSWORD
        # ----------------------------------------------------

        if (
            user is None
            or not user.is_active
            or not check_password_hash(
                user.password_hash,
                password
            )
        ):

            flash(
                "Invalid email or password.",
                "danger"
            )

            return render_template(
                "auth/login.html",
                form=form
            )

        # ----------------------------------------------------
        # LOGIN USER
        # ----------------------------------------------------

        login_user(user)

        # ----------------------------------------------------
        # ROLE-BASED REDIRECT
        # ----------------------------------------------------

        if user.role == "admin":

            return redirect(
                url_for(
                    "admin.dashboard"
                )
            )

        elif user.role in [
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

        logout_user()

        flash(
            "Your account has an invalid role.",
            "danger"
        )

        return redirect(
            url_for("auth.login")
        )

    # --------------------------------------------------------
    # SHOW LOGIN PAGE
    # --------------------------------------------------------

    return render_template(
        "auth/login.html",
        form=form
    )


# ============================================================
# LOGOUT
# ============================================================

@auth_bp.route(
    "/logout",
    methods=["POST"]
)
@login_required
def logout():

    logout_user()

    flash(
        "You have been logged out successfully.",
        "success"
    )

    return redirect(
        url_for("auth.login")
    )