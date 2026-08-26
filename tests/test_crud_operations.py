from database.connection import SessionLocal
from database.repositories import (
    create_user,
    delete_user,
    get_role_by_name,
    get_user_by_email,
    update_user_status
)
from utils.auth import hash_password


TEST_EMAIL = (
    "testuser@example.com"
)


def test_user_crud():

    db = SessionLocal()

    try:

        # CLEAN OLD TEST USER
        old_user = (
            get_user_by_email(
                db,
                TEST_EMAIL
            )
        )

        if old_user:
            delete_user(
                db,
                old_user.user_id
            )

        # ------------------------
        # CREATE
        # ------------------------

        analyst_role = (
            get_role_by_name(
                db,
                "Analyst"
            )
        )

        assert analyst_role is not None

        password_hash = (
            hash_password(
                "TestPassword123!"
            )
        )

        new_user = create_user(
            db=db,
            role_id=analyst_role.role_id,
            full_name="Test User",
            email=TEST_EMAIL,
            password_hash=password_hash
        )

        assert new_user is not None
        assert (
            new_user.email
            == TEST_EMAIL
        )

        # ------------------------
        # READ
        # ------------------------

        retrieved_user = (
            get_user_by_email(
                db,
                TEST_EMAIL
            )
        )

        assert retrieved_user is not None

        assert (
            retrieved_user.full_name
            == "Test User"
        )

        # ------------------------
        # UPDATE
        # ------------------------

        updated_user = (
            update_user_status(
                db,
                retrieved_user.user_id,
                False
            )
        )

        assert (
            updated_user.status
            is False
        )

        # ------------------------
        # DELETE
        # ------------------------

        deleted = delete_user(
            db,
            updated_user.user_id
        )

        assert deleted is True

        final_user = (
            get_user_by_email(
                db,
                TEST_EMAIL
            )
        )

        assert final_user is None

    finally:

        db.close()
        