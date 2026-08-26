import pandas as pd

from services.data_loader import (
    load_raw_dataset,
    filter_nigeria
)

from services.validator import (
    validate_dataset_not_empty,
    validate_required_columns,
    validate_nigeria_records
)
from services.validator import validate_numeric_values


def inspect_dataset():

    df = load_raw_dataset()

    validate_dataset_not_empty(df)

    validation = validate_required_columns(df)

    print("\n1. DATASET VALIDATION")
    print("=" * 60)

    print(
        f"Required columns present: "
        f"{validation['valid']}"
    )

    print(
        f"Expected columns: "
        f"{validation['required_count']}"
    )

    print(
        f"Actual columns: "
        f"{validation['actual_count']}"
    )

    print(
        f"Missing columns: "
        f"{validation['missing_columns']}"
    )

    print(
        f"Unexpected columns: "
        f"{validation['unexpected_columns']}"
    )

    nigeria_count = validate_nigeria_records(df)

    print(
        f"\nNigeria rows found: "
        f"{nigeria_count:,}"
    )

    nigeria = filter_nigeria(df)

    print("\n2. NIGERIA DATASET SIZE")
    print("=" * 60)

    print(
        f"Rows: {len(nigeria):,}"
    )

    print(
        f"Columns: {len(nigeria.columns)}"
    )

    print("\n3. COLUMN DATA TYPES")
    print("=" * 60)

    print(nigeria.dtypes)

    print("\n4. MISSING VALUES")
    print("=" * 60)

    missing = (
        nigeria
        .isna()
        .sum()
        .sort_values(
            ascending=False
        )
    )

    print(missing)

    print("\n5. COMPLETELY DUPLICATED ROWS")
    print("=" * 60)

    duplicates = nigeria.duplicated().sum()

    print(
        f"Duplicate rows: {duplicates:,}"
    )

    print("\n6. STATES / FCT")
    print("=" * 60)

    states = sorted(
        nigeria["ADMIN1"]
        .dropna()
        .unique()
    )

    print(
        f"Number of states/FCT: "
        f"{len(states)}"
    )

    for state in states:
        print(state)

    print("\n7. EVENT TYPES")
    print("=" * 60)

    event_types = (
        nigeria["EVENT_TYPE"]
        .value_counts()
    )

    print(event_types)

    print("\n8. SUB-EVENT TYPES")
    print("=" * 60)

    sub_event_types = (
        nigeria["SUB_EVENT_TYPE"]
        .value_counts()
    )

    print(sub_event_types)

    print("\n9. DISORDER TYPES")
    print("=" * 60)

    disorder_types = (
        nigeria["DISORDER_TYPE"]
        .value_counts()
    )

    print(disorder_types)

    print("\n10. NUMERIC SUMMARY")
    print("=" * 60)

    numeric_columns = [
        "EVENTS",
        "FATALITIES",
        "POPULATION_EXPOSURE",
        "CENTROID_LATITUDE",
        "CENTROID_LONGITUDE",
    ]

    print(
        nigeria[
            numeric_columns
        ].describe()
    )

    print("\n11. DATE COVERAGE")
    print("=" * 60)

    week = pd.to_datetime(
        nigeria["WEEK"],
        errors="coerce"
    )

    print(
        f"Earliest week: "
        f"{week.min()}"
    )

    print(
        f"Latest week: "
        f"{week.max()}"
    )

    print("\n12. TOTAL EVENT COUNTS")
    print("=" * 60)

    print(
        f"Total represented events: "
        f"{nigeria['EVENTS'].sum():,.0f}"
    )

    print(
        f"Total recorded fatalities: "
        f"{nigeria['FATALITIES'].sum():,.0f}"
    )

    return nigeria


if __name__ == "__main__":
    inspect_dataset()