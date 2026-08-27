from database.connection import (
    SessionLocal
)

from database.repositories import (
    create_user,
    get_role_by_name,
    get_user_by_email
)

from utils.auth import (
    hash_password
)


ANALYST_EMAIL = (
    "analyst@securityews.local"
)

ANALYST_PASSWORD = (
    "Analyst2026!"
)


def create_analyst():

    db = SessionLocal()

    try:

        existing = (
            get_user_by_email(
                db,
                ANALYST_EMAIL
            )
        )

        if existing:

            print(
                "Analyst already exists."
            )

            return

        role = get_role_by_name(
            db,
            "Analyst"
        )

        if not role:

            raise RuntimeError(
                "Analyst role not found."
            )

        user = create_user(
            db=db,
            role_id=
                role.role_id,
            full_name=
                "Security Analyst",
            email=
                ANALYST_EMAIL,
            password_hash=
                hash_password(
                    ANALYST_PASSWORD
                )
        )

        print(
            "Analyst created successfully."
        )

        print(
            f"Email: {user.email}"
        )

    finally:

        db.close()


if __name__ == "__main__":

    create_analyst()