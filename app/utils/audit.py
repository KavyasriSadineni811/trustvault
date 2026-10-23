from flask import request

from app.extensions import db
from app.models import AuditLog


# ============================================================
# CREATE AUDIT LOG
# ============================================================

def create_audit_log(
    action,
    document_id=None,
    user_id=None,
    details=None
):
    """
    Create a detailed audit-log record.

    Automatically records:
        - timestamp
        - user
        - document
        - action
        - details
        - IP address
        - user-agent
    """

    # ========================================================
    # GET CLIENT IP ADDRESS
    # ========================================================

    ip_address = request.remote_addr

    # ========================================================
    # GET USER-AGENT
    # ========================================================

    user_agent = request.headers.get(
        "User-Agent"
    )

    # ========================================================
    # CREATE AUDIT RECORD
    # ========================================================

    audit_log = AuditLog(
        document_id=document_id,
        user_id=user_id,
        action=action,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent
    )

    # ========================================================
    # ADD TO DATABASE SESSION
    # ========================================================

    db.session.add(audit_log)

    return audit_log