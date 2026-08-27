from pathlib import Path

import numpy as np
import pandas as pd

from config.settings import (
    MODEL_START_DATE,
    MODEL_END_DATE,
)

from services.state_week_aggregation import (
    create_state_week_dataset,
)


OUTPUT_PATH = Path(
    "data/processed/"
    "acled_nigeria_state_week_features.csv"
)


COUNT_COLUMNS = [
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
    "remote_explosives_ied",
    "air_drone_strikes",
    "suicide_bombs",
    "mob_violence",
    "violent_demonstrations",
    "violent_events",
    "high_severity_events",
]

def create_complete_state_week_panel(df):
    """
    Create one row for every Nigerian state/FCT
    for every week in the modelling period.
    """

    df = df.copy()

    df["WEEK"] = pd.to_datetime(
        df["WEEK"]
    )

    start_date = pd.to_datetime(
        MODEL_START_DATE
    )

    end_date = pd.to_datetime(
        MODEL_END_DATE
    )

    # Keep only modelling period
    df = df[
        (df["WEEK"] >= start_date)
        &
        (df["WEEK"] <= end_date)
    ].copy()

    states = sorted(
        df["ADMIN1"].unique()
    )

    # ACLED weekly dates in this dataset
    # are Saturdays.
    weeks = pd.date_range(
        start=start_date,
        end=end_date,
        freq="W-SAT"
    )

    complete_index = (
        pd.MultiIndex.from_product(
            [
                states,
                weeks
            ],
            names=[
                "ADMIN1",
                "WEEK"
            ]
        )
    )

    panel = (
        df.set_index(
            [
                "ADMIN1",
                "WEEK"
            ]
        )
        .reindex(
            complete_index
        )
        .reset_index()
    )

    # Recover coordinates for synthetic zero weeks
    coordinates = (
        df.groupby(
            "ADMIN1",
            as_index=False
        )
        .agg(
            latitude=(
                "latitude",
                "first"
            ),
            longitude=(
                "longitude",
                "first"
            )
        )
    )

    panel = (
        panel.drop(
            columns=[
                "latitude",
                "longitude"
            ],
            errors="ignore"
        )
        .merge(
            coordinates,
            on="ADMIN1",
            how="left"
        )
    )

    # Missing state-week event counts mean
    # zero recorded events for that weekly panel.
    for column in COUNT_COLUMNS:

        if column in panel.columns:

            panel[column] = (
                panel[column]
                .fillna(0)
                .astype(int)
            )

    panel = panel.sort_values(
        [
            "ADMIN1",
            "WEEK"
        ]
    ).reset_index(
        drop=True
    )

    return panel


def add_time_features(df):

    df = df.copy()

    df["year"] = (
        df["WEEK"].dt.year
    )

    df["month"] = (
        df["WEEK"].dt.month
    )

    df["quarter"] = (
        df["WEEK"].dt.quarter
    )

    df["week_of_year"] = (
        df["WEEK"]
        .dt.isocalendar()
        .week
        .astype(int)
    )

    return df



def add_lag_features(df):

    df = df.copy()

    df = df.sort_values(
        [
            "ADMIN1",
            "WEEK"
        ]
    )

    grouped = df.groupby(
        "ADMIN1"
    )

    lag_source_columns = [
        "total_events",
        "total_fatalities",
        "violent_events",
        "high_severity_events",
        "battles",
        "violence_against_civilians",
        "abductions",
        "explosions_remote_violence",
    ]

    for column in lag_source_columns:

        for lag in [
            1,
            2,
            3,
            4
        ]:

            df[
                f"{column}_lag_{lag}"
            ] = (
                grouped[column]
                .shift(lag)
            )

    return df




def add_rolling_features(df):

    df = df.copy()

    df = df.sort_values(
        [
            "ADMIN1",
            "WEEK"
        ]
    )

    rolling_columns = [
        "total_events",
        "total_fatalities",
        "violent_events",
        "high_severity_events",
        "abductions",
    ]

    for column in rolling_columns:

        df[
            f"{column}_4wk_mean"
        ] = (
            df.groupby(
                "ADMIN1"
            )[column]
            .transform(
                lambda x:
                    x.rolling(
                        window=4,
                        min_periods=1
                    ).mean()
            )
        )

        df[
            f"{column}_4wk_sum"
        ] = (
            df.groupby(
                "ADMIN1"
            )[column]
            .transform(
                lambda x:
                    x.rolling(
                        window=4,
                        min_periods=1
                    ).sum()
            )
        )

    return df











def safe_percentage_change(
    current,
    previous
):

    denominator = (
        previous.abs()
        .replace(
            0,
            np.nan
        )
    )

    result = (
        (current - previous)
        /
        denominator
    )

    return result.replace(
        [
            np.inf,
            -np.inf
        ],
        np.nan
    )










def add_trend_features(df):

    df = df.copy()

    grouped = df.groupby(
        "ADMIN1"
    )

    # Absolute week-to-week changes
    df[
        "event_change_1wk"
    ] = (
        grouped[
            "total_events"
        ]
        .diff()
    )

    df[
        "fatality_change_1wk"
    ] = (
        grouped[
            "total_fatalities"
        ]
        .diff()
    )

    df[
        "violent_event_change_1wk"
    ] = (
        grouped[
            "violent_events"
        ]
        .diff()
    )

    df[
        "high_severity_change_1wk"
    ] = (
        grouped[
            "high_severity_events"
        ]
        .diff()
    )

    df[
        "abduction_change_1wk"
    ] = (
        grouped[
            "abductions"
        ]
        .diff()
    )

    # Previous-week values
    previous_events = (
        grouped[
            "total_events"
        ]
        .shift(1)
    )

    previous_fatalities = (
        grouped[
            "total_fatalities"
        ]
        .shift(1)
    )

    # Percentage week-to-week changes
    df[
        "event_pct_change_1wk"
    ] = safe_percentage_change(
        df["total_events"],
        previous_events
    )

    df[
        "fatality_pct_change_1wk"
    ] = safe_percentage_change(
        df["total_fatalities"],
        previous_fatalities
    )

    return df







def add_event_category_features(df):

    df = df.copy()

    denominator = (
        df["total_events"]
        .replace(
            0,
            np.nan
        )
    )

    df[
        "violent_event_ratio"
    ] = (
        df[
            "violent_events"
        ]
        /
        denominator
    )

    df[
        "high_severity_ratio"
    ] = (
        df[
            "high_severity_events"
        ]
        /
        denominator
    )

    df[
        "battle_ratio"
    ] = (
        df["battles"]
        /
        denominator
    )

    df[
        "civilian_violence_ratio"
    ] = (
        df[
            "violence_against_civilians"
        ]
        /
        denominator
    )

    df[
        "abduction_ratio"
    ] = (
        df["abductions"]
        /
        denominator
    )

    df[
        "explosion_ratio"
    ] = (
        df[
            "explosions_remote_violence"
        ]
        /
        denominator
    )

    df[
        "protest_ratio"
    ] = (
        df["protests"]
        /
        denominator
    )

    ratio_columns = [
        "violent_event_ratio",
        "high_severity_ratio",
        "battle_ratio",
        "civilian_violence_ratio",
        "abduction_ratio",
        "explosion_ratio",
        "protest_ratio",
    ]

    df[
        ratio_columns
    ] = (
        df[
            ratio_columns
        ]
        .fillna(0)
    )

    return df




# We can also create simple binary features indicating notable escalation.
def add_escalation_features(df):

    df = df.copy()

    df[
        "events_increasing"
    ] = (
        df[
            "event_change_1wk"
        ] > 0
    ).astype(int)

    df[
        "fatalities_increasing"
    ] = (
        df[
            "fatality_change_1wk"
        ] > 0
    ).astype(int)

    df[
        "violence_increasing"
    ] = (
        df[
            "violent_event_change_1wk"
        ] > 0
    ).astype(int)

    df[
        "high_severity_increasing"
    ] = (
        df[
            "high_severity_change_1wk"
        ] > 0
    ).astype(int)

    return df



# Build the Complete Feature Pipeline
def create_feature_dataset():

    state_week = (
        create_state_week_dataset()
    )

    df = (
        create_complete_state_week_panel(
            state_week
        )
    )

    df = add_time_features(
        df
    )

    df = add_lag_features(
        df
    )

    df = add_rolling_features(
        df
    )

    df = add_trend_features(
        df
    )

    df = add_event_category_features(
        df
    )

    df = add_escalation_features(
        df
    )

    df = df.sort_values(
        [
            "ADMIN1",
            "WEEK"
        ]
    ).reset_index(
        drop=True
    )

    return df





# Save the Feature Dataset
def save_feature_dataset(df):

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

    feature_df = (
        create_feature_dataset()
    )

    output = (
        save_feature_dataset(
            feature_df
        )
    )

    print(
        "\nFEATURE ENGINEERING COMPLETE"
    )

    print("=" * 60)

    print(
        f"Rows: "
        f"{len(feature_df):,}"
    )

    print(
        f"Columns: "
        f"{len(feature_df.columns)}"
    )

    print(
        f"States/FCT: "
        f"{feature_df['ADMIN1'].nunique()}"
    )

    print(
        f"Start: "
        f"{feature_df['WEEK'].min()}"
    )

    print(
        f"End: "
        f"{feature_df['WEEK'].max()}"
    )

    print(
        f"\nSaved to: "
        f"{output}"
    )
