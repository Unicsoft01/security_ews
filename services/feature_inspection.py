from services.feature_engineering import (
    create_feature_dataset
)


def inspect_features():

    df = create_feature_dataset()

    state = "Kaduna"

    columns = [
        "WEEK",
        "ADMIN1",
        "total_events",
        "total_events_lag_1",
        "total_events_lag_2",
        "total_events_4wk_mean",
        "event_change_1wk",
        "violent_events",
        "high_severity_events",
        "abductions",
        "violent_event_ratio",
    ]

    state_df = (
        df[
            df["ADMIN1"]
            == state
        ][columns]
        .tail(20)
    )

    print(
        state_df.to_string(
            index=False
        )
    )


if __name__ == "__main__":

    inspect_features()