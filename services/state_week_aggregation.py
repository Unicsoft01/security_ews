from pathlib import Path

import pandas as pd

from services.preprocessing import (
    preprocess_nigeria_dataset
)


OUTPUT_PATH = Path(
    "data/processed/"
    "acled_nigeria_state_week.csv"
)


EVENT_TYPE_MAP = {
    "Battles":
        "battles",

    "Violence against civilians":
        "violence_against_civilians",

    "Explosions/Remote violence":
        "explosions_remote_violence",

    "Riots":
        "riots",

    "Protests":
        "protests",

    "Strategic developments":
        "strategic_developments",
}


SUB_EVENT_TYPE_MAP = {
    "Armed clash":
        "armed_clashes",

    "Attack":
        "attacks",

    "Abduction/forced disappearance":
        "abductions",

    "Remote explosive/land mine/IED":
        "remote_explosives_ied",

    "Air/drone strike":
        "air_drone_strikes",

    "Suicide bomb":
        "suicide_bombs",

    "Mob violence":
        "mob_violence",

    "Violent demonstration":
        "violent_demonstrations",
}


def create_base_state_week(df):
    """
    Create one base row per state and week.
    """

    state_week = (
        df.groupby(
            [
                "WEEK",
                "ADMIN1"
            ],
            as_index=False
        )
        .agg(
            total_events=(
                "EVENTS",
                "sum"
            ),

            total_fatalities=(
                "FATALITIES",
                "sum"
            ),

            latitude=(
                "CENTROID_LATITUDE",
                "first"
            ),

            longitude=(
                "CENTROID_LONGITUDE",
                "first"
            )
        )
    )

    return state_week


def create_event_type_features(df):
    """
    Aggregate ACLED EVENT_TYPE values for each
    state-week.
    """

    event_data = (
        df[
            df["EVENT_TYPE"].isin(
                EVENT_TYPE_MAP.keys()
            )
        ]
        .groupby(
            [
                "WEEK",
                "ADMIN1",
                "EVENT_TYPE"
            ]
        )["EVENTS"]
        .sum()
        .unstack(
            fill_value=0
        )
        .reset_index()
    )

    event_data = (
        event_data.rename(
            columns=EVENT_TYPE_MAP
        )
    )

    # Ensure every expected column exists
    for output_column in (
        EVENT_TYPE_MAP.values()
    ):

        if output_column not in (
            event_data.columns
        ):

            event_data[
                output_column
            ] = 0

    return event_data


def create_sub_event_features(df):
    """
    Aggregate selected ACLED SUB_EVENT_TYPE
    categories for each state-week.
    """

    sub_event_data = (
        df[
            df["SUB_EVENT_TYPE"].isin(
                SUB_EVENT_TYPE_MAP.keys()
            )
        ]
        .groupby(
            [
                "WEEK",
                "ADMIN1",
                "SUB_EVENT_TYPE"
            ]
        )["EVENTS"]
        .sum()
        .unstack(
            fill_value=0
        )
        .reset_index()
    )

    sub_event_data = (
        sub_event_data.rename(
            columns=SUB_EVENT_TYPE_MAP
        )
    )

    for output_column in (
        SUB_EVENT_TYPE_MAP.values()
    ):

        if output_column not in (
            sub_event_data.columns
        ):

            sub_event_data[
                output_column
            ] = 0

    return sub_event_data


def create_state_week_dataset():
    """
    Generate the observed state-week analytical
    dataset from cleaned ACLED Nigeria data.
    """

    clean_df, _ = (
        preprocess_nigeria_dataset()
    )

    base = create_base_state_week(
        clean_df
    )

    event_features = (
        create_event_type_features(
            clean_df
        )
    )

    sub_event_features = (
        create_sub_event_features(
            clean_df
        )
    )

    state_week = (
        base.merge(
            event_features,
            on=[
                "WEEK",
                "ADMIN1"
            ],
            how="left"
        )
    )

    state_week = (
        state_week.merge(
            sub_event_features,
            on=[
                "WEEK",
                "ADMIN1"
            ],
            how="left"
        )
    )

    count_columns = [
        "battles",
        "violence_against_civilians",
        "explosions_remote_violence",
        "riots",
        "protests",
        "strategic_developments",
        "armed_clashes",
        "attacks",
        "abductions",
        "remote_explosives_ied",
        "air_drone_strikes",
        "suicide_bombs",
        "mob_violence",
        "violent_demonstrations",
    ]

    for column in count_columns:

        state_week[column] = (
            state_week[column]
            .fillna(0)
            .astype(int)
        )

    state_week[
        "violent_events"
    ] = (
        state_week["battles"]
        + state_week["violence_against_civilians"]
        + state_week["explosions_remote_violence"]
    )

    state_week[
        "high_severity_events"
    ] = (
        state_week["armed_clashes"]
        + state_week["attacks"]
        + state_week["abductions"]
        + state_week["remote_explosives_ied"]
        + state_week["suicide_bombs"]
    )

    state_week[
        "total_events"
    ] = (
        state_week[
            "total_events"
        ]
        .astype(int)
    )

    state_week[
        "total_fatalities"
    ] = (
        state_week[
            "total_fatalities"
        ]
        .astype(int)
    )

    state_week = (
        state_week.sort_values(
            [
                "ADMIN1",
                "WEEK"
            ]
        )
        .reset_index(
            drop=True
        )
    )

    return state_week


def save_state_week_dataset(
    df
):

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    return OUTPUT_PATH


if __name__ == "__main__":

    df = create_state_week_dataset()

    output = (
        save_state_week_dataset(
            df
        )
    )

    print(
        "\nSTATE-WEEK AGGREGATION COMPLETE"
    )

    print("=" * 60)

    print(
        f"State-week records: "
        f"{len(df):,}"
    )

    print(
        f"States/FCT: "
        f"{df['ADMIN1'].nunique()}"
    )

    print(
        f"Earliest week: "
        f"{df['WEEK'].min()}"
    )

    print(
        f"Latest week: "
        f"{df['WEEK'].max()}"
    )

    print(
        f"Total represented events: "
        f"{df['total_events'].sum():,}"
    )

    print(
        f"Total fatalities: "
        f"{df['total_fatalities'].sum():,}"
    )

    print(
        f"\nSaved to: {output}"
    )