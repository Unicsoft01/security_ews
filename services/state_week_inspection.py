import pandas as pd

from services.state_week_aggregation import (
    create_state_week_dataset
)


def inspect_state_week():

    df = (
        create_state_week_dataset()
    )

    print(
        "\nSTATE-WEEK DATASET INSPECTION"
    )

    print("=" * 60)

    print(
        f"Rows: {len(df):,}"
    )

    print(
        f"States/FCT: "
        f"{df['ADMIN1'].nunique()}"
    )

    print(
        f"Unique weeks: "
        f"{df['WEEK'].nunique():,}"
    )

    print(
        "\nRECORDS BY YEAR"
    )

    print("=" * 60)

    yearly = (
        df.assign(
            YEAR=
                pd.to_datetime(
                    df["WEEK"]
                ).dt.year
        )
        .groupby(
            "YEAR"
        )
        .agg(
            state_week_records=(
                "ADMIN1",
                "count"
            ),

            states_reporting=(
                "ADMIN1",
                "nunique"
            ),

            total_events=(
                "total_events",
                "sum"
            ),

            total_fatalities=(
                "total_fatalities",
                "sum"
            )
        )
    )

    print(yearly)

    print(
        "\nOBSERVED WEEKS PER STATE"
    )

    print("=" * 60)

    state_summary = (
        df.groupby(
            "ADMIN1"
        )
        .agg(
            first_week=(
                "WEEK",
                "min"
            ),

            last_week=(
                "WEEK",
                "max"
            ),

            observed_weeks=(
                "WEEK",
                "nunique"
            ),

            total_events=(
                "total_events",
                "sum"
            ),

            total_fatalities=(
                "total_fatalities",
                "sum"
            )
        )
        .sort_values(
            "observed_weeks",
            ascending=False
        )
    )

    print(state_summary)


if __name__ == "__main__":

    inspect_state_week()