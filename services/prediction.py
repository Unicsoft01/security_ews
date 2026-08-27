from datetime import timedelta

import numpy as np
import pandas as pd

from services.feature_engineering import (
    create_feature_dataset
)

from services.model_service import (
    load_selected_model
)


def get_latest_feature_rows():
    """
    Return the most recent feature-engineered
    state-week record for every state/FCT.
    """

    df = create_feature_dataset()

    df = df.copy()

    df["WEEK"] = pd.to_datetime(
        df["WEEK"]
    )

    latest_week = (
        df["WEEK"].max()
    )

    latest_df = (
        df[
            df["WEEK"] == latest_week
        ]
        .copy()
    )

    latest_df = (
        latest_df.sort_values(
            "ADMIN1"
        )
        .reset_index(
            drop=True
        )
    )

    return (
        latest_df,
        latest_week
    )


def prepare_prediction_features(
    model,
    latest_df
):
    """
    Prepare latest state-week rows using exactly
    the feature columns used during model training.
    """

    if not hasattr(
        model,
        "feature_names_in_"
    ):

        raise AttributeError(
            "The saved model does not contain "
            "training feature names."
        )

    required_features = list(
        model.feature_names_in_
    )

    missing_columns = [
        column
        for column in required_features
        if column not in latest_df.columns
    ]

    if missing_columns:

        raise ValueError(
            "Latest feature dataset is missing "
            f"required model columns: "
            f"{missing_columns}"
        )

    X_latest = (
        latest_df[
            required_features
        ]
        .copy()
    )

    # Replace infinite values with NaN
    X_latest = X_latest.replace(
        [
            np.inf,
            -np.inf
        ],
        np.nan
    )

    return X_latest


def generate_latest_predictions():
    """
    Generate next-week risk predictions
    for all Nigerian states/FCT.
    """

    model = (
        load_selected_model()
    )

    (
        latest_df,
        assessment_week
    ) = get_latest_feature_rows()

    X_latest = (
        prepare_prediction_features(
            model,
            latest_df
        )
    )

    # -----------------------------------------
    # RISK CLASS PREDICTION
    # -----------------------------------------

    predictions = model.predict(
        X_latest
    )

    # -----------------------------------------
    # CLASS PROBABILITIES
    # -----------------------------------------

    probabilities = model.predict_proba(
        X_latest
    )

    classifier = (
        model.named_steps[
            "classifier"
        ]
    )

    classes = list(
        classifier.classes_
    )

    probability_df = (
        pd.DataFrame(
            probabilities,
            columns=[
                f"probability_{risk.lower()}"
                for risk in classes
            ]
        )
    )

    # -----------------------------------------
    # FORECAST PERIOD
    # -----------------------------------------

    forecast_week = (
        assessment_week
        + timedelta(days=7)
    )

    # -----------------------------------------
    # RESULT TABLE
    # -----------------------------------------

    results = pd.DataFrame(
        {
            "ADMIN1":
                latest_df[
                    "ADMIN1"
                ].values,

            "assessment_week":
                assessment_week,

            "forecast_week":
                forecast_week,

            "predicted_risk":
                predictions,
        }
    )

    results = pd.concat(
        [
            results,
            probability_df
        ],
        axis=1
    )

    # -----------------------------------------
    # PREDICTION CONFIDENCE
    # -----------------------------------------

    probability_columns = [
        column
        for column in (
            probability_df.columns
        )
    ]

    results[
        "prediction_confidence"
    ] = (
        results[
            probability_columns
        ]
        .max(
            axis=1
        )
    )

    return results