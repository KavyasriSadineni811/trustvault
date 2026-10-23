from flask import current_app

from app.extensions import db
from app.models import AuditLog

from app.utils.audit import _calculate_hash


def backfill_audit_hashes():

    logs = db.session.scalars(
        db.select(AuditLog)
        .order_by(AuditLog.id.asc())
    ).all()

    if not logs:
        print("No audit records found.")
        return

    previous_hash = None

    for log in logs:

        log.previous_hash = previous_hash

        log.record_hash = _calculate_hash(
            previous_hash=log.previous_hash,
            document_id=log.document_id,
            user_id=log.user_id,
            action=log.action,
            timestamp=log.timestamp,
            details=log.details
        )

        previous_hash = log.record_hash

        print(
            f"Updated audit record "
            f"{log.id}: {log.action}"
        )

    db.session.commit()

    print(
        f"Successfully backfilled "
        f"{len(logs)} audit records."
    )