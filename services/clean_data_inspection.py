import pandas as pd

from services.preprocessing import (
    preprocess_nigeria_dataset
)


def inspect_clean_data():

    df, report = (
        preprocess_nigeria_dataset()
    )

    print(
        "\nCLEAN DATASET SUMMARY"
    )

    print("=" * 60)

    print(
        f"Rows: {len(df):,}"
    )

    print(
        f"Columns: {len(df.columns)}"
    )

    print(
        f"States/FCT: "
        f"{df['ADMIN1'].nunique()}"
    )

    print(
        f"Start date: "
        f"{df['WEEK'].min().date()}"
    )

    print(
        f"End date: "
        f"{df['WEEK'].max().date()}"
    )

    print(
        f"Total represented events: "
        f"{df['EVENTS'].sum():,.0f}"
    )

    print(
        f"Total fatalities: "
        f"{df['FATALITIES'].sum():,.0f}"
    )

    print(
        "\nMISSING VALUES"
    )

    print("=" * 60)

    print(
        df.isna()
        .sum()
        .sort_values(
            ascending=False
        )
    )

    print(
        "\nEVENT TYPES"
    )

    print("=" * 60)

    print(
        df[
            "EVENT_TYPE"
        ]
        .value_counts()
    )


if __name__ == "__main__":

    inspect_clean_data()