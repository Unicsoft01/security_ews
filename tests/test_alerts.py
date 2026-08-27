from services.alert_service import (
    build_alert_message,
    get_latest_alerts,
)


def test_high_alert_message():

    message = (
        build_alert_message(
            "Kaduna",
            "High",
            "2026-08-15",
            0.85
        )
    )

    assert message is not None

    assert (
        "HIGH-RISK WARNING"
        in message
    )


def test_medium_alert_message():

    message = (
        build_alert_message(
            "Kaduna",
            "Medium",
            "2026-08-15",
            0.70
        )
    )

    assert (
        "MONITORING WARNING"
        in message
    )


def test_low_does_not_create_warning():

    message = (
        build_alert_message(
            "Kaduna",
            "Low",
            "2026-08-15",
            0.80
        )
    )

    assert message is None


def test_latest_alerts_structure():

    df = (
        get_latest_alerts()
    )

    if not df.empty:

        assert (
            "state"
            in df.columns
        )

        assert (
            "alert_level"
            in df.columns
        )

        assert (
            "message"
            in df.columns
        )