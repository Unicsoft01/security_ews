from services.risk_labelling import (
    LEAKAGE_COLUMNS,
    create_labelled_dataset,
)


def test_labelled_dataset_not_empty():

    df, _ = (
        create_labelled_dataset()
    )

    assert not df.empty


def test_target_column_exists():

    df, _ = (
        create_labelled_dataset()
    )

    assert (
        "target_risk"
        in df.columns
    )


def test_valid_risk_labels():

    df, _ = (
        create_labelled_dataset()
    )

    values = set(
        df[
            "target_risk"
        ]
        .dropna()
        .unique()
    )

    assert values.issubset(
        {
            "Low",
            "Medium",
            "High",
        }
    )


def test_next_week_target_exists():

    df, _ = (
        create_labelled_dataset()
    )

    assert (
        "next_week_severity_score"
        in df.columns
    )


def test_last_week_per_state_has_no_target():

    df, _ = (
        create_labelled_dataset()
    )

    last_rows = (
        df.sort_values(
            [
                "ADMIN1",
                "WEEK"
            ]
        )
        .groupby(
            "ADMIN1"
        )
        .tail(1)
    )

    assert (
        last_rows[
            "target_risk"
        ]
        .isna()
        .all()
    )


def test_all_three_classes_exist():

    df, _ = (
        create_labelled_dataset()
    )

    classes = set(
        df[
            "target_risk"
        ]
        .dropna()
        .unique()
    )

    assert classes == {
        "Low",
        "Medium",
        "High",
    }


def test_leakage_columns_defined():

    required = {
        "current_severity_score",
        "next_week_severity_score",
        "target_risk",
    }

    assert required.issubset(
        set(
            LEAKAGE_COLUMNS
        )
    )