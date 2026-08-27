from pages_ui.risk_map_view import (
    prepare_map_data
)


def test_risk_map_data_exists():

    df = prepare_map_data()

    assert not df.empty


def test_all_states_mapped():

    df = prepare_map_data()

    assert len(df) == 37

    assert (
        df[
            "state"
        ]
        .nunique()
        == 37
    )


def test_no_missing_coordinates():

    df = prepare_map_data()

    assert (
        df[
            [
                "latitude",
                "longitude"
            ]
        ]
        .isna()
        .sum()
        .sum()
        == 0
    )


def test_valid_latitudes():

    df = prepare_map_data()

    assert (
        df[
            "latitude"
        ]
        .between(
            -90,
            90
        )
        .all()
    )


def test_valid_longitudes():

    df = prepare_map_data()

    assert (
        df[
            "longitude"
        ]
        .between(
            -180,
            180
        )
        .all()
    )


def test_valid_risk_levels():

    df = prepare_map_data()

    valid = {
        "Low",
        "Medium",
        "High",
    }

    assert set(
        df[
            "risk_level"
        ]
    ).issubset(
        valid
    )