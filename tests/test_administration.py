from services.admin_service import (
    can_change_user_status,
    get_all_users,
    get_audit_logs,
)


def test_users_available():

    df = (
        get_all_users()
    )

    assert not df.empty


def test_administrator_exists():

    df = (
        get_all_users()
    )

    assert (
        df[
            "role"
        ]
        .eq(
            "Administrator"
        )
        .any()
    )


def test_user_columns():

    df = (
        get_all_users()
    )

    required = {
        "user_id",
        "full_name",
        "email",
        "status",
        "role",
        "created_at",
    }

    assert required.issubset(
        set(
            df.columns
        )
    )


def test_self_status_change_blocked():

    assert (
        can_change_user_status(
            1,
            1
        )
        is False
    )


def test_other_user_status_change_allowed():

    assert (
        can_change_user_status(
            2,
            1
        )
        is True
    )


def test_audit_dataframe():

    df = (
        get_audit_logs()
    )

    if not df.empty:

        required = {
            "log_id",
            "user",
            "activity",
            "created_at",
        }

        assert required.issubset(
            set(
                df.columns
            )
        )