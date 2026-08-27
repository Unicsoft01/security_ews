from services.prediction import (
    generate_latest_predictions,
    get_latest_feature_rows,
)


def test_latest_state_rows():

    df, latest_week = (
        get_latest_feature_rows()
    )

    assert len(df) == 37

    assert (
        df["ADMIN1"].nunique()
        == 37
    )


def test_predictions_generated():

    results = (
        generate_latest_predictions()
    )

    assert len(results) == 37


def test_valid_prediction_classes():

    results = (
        generate_latest_predictions()
    )

    valid_classes = {
        "Low",
        "Medium",
        "High",
    }

    assert set(
        results[
            "predicted_risk"
        ]
    ).issubset(
        valid_classes
    )


def test_prediction_confidence():

    results = (
        generate_latest_predictions()
    )

    assert (
        results[
            "prediction_confidence"
        ]
        .between(
            0,
            1
        )
        .all()
    )


def test_forecast_after_assessment():

    results = (
        generate_latest_predictions()
    )

    assert (
        results[
            "forecast_week"
        ]
        >
        results[
            "assessment_week"
        ]
    ).all()