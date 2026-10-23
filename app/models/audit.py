
from datetime import datetime, timezone

from app.extensions import db


class AuditLog(db.Model):

    __tablename__ = "audit_logs"

    # ========================================================
    # PRIMARY KEY
    # ========================================================

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    # ========================================================
    # DOCUMENT
    # ========================================================

    document_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "documents.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    # ========================================================
    # USER WHO PERFORMED THE ACTION
    # ========================================================

    user_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    # ========================================================
    # ACTION
    # ========================================================

    action = db.Column(
        db.String(50),
        nullable=False,
    )

    # ========================================================
    # TIMESTAMP
    # ========================================================

    timestamp = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ========================================================
    # RELATIONSHIPS
    # ========================================================

    document = db.relationship(
        "Document",
        backref=db.backref(
            "audit_logs",
            lazy=True,
        ),
    )

    user = db.relationship(
        "User",
        backref=db.backref(
            "audit_logs",
            lazy=True,
        ),
    )
