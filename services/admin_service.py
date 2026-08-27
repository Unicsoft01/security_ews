import pandas as pd

from database.connection import (
    SessionLocal
)

from database.models import (
    AuditLog,
    Role,
    User
)

from utils.auth import (
    hash_password
)


def get_all_users():
    """
    Retrieve all system users with role information.
    """

    db = SessionLocal()

    try:

        records = (
            db.query(
                User.user_id,
                User.full_name,
                User.email,
                User.status,
                User.created_at,
                Role.role_name,
            )
            .join(
                Role,
                User.role_id
                == Role.role_id
            )
            .order_by(
                User.created_at.desc()
            )
            .all()
        )

        data = [
            {
                "user_id":
                    row[0],

                "full_name":
                    row[1],

                "email":
                    row[2],

                "status":
                    "Active"
                    if row[3]
                    else "Inactive",

                "created_at":
                    row[4],

                "role":
                    row[5],
            }

            for row in records
        ]

        return pd.DataFrame(
            data
        )

    finally:

        db.close()


def create_system_user(
    full_name,
    email,
    password,
    role_name="Analyst"
):
    """
    Create a new system user.
    """

    db = SessionLocal()

    try:

        email = (
            email.strip()
            .lower()
        )

        existing = (
            db.query(
                User
            )
            .filter(
                User.email
                == email
            )
            .first()
        )

        if existing:

            return {
                "success": False,
                "message":
                    "A user with this email "
                    "already exists."
            }

        role = (
            db.query(
                Role
            )
            .filter(
                Role.role_name
                == role_name
            )
            .first()
        )

        if role is None:

            return {
                "success": False,
                "message":
                    f"Role '{role_name}' "
                    "was not found."
            }

        user = User(
            role_id=
                role.role_id,

            full_name=
                full_name.strip(),

            email=
                email,

            password_hash=
                hash_password(
                    password
                ),

            status=True
        )

        db.add(
            user
        )

        db.commit()

        db.refresh(
            user
        )

        return {
            "success": True,
            "message":
                "User created successfully.",
            "user_id":
                user.user_id
        }

    except Exception:

        db.rollback()
        raise

    finally:

        db.close()





def update_user_status(
    user_id,
    active
):
    """
    Activate or deactivate a system user.
    """

    db = SessionLocal()

    try:

        user = (
            db.query(
                User
            )
            .filter(
                User.user_id
                == user_id
            )
            .first()
        )

        if user is None:

            return False

        user.status = bool(
            active
        )

        db.commit()

        return True

    except Exception:

        db.rollback()
        raise

    finally:

        db.close()




def can_change_user_status(
    target_user_id,
    current_user_id
):
    """
    Prevent the currently logged-in administrator
    from disabling their own account.
    """

    return (
        int(target_user_id)
        != int(current_user_id)
    )




def get_audit_logs():
    """
    Retrieve system audit history.
    """

    db = SessionLocal()

    try:

        records = (
            db.query(
                AuditLog.log_id,
                AuditLog.user_id,
                User.full_name,
                User.email,
                AuditLog.activity,
                AuditLog.created_at,
            )
            .outerjoin(
                User,
                AuditLog.user_id
                == User.user_id
            )
            .order_by(
                AuditLog.created_at.desc()
            )
            .all()
        )

        data = [
            {
                "log_id":
                    row[0],

                "user_id":
                    row[1],

                "user":
                    row[2]
                    or "System",

                "email":
                    row[3]
                    or "",

                "activity":
                    row[4],

                "created_at":
                    row[5],
            }

            for row in records
        ]

        return pd.DataFrame(
            data
        )

    finally:

        db.close()