from services.auth_service import (
    authenticate_user
)


def test_admin_authentication():

    user = authenticate_user(
        "admin@securityews.local",
        "Admin2026!"
    )

    assert user is not None

    assert (
        user["role"]
        == "Administrator"
    )


def test_wrong_password():

    user = authenticate_user(
        "admin@securityews.local",
        "WrongPassword"
    )

    assert user is None


def test_unknown_user():

    user = authenticate_user(
        "nobody@example.com",
        "Password123"
    )

    assert user is None