from services.data_loader import (
    load_raw_dataset,
    filter_nigeria
)

from services.validator import (
    REQUIRED_COLUMNS,
    validate_required_columns
)


def test_dataset_loads():

    df = load_raw_dataset()

    assert not df.empty


def test_required_columns():

    df = load_raw_dataset()

    result = validate_required_columns(
        df
    )

    assert result["valid"] is True


def test_nigeria_exists():

    df = load_raw_dataset()

    nigeria = filter_nigeria(df)

    assert not nigeria.empty


def test_nigeria_country_only():

    df = load_raw_dataset()

    nigeria = filter_nigeria(df)

    countries = (
        nigeria["COUNTRY"]
        .dropna()
        .str.casefold()
        .unique()
    )

    assert list(countries) == [
        "nigeria"
    ]


def test_all_required_columns():

    df = load_raw_dataset()

    for column in REQUIRED_COLUMNS:
        assert column in df.columns