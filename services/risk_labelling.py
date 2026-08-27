from pathlib import Path

import numpy as np
import pandas as pd

from services.feature_engineering import (
    create_feature_dataset
)


OUTPUT_PATH = Path(
    "data/processed/"
    "acled_nigeria_ml_dataset.csv"
)


# --------------------------------------------------
# SEVERITY COMPONENTS
# --------------------------------------------------

SEVERITY_COMPONENTS = [
    "total_events",
    "total_fatalities",
    "violent_events",
    "high_severity_events",
]


SEVERITY_WEIGHTS = {
    "total_events": 0.25,
    "total_fatalities": 0.35,
    "violent_events": 0.25,
    "high_severity_events": 0.15,
}


# --------------------------------------------------
# LEAKAGE COLUMNS
# --------------------------------------------------

LEAKAGE_COLUMNS = [
    "current_severity_score",
    "next_week_severity_score",
    "target_risk",
    "total_events_severity_scaled",
    "total_fatalities_severity_scaled",
    "violent_events_severity_scaled",
    "high_severity_events_severity_scaled",
]


# --------------------------------------------------
# ROBUST SCALING
# --------------------------------------------------

def robust_minmax_scale(
    series,
    lower_quantile=0.01,
    upper_quantile=0.99,
):
    """
    Scale a numeric series between 0 and 1 using
    robust percentile limits.
    """

    lower = series.quantile(
        lower_quantile
    )

    upper = series.quantile(
        upper_quantile
    )

    if upper == lower:

        return pd.Series(
            0.0,
            index=series.index
        )

    clipped = series.clip(
        lower=lower,
        upper=upper
    )

    scaled = (
        (clipped - lower)
        /
        (upper - lower)
    )

    return scaled


# --------------------------------------------------
# CURRENT-WEEK SEVERITY
# --------------------------------------------------

def create_current_severity_score(df):
    """
    Create the observed security severity score
    for each state-week.
    """

    df = df.copy()

    for column in SEVERITY_COMPONENTS:

        scaled_column = (
            f"{column}_severity_scaled"
        )

        df[
            scaled_column
        ] = robust_minmax_scale(
            df[column]
        )

    df[
        "current_severity_score"
    ] = (
        df[
            "total_events_severity_scaled"
        ]
        * SEVERITY_WEIGHTS[
            "total_events"
        ]

        +

        df[
            "total_fatalities_severity_scaled"
        ]
        * SEVERITY_WEIGHTS[
            "total_fatalities"
        ]

        +

        df[
            "violent_events_severity_scaled"
        ]
        * SEVERITY_WEIGHTS[
            "violent_events"
        ]

        +

        df[
            "high_severity_events_severity_scaled"
        ]
        * SEVERITY_WEIGHTS[
            "high_severity_events"
        ]
    )

    return df


# --------------------------------------------------
# NEXT-WEEK TARGET
# --------------------------------------------------

def create_next_week_target(df):
    """
    Shift the observed severity score one week
    forward within each state.

    Features at week t will therefore predict
    security severity at week t+1.
    """

    df = df.copy()

    df = df.sort_values(
        [
            "ADMIN1",
            "WEEK"
        ]
    ).reset_index(
        drop=True
    )

    grouped = df.groupby(
        "ADMIN1"
    )

    df[
        "next_week_severity_score"
    ] = (
        grouped[
            "current_severity_score"
        ]
        .shift(-1)
    )

    return df


# --------------------------------------------------
# LOW / MEDIUM / HIGH RISK CLASSES
# --------------------------------------------------

def create_risk_classes(df):
    """
    Convert next-week severity scores into
    Low, Medium and High risk categories.
    """

    df = df.copy()

    valid_target = (
        df[
            "next_week_severity_score"
        ]
        .dropna()
    )

    low_threshold = (
        valid_target.quantile(
            0.33
        )
    )

    high_threshold = (
        valid_target.quantile(
            0.67
        )
    )

    def classify_risk(score):

        if pd.isna(score):

            return np.nan

        if score <= low_threshold:

            return "Low"

        if score <= high_threshold:

            return "Medium"

        return "High"

    df[
        "target_risk"
    ] = (
        df[
            "next_week_severity_score"
        ]
        .apply(
            classify_risk
        )
    )

    thresholds = {

        "low_threshold":
            float(
                low_threshold
            ),

        "high_threshold":
            float(
                high_threshold
            ),
    }

    return df, thresholds


# --------------------------------------------------
# COMPLETE LABELLING PIPELINE
# --------------------------------------------------

def create_labelled_dataset():
    """
    Run the complete Phase 7 risk-labelling
    pipeline.
    """

    df = (
        create_feature_dataset()
    )

    df = (
        create_current_severity_score(
            df
        )
    )

    df = (
        create_next_week_target(
            df
        )
    )

    df, thresholds = (
        create_risk_classes(
            df
        )
    )

    return df, thresholds


# --------------------------------------------------
# SAVE DATASET
# --------------------------------------------------

def save_labelled_dataset(df):
    """
    Save the machine-learning dataset.
    """

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    return OUTPUT_PATH


# --------------------------------------------------
# RUN DIRECTLY
# --------------------------------------------------

if __name__ == "__main__":

    df, thresholds = (
        create_labelled_dataset()
    )

    output = (
        save_labelled_dataset(
            df
        )
    )

    print(
        "\nRISK LABEL ENGINEERING COMPLETE"
    )

    print("=" * 60)

    print(
        f"Rows: {len(df):,}"
    )

    print(
        f"Low threshold: "
        f"{thresholds['low_threshold']:.4f}"
    )

    print(
        f"High threshold: "
        f"{thresholds['high_threshold']:.4f}"
    )

    print(
        "\nCLASS DISTRIBUTION"
    )

    print("=" * 60)

    print(
        df[
            "target_risk"
        ]
        .value_counts(
            dropna=False
        )
    )

    print(
        f"\nSaved to: "
        f"{output}"
    )