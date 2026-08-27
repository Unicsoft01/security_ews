from database.connection import (
    SessionLocal
)

from database.models import (
    User
)

from utils.auth import (
    verify_password
)


def authenticate_user(
    email,
    password
):
    """
    Authenticate an active user.

    Returns user information when valid.
    Returns None when authentication fails.
    """

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(
                User.email == email
            )
            .first()
        )

        if user is None:
            return None

        if not user.status:
            return None

        valid_password = (
            verify_password(
                password,
                user.password_hash
            )
        )

        if not valid_password:
            return None

        return {
            "user_id":
                user.user_id,

            "full_name":
                user.full_name,

            "email":
                user.email,

            "role":
                user.role.role_name,
        }

    finally:

        db.close()