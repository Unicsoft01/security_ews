REQUIRED_COLUMNS = [
    "WEEK",
    "REGION",
    "COUNTRY",
    "ADMIN1",
    "EVENT_TYPE",
    "SUB_EVENT_TYPE",
    "EVENTS",
    "FATALITIES",
    "POPULATION_EXPOSURE",
    "DISORDER_TYPE",
    "ID",
    "CENTROID_LATITUDE",
    "CENTROID_LONGITUDE",
]


def validate_required_columns(df):
    """
    Check that every required ACLED column exists.
    """

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    unexpected_columns = [
        column
        for column in df.columns
        if column not in REQUIRED_COLUMNS
    ]

    return {
        "valid": len(missing_columns) == 0,
        "missing_columns": missing_columns,
        "unexpected_columns": unexpected_columns,
        "required_count": len(REQUIRED_COLUMNS),
        "actual_count": len(df.columns),
    }


def validate_dataset_not_empty(df):

    if df.empty:
        raise ValueError(
            "Dataset is empty."
        )

    return True


def validate_nigeria_records(df):

    if "COUNTRY" not in df.columns:
        raise KeyError(
            "COUNTRY column is missing."
        )

    countries = (
        df["COUNTRY"]
        .dropna()
        .astype(str)
        .str.strip()
        .str.casefold()
    )

    nigeria_count = (
        countries == "nigeria"
    ).sum()

    if nigeria_count == 0:
        raise ValueError(
            "No Nigeria records were found."
        )

    return nigeria_count

# Added 
def validate_numeric_values(df):

    problems = {}

    if "EVENTS" in df.columns:

        negative_events = (
            df["EVENTS"] < 0
        ).sum()

        problems[
            "negative_events"
        ] = int(negative_events)

    if "FATALITIES" in df.columns:

        negative_fatalities = (
            df["FATALITIES"] < 0
        ).sum()

        problems[
            "negative_fatalities"
        ] = int(
            negative_fatalities
        )

    return problems


# To validate state coordinates
def validate_coordinates(df):

    invalid_latitude = (
        (df["CENTROID_LATITUDE"] < -90)
        |
        (df["CENTROID_LATITUDE"] > 90)
    ).sum()

    invalid_longitude = (
        (df["CENTROID_LONGITUDE"] < -180)
        |
        (df["CENTROID_LONGITUDE"] > 180)
    ).sum()

    return {
        "invalid_latitude":
            int(invalid_latitude),

        "invalid_longitude":
            int(invalid_longitude),
    }