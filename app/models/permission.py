from app.extensions import db


class DocumentPermission(db.Model):

    __tablename__ = "document_permissions"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    document_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "documents.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    permission = db.Column(
        db.String(20),
        nullable=False,
    )

    document = db.relationship(
        "Document",
        backref=db.backref(
            "permissions",
            lazy=True,
            cascade="all, delete-orphan",
        ),
    )

    user = db.relationship(
        "User",
        backref=db.backref(
            "document_permissions",
            lazy=True,
            cascade="all, delete-orphan",
        ),
    )

    __table_args__ = (
        db.UniqueConstraint(
            "document_id",
            "user_id",
            name="uq_document_user_permission",
        ),
    )