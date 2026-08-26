from pathlib import Path

import numpy as np
import pandas as pd

from services.data_loader import (
    load_raw_dataset,
    filter_nigeria,
)


CLEAN_OUTPUT_PATH = Path(
    "data/processed/acled_nigeria_clean.csv"
)


ESSENTIAL_COLUMNS = [
    "WEEK",
    "COUNTRY",
    "ADMIN1",
    "EVENT_TYPE",
    "SUB_EVENT_TYPE",
    "EVENTS",
    "FATALITIES",
]


TEXT_COLUMNS = [
    "REGION",
    "COUNTRY",
    "ADMIN1",
    "EVENT_TYPE",
    "SUB_EVENT_TYPE",
    "DISORDER_TYPE",
]


def clean_text_columns(df):
    """
    Strip whitespace from text fields while preserving
    ACLED's original category terminology.
    """

    df = df.copy()

    for column in TEXT_COLUMNS:

        if column in df.columns:

            df[column] = (
                df[column]
                .astype("string")
                .str.strip()
            )

    return df


def clean_dates(df):
    """
    Convert WEEK to pandas datetime.
    """

    df = df.copy()

    df["WEEK"] = pd.to_datetime(
        df["WEEK"],
        errors="coerce"
    )

    return df


def clean_numeric_fields(df):
    """
    Convert numeric ACLED fields to proper numeric types.
    """

    df = df.copy()

    numeric_columns = [
        "EVENTS",
        "FATALITIES",
        "POPULATION_EXPOSURE",
        "CENTROID_LATITUDE",
        "CENTROID_LONGITUDE",
    ]

    for column in numeric_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    return df


def validate_coordinates(df):
    """
    Replace geographically impossible coordinates
    with missing values.
    """

    df = df.copy()

    invalid_latitude = (
        (df["CENTROID_LATITUDE"] < -90)
        |
        (df["CENTROID_LATITUDE"] > 90)
    )

    invalid_longitude = (
        (df["CENTROID_LONGITUDE"] < -180)
        |
        (df["CENTROID_LONGITUDE"] > 180)
    )

    df.loc[
        invalid_latitude,
        "CENTROID_LATITUDE"
    ] = np.nan

    df.loc[
        invalid_longitude,
        "CENTROID_LONGITUDE"
    ] = np.nan

    return df


def remove_invalid_records(df):
    """
    Remove records that cannot be used reliably in
    later analysis.
    """

    df = df.copy()

    # Remove rows missing essential fields
    df = df.dropna(
        subset=ESSENTIAL_COLUMNS
    )

    # Events and fatalities cannot be negative
    df = df[
        (df["EVENTS"] >= 0)
        &
        (df["FATALITIES"] >= 0)
    ].copy()

    # Events and fatalities represent counts
    df["EVENTS"] = (
        df["EVENTS"]
        .round()
        .astype(int)
    )

    df["FATALITIES"] = (
        df["FATALITIES"]
        .round()
        .astype(int)
    )

    return df


def clean_acled_id(df):
    """
    Preserve ACLED administrative identifier as text.
    """

    df = df.copy()

    if "ID" in df.columns:

        df["ID"] = (
            df["ID"]
            .astype("string")
            .str.strip()
        )

    return df


def remove_duplicates(df):
    """
    Remove completely duplicated ACLED records.
    """

    df = df.copy()

    before = len(df)

    df = df.drop_duplicates().copy()

    removed = before - len(df)

    return df, removed


def preprocess_nigeria_dataset():
    """
    Complete preprocessing pipeline.
    """

    raw_df = load_raw_dataset()

    nigeria_df = filter_nigeria(
        raw_df
    )

    original_count = len(
        nigeria_df
    )

    df = clean_text_columns(
        nigeria_df
    )

    df = clean_dates(
        df
    )

    df = clean_numeric_fields(
        df
    )

    df = validate_coordinates(
        df
    )

    df = clean_acled_id(
        df
    )

    df, duplicates_removed = (
        remove_duplicates(df)
    )

    before_invalid = len(df)

    df = remove_invalid_records(
        df
    )

    invalid_removed = (
        before_invalid
        - len(df)
    )

    # Sort chronologically for reproducibility
    df = df.sort_values(
        by=[
            "WEEK",
            "ADMIN1",
            "EVENT_TYPE",
            "SUB_EVENT_TYPE"
        ]
    ).reset_index(
        drop=True
    )

    report = {
        "original_nigeria_rows":
            original_count,

        "duplicates_removed":
            duplicates_removed,

        "invalid_rows_removed":
            invalid_removed,

        "clean_rows":
            len(df),

        "population_exposure_missing":
            int(
                df[
                    "POPULATION_EXPOSURE"
                ]
                .isna()
                .sum()
            ),

        "coordinate_lat_missing":
            int(
                df[
                    "CENTROID_LATITUDE"
                ]
                .isna()
                .sum()
            ),

        "coordinate_lon_missing":
            int(
                df[
                    "CENTROID_LONGITUDE"
                ]
                .isna()
                .sum()
            ),
    }

    return df, report


def save_clean_dataset(df):

    CLEAN_OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        CLEAN_OUTPUT_PATH,
        index=False
    )

    return CLEAN_OUTPUT_PATH


if __name__ == "__main__":

    clean_df, report = (
        preprocess_nigeria_dataset()
    )

    output = save_clean_dataset(
        clean_df
    )

    print(
        "\nACLED NIGERIA PREPROCESSING COMPLETE"
    )

    print("=" * 60)

    for key, value in report.items():

        print(
            f"{key}: {value:,}"
            if isinstance(value, int)
            else f"{key}: {value}"
        )

    print(
        f"\nClean dataset saved to: "
        f"{output}"
    )