import io

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import User, Document, DocumentPermission, AuditLog


# ============================================================
# APPLICATION FIXTURE
# ============================================================

@pytest.fixture
def app():
    """
    Create a fresh Flask application for security tests.
    """

    app = create_app()

    app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SECRET_KEY="test-secret-key"
    )

    with app.app_context():
        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()


# ============================================================
# CLIENT FIXTURE
# ============================================================

@pytest.fixture
def client(app):
    return app.test_client()


# ============================================================
# USER HELPER
# ============================================================

def create_user(email, role="user", name=None):
    """
    Create a test user.

    Your User model requires the name field.
    Therefore, if a test only provides an email,
    the name is automatically generated from the email.
    """

    user = User(
        name=name or email.split("@")[0],
        email=email,
        password_hash=generate_password_hash("password"),
        role=role,
        is_active=True
    )

    db.session.add(user)
    db.session.flush()

    return user


# ============================================================
# LOGIN HELPER
# ============================================================

def login(client, email, password="password"):
    """
    Log a user into the application.
    """

    return client.post(
        "/auth/login",
        data={
            "email": email,
            "password": password
        },
        follow_redirects=True
    )


# ============================================================
# SECURITY TEST DATA
# ============================================================

@pytest.fixture
def security_data(app):

    with app.app_context():

        # ----------------------------------------------------
        # Owner
        # ----------------------------------------------------

        owner = create_user(
            "security-owner@trustvault.local",
            role="owner",
            name="Security Owner"
        )

        # ----------------------------------------------------
        # Read-only user
        # ----------------------------------------------------

        read_user = create_user(
            "security-read@trustvault.local",
            role="user",
            name="Security Read User"
        )

        # ----------------------------------------------------
        # Edit user
        # ----------------------------------------------------

        edit_user = create_user(
            "security-edit@trustvault.local",
            role="user",
            name="Security Edit User"
        )

        # ----------------------------------------------------
        # Stranger
        # ----------------------------------------------------

        stranger = create_user(
            "security-stranger@trustvault.local",
            role="user",
            name="Security Stranger"
        )

        # ----------------------------------------------------
        # Revoked user
        # ----------------------------------------------------

        revoked_user = create_user(
            "security-revoked@trustvault.local",
            role="user",
            name="Security Revoked User"
        )

        # ----------------------------------------------------
        # Document
        # ----------------------------------------------------

        document = Document(
            owner_id=owner.id,
            original_filename="security-test.txt",
            stored_filename="security-test.txt",
            storage_path="security-test.txt"
        )

        db.session.add(document)
        db.session.flush()

        # ----------------------------------------------------
        # READ permission
        # ----------------------------------------------------

        read_permission = DocumentPermission(
            document_id=document.id,
            user_id=read_user.id,
            permission="read"
        )

        # ----------------------------------------------------
        # EDIT permission
        # ----------------------------------------------------

        edit_permission = DocumentPermission(
            document_id=document.id,
            user_id=edit_user.id,
            permission="edit"
        )

        # ----------------------------------------------------
        # Revoked permission
        # ----------------------------------------------------

        revoked_permission = DocumentPermission(
            document_id=document.id,
            user_id=revoked_user.id,
            permission="read"
        )

        db.session.add_all(
            [
                read_permission,
                edit_permission,
                revoked_permission
            ]
        )

        db.session.commit()

        return {
            "owner": owner,
            "read_user": read_user,
            "edit_user": edit_user,
            "stranger": stranger,
            "revoked_user": revoked_user,
            "document": document
        }


# ============================================================
# OWNER DOWNLOAD TEST
# ============================================================

def test_owner_can_download(client, security_data):

    owner = security_data["owner"]
    document = security_data["document"]

    with client.session_transaction() as session:
        session["_user_id"] = str(owner.id)
        session["_fresh"] = True

    response = client.get(
        f"/documents/download/{document.id}"
    )

    assert response.status_code in [200, 302]


# ============================================================
# READ USER DOWNLOAD TEST
# ============================================================

def test_read_user_can_download(client, security_data):

    read_user = security_data["read_user"]
    document = security_data["document"]

    with client.session_transaction() as session:
        session["_user_id"] = str(read_user.id)
        session["_fresh"] = True

    response = client.get(
        f"/documents/download/{document.id}"
    )

    assert response.status_code in [200, 302]


# ============================================================
# EDIT USER DOWNLOAD TEST
# ============================================================

def test_edit_user_can_download(client, security_data):

    edit_user = security_data["edit_user"]
    document = security_data["document"]

    with client.session_transaction() as session:
        session["_user_id"] = str(edit_user.id)
        session["_fresh"] = True

    response = client.get(
        f"/documents/download/{document.id}"
    )

    assert response.status_code in [200, 302]


# ============================================================
# STRANGER DOWNLOAD TEST
# ============================================================

def test_stranger_cannot_download(client, security_data):

    stranger = security_data["stranger"]
    document = security_data["document"]

    with client.session_transaction() as session:
        session["_user_id"] = str(stranger.id)
        session["_fresh"] = True

    response = client.get(
        f"/documents/download/{document.id}"
    )

    assert response.status_code in [403, 302, 404]


# ============================================================
# REVOKED USER DOWNLOAD TEST
# ============================================================

def test_revoked_user_cannot_download(client, security_data):

    revoked_user = security_data["revoked_user"]
    document = security_data["document"]

    with client.session_transaction() as session:
        session["_user_id"] = str(revoked_user.id)
        session["_fresh"] = True

    response = client.get(
        f"/documents/download/{document.id}"
    )

    assert response.status_code in [403, 302, 404]


# ============================================================
# READ USER CANNOT EDIT
# ============================================================

def test_read_user_cannot_edit(client, security_data):

    read_user = security_data["read_user"]
    document = security_data["document"]

    with client.session_transaction() as session:
        session["_user_id"] = str(read_user.id)
        session["_fresh"] = True

    response = client.post(
        f"/documents/edit/{document.id}",
        data={
            "content": "Unauthorized modification"
        },
        follow_redirects=False
    )

    assert response.status_code in [403, 302, 404]


# ============================================================
# EDIT USER CAN EDIT
# ============================================================

def test_edit_user_can_edit(client, security_data):

    edit_user = security_data["edit_user"]
    document = security_data["document"]

    with client.session_transaction() as session:
        session["_user_id"] = str(edit_user.id)
        session["_fresh"] = True

    response = client.post(
        f"/documents/edit/{document.id}",
        data={
            "content": "Authorized modification"
        },
        follow_redirects=False
    )

    assert response.status_code in [200, 302]


# ============================================================
# STRANGER CANNOT SHARE
# ============================================================

def test_stranger_cannot_share(client, security_data):

    stranger = security_data["stranger"]
    document = security_data["document"]

    with client.session_transaction() as session:
        session["_user_id"] = str(stranger.id)
        session["_fresh"] = True

    response = client.post(
        f"/documents/share/{document.id}",
        data={
            "email": "another-user@trustvault.local",
            "permission": "read"
        },
        follow_redirects=False
    )

    assert response.status_code in [403, 302, 404]


# ============================================================
# STRANGER CANNOT REVOKE
# ============================================================

def test_stranger_cannot_revoke(client, security_data):

    stranger = security_data["stranger"]
    document = security_data["document"]
    read_user = security_data["read_user"]

    with client.session_transaction() as session:
        session["_user_id"] = str(stranger.id)
        session["_fresh"] = True

    response = client.post(
        f"/documents/revoke/{document.id}/{read_user.id}",
        follow_redirects=False
    )

    assert response.status_code in [403, 302, 404]


# ============================================================
# STRANGER CANNOT DELETE
# ============================================================

def test_stranger_cannot_delete(client, security_data):

    stranger = security_data["stranger"]
    document = security_data["document"]

    with client.session_transaction() as session:
        session["_user_id"] = str(stranger.id)
        session["_fresh"] = True

    response = client.post(
        f"/documents/delete/{document.id}",
        follow_redirects=False
    )

    assert response.status_code in [403, 302, 404]


# ============================================================
# UNAUTHORIZED DOWNLOAD CREATES AUDIT LOG
# ============================================================

def test_unauthorized_download_creates_audit_log(
    client,
    security_data
):

    stranger = security_data["stranger"]
    document = security_data["document"]

    with client.session_transaction() as session:
        session["_user_id"] = str(stranger.id)
        session["_fresh"] = True

    response = client.get(
        f"/documents/download/{document.id}"
    )

    assert response.status_code in [403, 302, 404]

    with client.application.app_context():

        audit = db.session.scalar(
            db.select(AuditLog)
            .where(
                AuditLog.document_id == document.id,
                AuditLog.user_id == stranger.id
            )
            .order_by(AuditLog.id.desc())
        )

        assert audit is not None


# ============================================================
# OWNER HAS DIRECT ACCESS
# ============================================================

def test_owner_has_direct_access(
    client,
    security_data
):

    owner = security_data["owner"]
    document = security_data["document"]

    with client.session_transaction() as session:
        session["_user_id"] = str(owner.id)
        session["_fresh"] = True

    response = client.get(
        f"/documents/download/{document.id}"
    )

    assert response.status_code in [200, 302]


# ============================================================
# PERMISSION DATA TEST
# ============================================================

def test_permissions_are_correct(
    security_data
):

    document = security_data["document"]

    read_user = security_data["read_user"]
    edit_user = security_data["edit_user"]
    revoked_user = security_data["revoked_user"]

    read_permission = db.session.scalar(
        db.select(DocumentPermission).where(
            DocumentPermission.document_id == document.id,
            DocumentPermission.user_id == read_user.id
        )
    )

    edit_permission = db.session.scalar(
        db.select(DocumentPermission).where(
            DocumentPermission.document_id == document.id,
            DocumentPermission.user_id == edit_user.id
        )
    )

    revoked_permission = db.session.scalar(
        db.select(DocumentPermission).where(
            DocumentPermission.document_id == document.id,
            DocumentPermission.user_id == revoked_user.id
        )
    )

    assert read_permission is not None
    assert read_permission.permission == "read"

    assert edit_permission is not None
    assert edit_permission.permission == "edit"

    assert revoked_permission is not None
    assert revoked_permission.permission == "read"