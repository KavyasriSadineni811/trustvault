
from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    # ==================================================
    # USER ID
    # ==================================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # ==================================================
    # USER INFORMATION
    # ==================================================

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(255),
        unique=True,
        nullable=False,
        index=True
    )

    # ==================================================
    # PASSWORD
    # ==================================================

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    # ==================================================
    # ROLE
    #
    # Allowed roles:
    # ADMIN
    # OWNER
    # VIEWER
    # ==================================================

    role = db.Column(
        db.String(20),
        nullable=False,
        default="VIEWER"
    )

    # ==================================================
    # ACCOUNT STATUS
    # ==================================================

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    # ==================================================
    # CREATED TIME
    # ==================================================

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    # ==================================================
    # PASSWORD METHODS
    # ==================================================

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(
            self.password_hash,
            password
        )

    # ==================================================
    # ROLE HELPER METHODS
    # ==================================================

    def is_admin(self):
        return self.role == "ADMIN"

    def is_owner(self):
        return self.role == "OWNER"

    def is_viewer(self):
        return self.role == "VIEWER"

    # ==================================================
    # ROLE VALIDATION
    # ==================================================

    def has_valid_role(self):
        return self.role in {
            "ADMIN",
            "OWNER",
            "VIEWER"
        }

    # ==================================================
    # REPRESENTATION
    # ==================================================

    def __repr__(self):
        return (
            f"<User "
            f"id={self.id} "
            f"email={self.email} "
            f"role={self.role}>"
        )
