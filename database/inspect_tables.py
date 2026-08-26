from sqlalchemy import inspect

from database.connection import engine


def inspect_database():

    inspector = inspect(engine)

    tables = inspector.get_table_names()

    print(
        "\nDATABASE TABLES"
    )

    print(
        "=" * 50
    )

    for table in tables:
        print(table)

    print(
        f"\nTotal tables: {len(tables)}"
    )


if __name__ == "__main__":
    inspect_database()

from services.preprocessing import (
    preprocess_nigeria_dataset
)

clean_df, report = (
    preprocess_nigeria_dataset()
)

st.subheader(
    "Preprocessing Summary"
)

col1, col2, col3, col4 = (
    st.columns(4)
)

col1.metric(
    "Original Nigeria Rows",
    f"{report['original_nigeria_rows']:,}"
)

col2.metric(
    "Clean Rows",
    f"{report['clean_rows']:,}"
)

col3.metric(
    "Duplicates Removed",
    report[
        "duplicates_removed"
    ]
)

col4.metric(
    "Invalid Rows Removed",
    report[
        "invalid_rows_removed"
    ]
)

st.metric(
    "Missing Population Exposure",
    f"{report['population_exposure_missing']:,}"
)