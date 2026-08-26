from database.connection import SessionLocal
from database.models import Role


DEFAULT_ROLES = [
    {
        "role_name": "Administrator",
        "description":
            "Full system administration access."
    },
    {
        "role_name": "Analyst",
        "description":
            "Security analysis and reporting access."
    },
]


def seed_roles():

    db = SessionLocal()

    try:

        for role_data in DEFAULT_ROLES:

            existing = (
                db.query(Role)
                .filter(
                    Role.role_name
                    == role_data["role_name"]
                )
                .first()
            )

            if existing:
                continue

            role = Role(
                **role_data
            )

            db.add(role)

        db.commit()

        print(
            "Default roles created successfully."
        )

    except Exception:

        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_roles()