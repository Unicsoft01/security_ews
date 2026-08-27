from services.risk_assessment_service import (
    get_latest_risk_assessments
)


def test_latest_assessments_exist():

    df = (
        get_latest_risk_assessments()
    )

    assert not df.empty


def test_37_states_assessed():

    df = (
        get_latest_risk_assessments()
    )

    assert len(df) == 37

    assert (
        df["state"].nunique()
        == 37
    )


def test_risk_levels_valid():

    df = (
        get_latest_risk_assessments()
    )

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


def test_confidence_valid():

    df = (
        get_latest_risk_assessments()
    )

    assert (
        df[
            "confidence"
        ]
        .between(
            0,
            1
        )
        .all()
    )