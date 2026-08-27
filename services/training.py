from pathlib import Path

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier

from config.settings import (
    TRAIN_END_DATE,
    TEST_START_DATE,
)

from services.risk_labelling import (
    LEAKAGE_COLUMNS,
    create_labelled_dataset,
)


MODEL_DIR = Path("models")

DECISION_TREE_PATH = (
    MODEL_DIR /
    "decision_tree.pkl"
)


def prepare_modelling_data():
    """
    Prepare labelled dataset for machine learning.
    """

    df, _ = create_labelled_dataset()

    df = df.copy()

    df["WEEK"] = pd.to_datetime(
        df["WEEK"]
    )

    # Remove rows without future target
    df = df[
        df["target_risk"].notna()
    ].copy()

    # Remove rows that do not yet have
    # sufficient 4-week history
    required_history_columns = [
        "total_events_lag_4",
        "total_fatalities_lag_4",
        "violent_events_lag_4",
        "high_severity_events_lag_4",
    ]

    df = df.dropna(
        subset=required_history_columns
    ).copy()

    # IMPORTANT:
    # Sort chronologically before creating X and y.
    # This supports time-aware train/test splitting
    # and TimeSeriesSplit during model tuning.
    df = df.sort_values(
        [
            "WEEK",
            "ADMIN1"
        ]
    ).reset_index(
        drop=True
    )

    # Separate target
    y = df["target_risk"].copy()

    # Columns that must not be used as predictors
    columns_to_drop = (
        LEAKAGE_COLUMNS
        + [
            "WEEK",
            "latitude",
            "longitude",
        ]
    )

    X = df.drop(
        columns=[
            column
            for column in columns_to_drop
            if column in df.columns
        ]
    )

    return df, X, y


# Create the Chronological Split
def chronological_split(
    df,
    X,
    y
):
    """
    Split training and testing data by date.
    """

    train_end = pd.to_datetime(
        TRAIN_END_DATE
    )

    test_start = pd.to_datetime(
        TEST_START_DATE
    )

    train_mask = (
        df["WEEK"]
        <= train_end
    )

    test_mask = (
        df["WEEK"]
        >= test_start
    )

    X_train = X.loc[
        train_mask
    ].copy()

    y_train = y.loc[
        train_mask
    ].copy()

    X_test = X.loc[
        test_mask
    ].copy()

    y_test = y.loc[
        test_mask
    ].copy()

    return (
        X_train,
        X_test,
        y_train,
        y_test,
    )

# Build the Preprocessing Pipeline
def build_preprocessor(X):
    """
    Build preprocessing pipeline.
    """

    categorical_features = [
        column
        for column in [
            "ADMIN1"
        ]
        if column in X.columns
    ]

    numeric_features = [
        column
        for column in X.columns
        if column not in categorical_features
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
                categorical_features
            ),
            (
                "numeric",
                "passthrough",
                numeric_features
            ),
        ]
    )

    return preprocessor


# Create the Baseline Decision Tree
def build_decision_tree_pipeline(
    X
):
    """
    Create baseline Decision Tree pipeline.
    """

    preprocessor = (
        build_preprocessor(X)
    )

    model = DecisionTreeClassifier(
        random_state=42,
        class_weight="balanced"
    )

    pipeline = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor
            ),
            (
                "classifier",
                model
            ),
        ]
    )

    return pipeline


# Train the Baseline Model
def train_decision_tree():

    df, X, y = (
        prepare_modelling_data()
    )

    (
        X_train,
        X_test,
        y_train,
        y_test,
    ) = chronological_split(
        df,
        X,
        y
    )

    model = (
        build_decision_tree_pipeline(
            X_train
        )
    )

    model.fit(
        X_train,
        y_train
    )

    return (
        model,
        X_train,
        X_test,
        y_train,
        y_test,
    )


