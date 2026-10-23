
from flask import render_template, redirect, url_for
from flask_login import current_user, login_required

from app.admin import admin_bp
from app.extensions import db
from app.models import User, Document, AuditLog, DocumentPermission


# ============================================================
# ADMIN ACCESS CONTROL
# ============================================================

def admin_required():

    if not current_user.is_authenticated:

        return redirect(
            url_for("auth.login")
        )

    if current_user.role != "admin":

        return (
            "You are not authorized to access the admin dashboard.",
            403
        )

    return None


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@admin_bp.route(
    "/",
    methods=["GET"]
)
@login_required
def dashboard():

    # --------------------------------------------------------
    # CHECK ADMIN ROLE
    # --------------------------------------------------------

    access_error = admin_required()

    if access_error is not None:

        return access_error

    # --------------------------------------------------------
    # GET ALL AUDIT LOGS
    # --------------------------------------------------------

    audit_logs = db.session.scalars(
        db.select(AuditLog)
        .order_by(
            AuditLog.timestamp.desc()
        )
    ).all()

    # --------------------------------------------------------
    # GET ALL USERS
    # --------------------------------------------------------

    users = db.session.scalars(
        db.select(User)
        .order_by(
            User.created_at.desc()
        )
    ).all()

    # --------------------------------------------------------
    # GET ALL DOCUMENTS
    # --------------------------------------------------------

    documents = db.session.scalars(
        db.select(Document)
        .order_by(
            Document.created_at.desc()
        )
    ).all()

    # --------------------------------------------------------
    # GET ALL ACTIVE PERMISSIONS
    # --------------------------------------------------------

    permissions = db.session.scalars(
        db.select(DocumentPermission)
    ).all()

    # --------------------------------------------------------
    # DASHBOARD COUNTS
    # --------------------------------------------------------

    total_users = len(users)

    total_documents = len(documents)

    total_permissions = len(permissions)

    total_audit_logs = len(audit_logs)

    # --------------------------------------------------------
    # RENDER ADMIN DASHBOARD
    # --------------------------------------------------------

    return render_template(
        "admin/dashboard.html",

        audit_logs=audit_logs,

        users=users,

        documents=documents,

        permissions=permissions,

        total_users=total_users,

        total_documents=total_documents,

        total_permissions=total_permissions,

        total_audit_logs=total_audit_logs,
    )


# ============================================================
# ADMIN PERMISSIONS VIEW
# ============================================================

@admin_bp.route(
    "/permissions",
    methods=["GET"]
)
@login_required
def permissions_view():

    # --------------------------------------------------------
    # CHECK ADMIN ROLE
    # --------------------------------------------------------

    access_error = admin_required()

    if access_error is not None:

        return access_error

    # --------------------------------------------------------
    # GET ALL PERMISSIONS
    # --------------------------------------------------------

    permissions = db.session.scalars(
        db.select(DocumentPermission)
    ).all()

    # --------------------------------------------------------
    # RENDER
    # --------------------------------------------------------

    return render_template(
        "admin/permissions.html",
        permissions=permissions
    )
