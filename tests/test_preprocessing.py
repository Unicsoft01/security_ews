from services.preprocessing import (
    preprocess_nigeria_dataset
)


def test_clean_dataset_not_empty():

    df, _ = preprocess_nigeria_dataset()

    assert not df.empty


def test_only_nigeria():

    df, _ = preprocess_nigeria_dataset()

    countries = (
        df["COUNTRY"]
        .str.casefold()
        .unique()
        .tolist()
    )

    assert countries == [
        "nigeria"
    ]


def test_no_missing_essential_fields():

    df, _ = preprocess_nigeria_dataset()

    essential = [
        "WEEK",
        "ADMIN1",
        "EVENT_TYPE",
        "SUB_EVENT_TYPE",
        "EVENTS",
        "FATALITIES",
    ]

    assert (
        df[essential]
        .isna()
        .sum()
        .sum()
        == 0
    )


def test_no_negative_events():

    df, _ = preprocess_nigeria_dataset()

    assert (
        df["EVENTS"] >= 0
    ).all()


def test_no_negative_fatalities():

    df, _ = preprocess_nigeria_dataset()

    assert (
        df["FATALITIES"] >= 0
    ).all()


def test_no_exact_duplicates():

    df, _ = preprocess_nigeria_dataset()

    assert (
        df.duplicated().sum()
        == 0
    )


def test_nigeria_locations():

    df, _ = preprocess_nigeria_dataset()

    assert (
        df["ADMIN1"].nunique()
        == 37
    )