from datetime import datetime, timezone

from app.extensions import db


class Document(db.Model):

    __tablename__ = "documents"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    owner_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    original_filename = db.Column(
        db.String(255),
        nullable=False,
    )

    stored_filename = db.Column(
        db.String(255),
        nullable=False,
        unique=True,
    )

    storage_path = db.Column(
        db.String(1000),
        nullable=False,
    )

    # --------------------------------------------------------
    # DOCUMENT CATEGORY
    # --------------------------------------------------------

    category = db.Column(
        db.String(100),
        nullable=False,
        default="Other",
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    owner = db.relationship(
        "User",
        backref=db.backref(
            "documents",
            lazy=True,
        ),
    )