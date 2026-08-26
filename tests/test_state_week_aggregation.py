from services.preprocessing import (
    preprocess_nigeria_dataset
)

from services.state_week_aggregation import (
    create_state_week_dataset
)


def test_state_week_not_empty():

    df = (
        create_state_week_dataset()
    )

    assert not df.empty


def test_state_week_locations():

    df = (
        create_state_week_dataset()
    )

    assert (
        df["ADMIN1"].nunique()
        == 37
    )


def test_unique_state_week():

    df = (
        create_state_week_dataset()
    )

    duplicates = (
        df.duplicated(
            subset=[
                "WEEK",
                "ADMIN1"
            ]
        )
        .sum()
    )

    assert duplicates == 0


def test_event_total_preserved():

    clean_df, _ = (
        preprocess_nigeria_dataset()
    )

    state_week = (
        create_state_week_dataset()
    )

    assert (
        state_week[
            "total_events"
        ].sum()
        ==
        clean_df[
            "EVENTS"
        ].sum()
    )


def test_fatality_total_preserved():

    clean_df, _ = (
        preprocess_nigeria_dataset()
    )

    state_week = (
        create_state_week_dataset()
    )

    assert (
        state_week[
            "total_fatalities"
        ].sum()
        ==
        clean_df[
            "FATALITIES"
        ].sum()
    )


def test_no_negative_totals():

    df = (
        create_state_week_dataset()
    )

    assert (
        df[
            "total_events"
        ] >= 0
    ).all()

    assert (
        df[
            "total_fatalities"
        ] >= 0
    ).all()


def test_required_features_exist():

    df = (
        create_state_week_dataset()
    )

    required = [
        "WEEK",
        "ADMIN1",
        "total_events",
        "total_fatalities",
        "battles",
        "violence_against_civilians",
        "explosions_remote_violence",
        "riots",
        "protests",
        "strategic_developments",
        "armed_clashes",
        "attacks",
        "abductions",
    ]

    for column in required:

        assert column in (
            df.columns
        )