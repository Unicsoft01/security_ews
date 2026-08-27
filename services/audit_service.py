from database.connection import (
    SessionLocal
)

from database.models import (
    AuditLog
)


def log_activity(
    user_id,
    activity
):
    """
    Record a user's activity in the
    system audit log.
    """

    db = SessionLocal()

    try:

        audit_log = AuditLog(
            user_id=user_id,
            activity=activity
        )

        db.add(
            audit_log
        )

        db.commit()

        db.refresh(
            audit_log
        )

        return audit_log

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()