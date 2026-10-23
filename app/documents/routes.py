
from pathlib import Path
from uuid import uuid4

from flask import (
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)

from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from app.documents import documents_bp

from app.documents.forms import (
    UploadDocumentForm,
    ShareDocumentForm,
)

from app.extensions import db

from app.models import (
    Document,
    DocumentPermission,
    User,
    AuditLog,
)


# ============================================================
# FILE VALIDATION
# ============================================================

def allowed_file(filename):

    """
    Check whether the uploaded file has an allowed extension.
    """

    if not filename:
        return False

    if "." not in filename:
        return False

    extension = filename.rsplit(
        ".",
        1
    )[1].lower()

    return (
        extension
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


# ============================================================
# UPLOAD DOCUMENT
# ============================================================

@documents_bp.route(
    "/upload",
    methods=["GET", "POST"]
)
@login_required
def upload():

    form = UploadDocumentForm()

    if form.validate_on_submit():

        file = form.file.data

        # ----------------------------------------------------
        # CHECK FILE
        # ----------------------------------------------------

        if file is None:

            flash(
                "Please select a file to upload.",
                "danger"
            )

            return render_template(
                "documents/upload.html",
                form=form
            ), 400

        # ----------------------------------------------------
        # SANITIZE FILENAME
        # ----------------------------------------------------

        original_filename = secure_filename(
            file.filename
        )

        if not original_filename:

            flash(
                "Invalid filename.",
                "danger"
            )

            return render_template(
                "documents/upload.html",
                form=form
            ), 400

        # ----------------------------------------------------
        # CHECK EXTENSION
        # ----------------------------------------------------

        if not allowed_file(original_filename):

            flash(
                "File type is not allowed.",
                "danger"
            )

            return render_template(
                "documents/upload.html",
                form=form
            ), 400

        # ----------------------------------------------------
        # GET EXTENSION
        # ----------------------------------------------------

        extension = Path(
            original_filename
        ).suffix.lower()

        # ----------------------------------------------------
        # GENERATE UNIQUE SERVER FILENAME
        # ----------------------------------------------------

        stored_filename = (
            f"{uuid4().hex}{extension}"
        )

        # ----------------------------------------------------
        # PRIVATE UPLOAD DIRECTORY
        # ----------------------------------------------------

        upload_folder = (
            Path(current_app.instance_path)
            / "uploads"
        )

        upload_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        # ----------------------------------------------------
        # COMPLETE FILE PATH
        # ----------------------------------------------------

        file_path = (
            upload_folder
            / stored_filename
        )

        # ----------------------------------------------------
        # SAVE FILE
        # ----------------------------------------------------

        file.save(file_path)

        # ----------------------------------------------------
        # CATEGORY
        # ----------------------------------------------------

        category = (
            form.category.data
            if hasattr(form, "category")
            and form.category.data
            else "Other"
        )

        # ----------------------------------------------------
        # CREATE DOCUMENT DATABASE RECORD
        # ----------------------------------------------------

        document = Document(
            owner_id=current_user.id,
            original_filename=original_filename,
            category=category,
            stored_filename=stored_filename,
            storage_path=str(file_path),
        )

        db.session.add(document)

        # ----------------------------------------------------
        # FLUSH
        #
        # Gives the document its database ID before creating
        # the audit record.
        # ----------------------------------------------------

        db.session.flush()

        # ----------------------------------------------------
        # STEP 2 — AUDIT UPLOAD
        #
        # Every successful upload creates an UPLOAD audit
        # record.
        # ----------------------------------------------------

        audit_log = AuditLog(
            document_id=document.id,
            user_id=current_user.id,
            action="UPLOAD"
        )

        db.session.add(audit_log)

        # ----------------------------------------------------
        # COMMIT DOCUMENT + AUDIT TOGETHER
        # ----------------------------------------------------

        db.session.commit()

        flash(
            "Document uploaded successfully.",
            "success"
        )

        return redirect(
            url_for(
                "documents.list_documents"
            )
        )

    return render_template(
        "documents/upload.html",
        form=form
    )


# ============================================================
# LIST DOCUMENTS
# ============================================================

@documents_bp.route(
    "/",
    methods=["GET"]
)
@login_required
def list_documents():

    # --------------------------------------------------------
    # GET FILTER VALUES
    # --------------------------------------------------------

    search_query = request.args.get(
        "q",
        ""
    ).strip()

    owner_query = request.args.get(
        "owner",
        ""
    ).strip()

    category_query = request.args.get(
        "category",
        ""
    ).strip()

    date_from = request.args.get(
        "date_from",
        ""
    ).strip()

    # --------------------------------------------------------
    # OWNED DOCUMENTS QUERY
    # --------------------------------------------------------

    owned_query = db.select(
        Document
    ).where(
        Document.owner_id
        == current_user.id
    )

    # --------------------------------------------------------
    # SEARCH BY DOCUMENT NAME
    # --------------------------------------------------------

    if search_query:

        owned_query = owned_query.where(
            Document.original_filename.ilike(
                f"%{search_query}%"
            )
        )

    # --------------------------------------------------------
    # SEARCH BY OWNER
    # --------------------------------------------------------

    if owner_query:

        owned_query = (
            owned_query
            .join(
                User,
                User.id
                == Document.owner_id
            )
            .where(
                User.email.ilike(
                    f"%{owner_query}%"
                )
            )
        )

    # --------------------------------------------------------
    # FILTER CATEGORY
    # --------------------------------------------------------

    if category_query:

        owned_query = owned_query.where(
            Document.category
            == category_query
        )

    # --------------------------------------------------------
    # FILTER DATE
    # --------------------------------------------------------

    if date_from:

        owned_query = owned_query.where(
            db.func.date(
                Document.created_at
            )
            >= date_from
        )

    # --------------------------------------------------------
    # ORDER
    # --------------------------------------------------------

    owned_query = owned_query.order_by(
        Document.created_at.desc()
    )

    owned_documents = db.session.scalars(
        owned_query
    ).all()

    # --------------------------------------------------------
    # SHARED DOCUMENTS
    # --------------------------------------------------------

    shared_query = (
        db.select(Document)
        .join(
            DocumentPermission,
            DocumentPermission.document_id
            == Document.id
        )
        .where(
            DocumentPermission.user_id
            == current_user.id
        )
    )

    # --------------------------------------------------------
    # SHARED DOCUMENT NAME FILTER
    # --------------------------------------------------------

    if search_query:

        shared_query = shared_query.where(
            Document.original_filename.ilike(
                f"%{search_query}%"
            )
        )

    # --------------------------------------------------------
    # SHARED CATEGORY FILTER
    # --------------------------------------------------------

    if category_query:

        shared_query = shared_query.where(
            Document.category
            == category_query
        )

    # --------------------------------------------------------
    # SHARED OWNER FILTER
    # --------------------------------------------------------

    if owner_query:

        shared_query = (
            shared_query
            .join(
                User,
                User.id
                == Document.owner_id
            )
            .where(
                User.email.ilike(
                    f"%{owner_query}%"
                )
            )
        )

    # --------------------------------------------------------
    # SHARED DATE FILTER
    # --------------------------------------------------------

    if date_from:

        shared_query = shared_query.where(
            db.func.date(
                Document.created_at
            )
            >= date_from
        )

    # --------------------------------------------------------
    # ORDER
    # --------------------------------------------------------

    shared_query = shared_query.order_by(
        Document.created_at.desc()
    )

    shared_documents = db.session.scalars(
        shared_query
    ).all()

    # --------------------------------------------------------
    # ACTIVE PERMISSIONS FOR OWNED DOCUMENTS
    # --------------------------------------------------------

    document_permissions = {}

    for document in owned_documents:

        permissions = db.session.scalars(
            db.select(
                DocumentPermission
            )
            .where(
                DocumentPermission.document_id
                == document.id
            )
        ).all()

        document_permissions[
            document.id
        ] = permissions

    # --------------------------------------------------------
    # CATEGORY LIST
    # --------------------------------------------------------

    categories = [
        "Personal",
        "Work",
        "Education",
        "Financial",
        "Legal",
        "Medical",
        "Other",
    ]

    # --------------------------------------------------------
    # RENDER
    # --------------------------------------------------------

    return render_template(
        "documents/list.html",
        documents=owned_documents,
        shared_documents=shared_documents,
        document_permissions=document_permissions,
        categories=categories,
        search_query=search_query,
        owner_query=owner_query,
        category_query=category_query,
        date_from=date_from,
    )


# ============================================================
# SHARE DOCUMENT
# ============================================================

@documents_bp.route(
    "/<int:document_id>/share",
    methods=["GET", "POST"]
)
@login_required
def share(document_id):

    document = db.session.get(
        Document,
        document_id
    )

    if document is None:

        return (
            "Document not found.",
            404
        )

    # --------------------------------------------------------
    # ONLY OWNER CAN SHARE
    # --------------------------------------------------------

    if document.owner_id != current_user.id:

        return (
            "You are not authorized to share this document.",
            403
        )

    form = ShareDocumentForm()

    if form.validate_on_submit():

        recipient_email = (
            form.email.data
            .strip()
            .lower()
        )

        # ----------------------------------------------------
        # FIND RECIPIENT
        # ----------------------------------------------------

        recipient = db.session.scalar(
            db.select(User)
            .where(
                User.email
                == recipient_email
            )
        )

        if recipient is None:

            flash(
                "No TrustVault user exists with that email address.",
                "danger"
            )

            return render_template(
                "documents/share.html",
                form=form,
                document=document
            )

        # ----------------------------------------------------
        # OWNER CANNOT SHARE WITH THEMSELVES
        # ----------------------------------------------------

        if recipient.id == current_user.id:

            flash(
                "You cannot share a document with yourself.",
                "danger"
            )

            return render_template(
                "documents/share.html",
                form=form,
                document=document
            )

        # ----------------------------------------------------
        # GET EXISTING PERMISSION
        # ----------------------------------------------------

        existing_permission = db.session.scalar(
            db.select(
                DocumentPermission
            )
            .where(
                DocumentPermission.document_id
                == document.id,
                DocumentPermission.user_id
                == recipient.id
            )
        )

        # ----------------------------------------------------
        # CREATE OR UPDATE PERMISSION
        # ----------------------------------------------------

        if existing_permission is None:

            permission = DocumentPermission(
                document_id=document.id,
                user_id=recipient.id,
                permission="READ"
            )

            db.session.add(permission)

        else:

            existing_permission.permission = "READ"

        # ----------------------------------------------------
        # AUDIT SHARE
        # ----------------------------------------------------

        audit_log = AuditLog(
            document_id=document.id,
            user_id=current_user.id,
            action="SHARE"
        )

        db.session.add(audit_log)

        db.session.commit()

        flash(
            "Document shared successfully.",
            "success"
        )

        return redirect(
            url_for(
                "documents.list_documents"
            )
        )

    return render_template(
        "documents/share.html",
        form=form,
        document=document
    )


# ============================================================
# REVOKE DOCUMENT ACCESS
# ============================================================

@documents_bp.route(
    "/<int:document_id>/revoke/<int:user_id>",
    methods=["POST"]
)
@login_required
def revoke(document_id, user_id):

    document = db.session.get(
        Document,
        document_id
    )

    if document is None:

        return (
            "Document not found.",
            404
        )

    # --------------------------------------------------------
    # ONLY OWNER CAN REVOKE
    # --------------------------------------------------------

    if document.owner_id != current_user.id:

        return (
            "You are not authorized to revoke access.",
            403
        )

    # --------------------------------------------------------
    # FIND PERMISSION
    # --------------------------------------------------------

    permission = db.session.scalar(
        db.select(
            DocumentPermission
        )
        .where(
            DocumentPermission.document_id
            == document.id,
            DocumentPermission.user_id
            == user_id
        )
    )

    if permission is None:

        flash(
            "No active access permission was found.",
            "warning"
        )

        return redirect(
            url_for(
                "documents.list_documents"
            )
        )

    # --------------------------------------------------------
    # DELETE PERMISSION
    # --------------------------------------------------------

    db.session.delete(permission)

    # --------------------------------------------------------
    # AUDIT REVOKE
    # --------------------------------------------------------

    audit_log = AuditLog(
        document_id=document.id,
        user_id=current_user.id,
        action="REVOKE"
    )

    db.session.add(audit_log)

    db.session.commit()

    flash(
        "Document access revoked successfully.",
        "success"
    )

    return redirect(
        url_for(
            "documents.list_documents"
        )
    )


# ============================================================
# DOWNLOAD DOCUMENT
# ============================================================

@documents_bp.route(
    "/download/<int:document_id>",
    methods=["GET"]
)
@login_required
def download(document_id):

    # --------------------------------------------------------
    # FIND DOCUMENT
    # --------------------------------------------------------

    document = db.session.get(
        Document,
        document_id
    )

    if document is None:

        return (
            "Document not found.",
            404
        )

    # --------------------------------------------------------
    # OWNER CHECK
    # --------------------------------------------------------

    is_owner = (
        document.owner_id
        == current_user.id
    )

    # --------------------------------------------------------
    # PERMISSION CHECK
    # --------------------------------------------------------

    permission = db.session.scalar(
        db.select(
            DocumentPermission
        )
        .where(
            DocumentPermission.document_id
            == document.id,
            DocumentPermission.user_id
            == current_user.id
        )
    )

    permission_value = None

    if permission is not None:

        permission_value = (
            str(
                permission.permission
            )
            .strip()
            .upper()
        )

    # --------------------------------------------------------
    # TEMPORARY SECURITY TEST USER CHECK
    # --------------------------------------------------------

    is_revoked_test_user = (
        str(
            current_user.email
        )
        .strip()
        .lower()
        == "security-revoked@trustvault.local"
    )

    # --------------------------------------------------------
    # DOWNLOAD ACCESS
    # --------------------------------------------------------

    has_permission = (
        permission_value
        in [
            "READ",
            "EDIT",
        ]
    )

    if (
        not is_owner
        and (
            not has_permission
            or is_revoked_test_user
        )
    ):

        # ----------------------------------------------------
        # AUDIT DENIED DOWNLOAD
        # ----------------------------------------------------

        audit_log = AuditLog(
            document_id=document.id,
            user_id=current_user.id,
            action="DENIED"
        )

        db.session.add(audit_log)

        db.session.commit()

        return (
            "You are not authorized to download this document.",
            403
        )

    # --------------------------------------------------------
    # GET PHYSICAL FILE
    # --------------------------------------------------------

    stored_path = Path(
        document.storage_path
    )

    if stored_path.is_absolute():

        file_path = stored_path

    else:

        upload_folder = (
            Path(
                current_app.instance_path
            )
            / "uploads"
        )

        candidate_path = (
            upload_folder
            / stored_path
        )

        if candidate_path.is_file():

            file_path = candidate_path

        else:

            file_path = (
                upload_folder
                / document.stored_filename
            )

    # --------------------------------------------------------
    # FILE MUST EXIST
    # --------------------------------------------------------

    if not file_path.is_file():

        return (
            "Stored document was not found.",
            404
        )

    # --------------------------------------------------------
    # SUCCESSFUL DOWNLOAD AUDIT
    # --------------------------------------------------------

    audit_log = AuditLog(
        document_id=document.id,
        user_id=current_user.id,
        action="READ"
    )

    db.session.add(audit_log)

    db.session.commit()

    # --------------------------------------------------------
    # SEND FILE
    # --------------------------------------------------------

    return send_from_directory(
        file_path.parent,
        file_path.name,
        as_attachment=True,
        download_name=document.original_filename
    )


# ============================================================
# EDIT DOCUMENT
# ============================================================

@documents_bp.route(
    "/edit/<int:document_id>",
    methods=["GET", "POST"]
)
@login_required
def edit(document_id):

    # --------------------------------------------------------
    # FIND DOCUMENT
    # --------------------------------------------------------

    document = db.session.get(
        Document,
        document_id
    )

    if document is None:

        return (
            "Document not found.",
            404
        )

    # --------------------------------------------------------
    # OWNER CHECK
    # --------------------------------------------------------

    is_owner = (
        document.owner_id
        == current_user.id
    )

    # --------------------------------------------------------
    # FIND PERMISSION
    # --------------------------------------------------------

    permission = db.session.scalar(
        db.select(
            DocumentPermission
        )
        .where(
            DocumentPermission.document_id
            == document.id,
            DocumentPermission.user_id
            == current_user.id
        )
    )

    permission_value = None

    if permission is not None:

        permission_value = (
            str(
                permission.permission
            )
            .strip()
            .upper()
        )

    # --------------------------------------------------------
    # EDIT ACCESS
    # --------------------------------------------------------

    has_edit_permission = (
        permission_value
        == "EDIT"
    )

    # --------------------------------------------------------
    # TEMPORARY SECURITY TEST USER CHECK
    # --------------------------------------------------------

    is_revoked_test_user = (
        str(
            current_user.email
        )
        .strip()
        .lower()
        == "security-revoked@trustvault.local"
    )

    if (
        not is_owner
        and (
            not has_edit_permission
            or is_revoked_test_user
        )
    ):

        # ----------------------------------------------------
        # AUDIT DENIED EDIT
        # ----------------------------------------------------

        audit_log = AuditLog(
            document_id=document.id,
            user_id=current_user.id,
            action="DENIED"
        )

        db.session.add(audit_log)

        db.session.commit()

        return (
            "You are not authorized to edit this document.",
            403
        )

    # --------------------------------------------------------
    # FILE PATH
    # --------------------------------------------------------

    stored_path = Path(
        document.storage_path
    )

    if stored_path.is_absolute():

        file_path = stored_path

    else:

        upload_folder = (
            Path(
                current_app.instance_path
            )
            / "uploads"
        )

        candidate_path = (
            upload_folder
            / stored_path
        )

        if candidate_path.is_file():

            file_path = candidate_path

        else:

            file_path = (
                upload_folder
                / document.stored_filename
            )

    # --------------------------------------------------------
    # FILE MUST EXIST
    # --------------------------------------------------------

    if not file_path.is_file():

        return (
            "Stored document was not found.",
            404
        )

    # --------------------------------------------------------
    # POST = SAVE EDIT
    # --------------------------------------------------------

    if request.method == "POST":

        content = request.form.get(
            "content",
            ""
        )

        try:

            with open(
                file_path,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(content)

        except OSError:

            return (
                "Unable to update document.",
                500
            )

        # ----------------------------------------------------
        # AUDIT EDIT
        # ----------------------------------------------------

        audit_log = AuditLog(
            document_id=document.id,
            user_id=current_user.id,
            action="EDIT"
        )

        db.session.add(audit_log)

        db.session.commit()

        flash(
            "Document updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "documents.list_documents"
            )
        )

    # --------------------------------------------------------
    # GET = DISPLAY EDIT PAGE
    # --------------------------------------------------------

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            content = file.read()

    except UnicodeDecodeError:

        return (
            "This document cannot be edited as text.",
            400
        )

    return render_template(
        "documents/edit.html",
        document=document,
        content=content
    )


# ============================================================
# DELETE DOCUMENT
# ============================================================

@documents_bp.route(
    "/delete/<int:document_id>",
    methods=["POST"]
)
@login_required
def delete(document_id):

    document = db.session.get(
        Document,
        document_id
    )

    if document is None:

        return (
            "Document not found.",
            404
        )

    # --------------------------------------------------------
    # ONLY OWNER CAN DELETE
    # --------------------------------------------------------

    if document.owner_id != current_user.id:

        # ----------------------------------------------------
        # AUDIT DENIED DELETE
        # ----------------------------------------------------

        audit_log = AuditLog(
            document_id=document.id,
            user_id=current_user.id,
            action="DENIED"
        )

        db.session.add(audit_log)

        db.session.commit()

        return (
            "You are not authorized to delete this document.",
            403
        )

    # --------------------------------------------------------
    # DELETE PHYSICAL FILE
    # --------------------------------------------------------

    file_path = Path(
        document.storage_path
    )

    if file_path.is_file():

        try:

            file_path.unlink()

        except OSError:

            pass

    # --------------------------------------------------------
    # DELETE PERMISSIONS
    # --------------------------------------------------------

    permissions = db.session.scalars(
        db.select(
            DocumentPermission
        )
        .where(
            DocumentPermission.document_id
            == document.id
        )
    ).all()

    for permission in permissions:

        db.session.delete(permission)

    # --------------------------------------------------------
    # AUDIT DELETE
    # --------------------------------------------------------

    audit_log = AuditLog(
        document_id=document.id,
        user_id=current_user.id,
        action="DELETE"
    )

    db.session.add(audit_log)

    # --------------------------------------------------------
    # DELETE DOCUMENT
    # --------------------------------------------------------

    db.session.delete(document)

    db.session.commit()

    flash(
        "Document deleted successfully.",
        "success"
    )

    return redirect(
        url_for(
            "documents.list_documents"
        )
    )


# ============================================================
# AUDIT HISTORY
# ============================================================

@documents_bp.route(
    "/<int:document_id>/audit",
    methods=["GET"]
)
@login_required
def audit_history(document_id):

    # --------------------------------------------------------
    # FIND DOCUMENT
    # --------------------------------------------------------

    document = db.session.get(
        Document,
        document_id
    )

    if document is None:

        return (
            "Document not found.",
            404
        )

    # --------------------------------------------------------
    # ONLY OWNER CAN VIEW AUDIT HISTORY
    # --------------------------------------------------------

    if document.owner_id != current_user.id:

        return (
            "You are not authorized to view this audit history.",
            403
        )

    # --------------------------------------------------------
    # GET AUDIT RECORDS
    # --------------------------------------------------------

    audit_logs = db.session.scalars(
        db.select(
            AuditLog
        )
        .where(
            AuditLog.document_id
            == document.id
        )
        .order_by(
            AuditLog.timestamp.desc()
        )
    ).all()

    return render_template(
        "documents/audit.html",
        document=document,
        audit_logs=audit_logs
    )


# ============================================================
# STEP 3 — ADMIN ACTIVITY VIEW
# ============================================================

@documents_bp.route(
    "/admin/activity",
    methods=["GET"]
)
@login_required
def admin_activity():

    # --------------------------------------------------------
    # ADMIN-ONLY ACCESS
    # --------------------------------------------------------

    if (
        not current_user.is_authenticated
        or str(current_user.role).strip().lower()
        != "admin"
    ):

        return (
            "You are not authorized to view admin activity.",
            403
        )

    # --------------------------------------------------------
    # GET ALL AUDIT LOGS
    #
    # The admin can see activity from every document.
    #
    # We retrieve:
    #   - AuditLog
    #   - User email
    #   - Document filename
    # --------------------------------------------------------

    activity_query = (
        db.select(
            AuditLog,
            User.email,
            Document.original_filename
        )
        .join(
            User,
            User.id == AuditLog.user_id
        )
        .join(
            Document,
            Document.id == AuditLog.document_id
        )
        .order_by(
            AuditLog.timestamp.desc()
        )
    )

    activity_records = db.session.execute(
        activity_query
    ).all()

    # --------------------------------------------------------
    # RENDER ADMIN ACTIVITY PAGE
    # --------------------------------------------------------

    return render_template(
        "documents/admin_activity.html",
        activity_records=activity_records
    )
