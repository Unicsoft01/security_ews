from services.feature_engineering import (
    create_feature_dataset
)


def test_feature_dataset_not_empty():

    df = create_feature_dataset()

    assert not df.empty


def test_all_states_present():

    df = create_feature_dataset()

    assert (
        df["ADMIN1"].nunique()
        == 37
    )


def test_unique_state_week():

    df = create_feature_dataset()

    duplicates = (
        df.duplicated(
            subset=[
                "ADMIN1",
                "WEEK"
            ]
        )
        .sum()
    )

    assert duplicates == 0


def test_lag_columns_exist():

    df = create_feature_dataset()

    required = [
        "total_events_lag_1",
        "total_events_lag_4",
        "total_fatalities_lag_1",
        "violent_events_lag_1",
        "abductions_lag_1",
    ]

    for column in required:

        assert column in df.columns


def test_rolling_columns_exist():

    df = create_feature_dataset()

    required = [
        "total_events_4wk_mean",
        "total_events_4wk_sum",
        "total_fatalities_4wk_mean",
        "violent_events_4wk_mean",
    ]

    for column in required:

        assert column in df.columns


def test_trend_columns_exist():

    df = create_feature_dataset()

    required = [
        "event_change_1wk",
        "fatality_change_1wk",
        "violent_event_change_1wk",
    ]

    for column in required:

        assert column in df.columns


def test_ratios_are_non_negative():

    df = create_feature_dataset()

    ratio_columns = [
        "violent_event_ratio",
        "high_severity_ratio",
        "battle_ratio",
        "abduction_ratio",
    ]

    for column in ratio_columns:

        assert (
            df[column] >= 0
        ).all()