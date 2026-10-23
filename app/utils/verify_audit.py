import hashlib
import hmac
import json

from flask import current_app

from app.extensions import db
from app.models import AuditLog


def _calculate_expected_hash(log):
    """Calculate the expected hash for an audit record."""

    audit_key = current_app.config["AUDIT_LOG_KEY"]

    if not audit_key:
        raise RuntimeError(
            "AUDIT_LOG_KEY is not configured."
        )

    data = {
        "previous_hash": log.previous_hash,
        "document_id": log.document_id,
        "user_id": log.user_id,
        "action": log.action,
        "timestamp": log.timestamp.isoformat(),
        "details": log.details,
    }

    message = json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":")
    ).encode("utf-8")

    return hmac.new(
        audit_key.encode("utf-8"),
        message,
        hashlib.sha256
    ).hexdigest()


def verify_audit_chain():
    """Verify the complete audit-log hash chain."""

    logs = db.session.scalars(
        db.select(AuditLog)
        .order_by(AuditLog.id.asc())
    ).all()

    if not logs:
        return True

    previous_hash = None

    for log in logs:

        # The previous_hash stored in the current
        # record must match the previous record.
        if log.previous_hash != previous_hash:
            return False

        # Existing records without hashes are invalid.
        if not log.record_hash:
            return False

        expected_hash = _calculate_expected_hash(log)

        if not hmac.compare_digest(
            expected_hash,
            log.record_hash
        ):
            return False

        previous_hash = log.record_hash

    return True