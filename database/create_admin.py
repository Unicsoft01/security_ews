from database.connection import SessionLocal
from database.repositories import (
    create_user,
    get_role_by_name,
    get_user_by_email
)
from utils.auth import hash_password


ADMIN_EMAIL = (
    "admin@securityews.local"
)

ADMIN_PASSWORD = (
    "Admin2026!"
)


def create_admin():

    db = SessionLocal()

    try:

        existing = (
            get_user_by_email(
                db,
                ADMIN_EMAIL
            )
        )

        if existing:

            print(
                "Administrator already exists."
            )

            return

        role = get_role_by_name(
            db,
            "Administrator"
        )

        if not role:

            raise RuntimeError(
                "Administrator role "
                "does not exist."
            )

        password_hash = (
            hash_password(
                ADMIN_PASSWORD
            )
        )

        user = create_user(
            db=db,
            role_id=role.role_id,
            full_name=
                "System Administrator",
            email=ADMIN_EMAIL,
            password_hash=
                password_hash
        )

        print(
            "Administrator created."
        )

        print(
            f"Email: {user.email}"
        )

    finally:

        db.close()


if __name__ == "__main__":
    create_admin()