from services.dashboard_service import (
    get_dashboard_summary,
    get_events_by_state,
    get_weekly_event_trend,
)


def test_dashboard_summary():

    summary = (
        get_dashboard_summary()
    )

    assert (
        summary[
            "represented_events"
        ] >= 0
    )

    assert (
        summary[
            "locations"
        ] == 37
    )


def test_events_by_state():

    data = (
        get_events_by_state()
    )

    assert len(data) == 37


def test_weekly_trend():

    data = (
        get_weekly_event_trend()
    )

    assert len(data) > 0