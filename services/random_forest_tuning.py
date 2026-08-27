import json
from pathlib import Path

import joblib

from sklearn.ensemble import (
    RandomForestClassifier
)

from sklearn.model_selection import (
    GridSearchCV,
    TimeSeriesSplit,
)

from sklearn.pipeline import Pipeline

from services.evaluation import (
    evaluate_classifier,
    save_confusion_matrix,
)

from services.model_interpretation import (
    get_feature_importance
)

from services.training import (
    build_preprocessor,
    chronological_split,
    prepare_modelling_data,
)


# --------------------------------------------------
# OUTPUT PATHS
# --------------------------------------------------

MODEL_PATH = Path(
    "models/random_forest.pkl"
)

METADATA_PATH = Path(
    "models/random_forest_metadata.json"
)

FEATURE_IMPORTANCE_PATH = Path(
    "data/exports/"
    "random_forest_feature_importance.csv"
)


# --------------------------------------------------
# RANDOM FOREST TUNING
# --------------------------------------------------

def tune_random_forest():
    """
    Tune Random Forest using time-aware
    cross-validation.
    """

    # Prepare exactly the same modelling data
    # used for Decision Tree.
    df, X, y = (
        prepare_modelling_data()
    )

    # Chronological train/test split
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

    # Preprocessing
    preprocessor = (
        build_preprocessor(
            X_train
        )
    )

    # Base Random Forest
    classifier = (
        RandomForestClassifier(
            random_state=42,
            class_weight="balanced",
            n_jobs=-1
        )
    )

    # Full pipeline
    pipeline = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor
            ),
            (
                "classifier",
                classifier
            ),
        ]
    )

    # ----------------------------------------------
    # HYPERPARAMETER SEARCH SPACE
    # ----------------------------------------------

    parameter_grid = {

        "classifier__n_estimators": [
            100,
            200,
            300
        ],

        "classifier__max_depth": [
            8,
            12,
            16,
            None
        ],

        "classifier__min_samples_split": [
            2,
            5,
            10
        ],

        "classifier__min_samples_leaf": [
            1,
            3,
            5,
            10
        ],

        "classifier__max_features": [
            "sqrt",
            "log2"
        ],
    }

    # Time-aware cross-validation
    time_cv = TimeSeriesSplit(
        n_splits=5
    )

    # Grid search
    grid_search = GridSearchCV(
        estimator=pipeline,
        param_grid=parameter_grid,
        scoring="f1_macro",
        cv=time_cv,
        n_jobs=-1,
        verbose=1
    )

    # Train candidate models
    grid_search.fit(
        X_train,
        y_train
    )

    # Best-performing model
    best_model = (
        grid_search.best_estimator_
    )

    # Test on unseen chronological test set
    (
        metrics,
        report,
        matrix,
        predictions,
    ) = evaluate_classifier(
        best_model,
        X_test,
        y_test
    )

    return (
        grid_search,
        best_model,
        metrics,
        report,
        matrix,
        predictions,
        X_train,
        X_test,
        y_train,
        y_test,
    )


# --------------------------------------------------
# SAVE MODEL AND METADATA
# --------------------------------------------------

def save_random_forest_model(
    grid_search,
    best_model,
    metrics
):
    """
    Save trained Random Forest and its metadata.
    """

    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save trained model
    joblib.dump(
        best_model,
        MODEL_PATH
    )

    # Prepare metadata
    metadata = {
        "model":
            "RandomForestClassifier",

        "best_parameters":
            grid_search.best_params_,

        "cross_validation_f1":
            float(
                grid_search.best_score_
            ),

        "test_metrics": {
            key:
                float(value)

            for key, value
            in metrics.items()
        },
    }

    # Save metadata JSON
    with open(
        METADATA_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metadata,
            file,
            indent=4
        )

    print(
        f"\nModel saved to: "
        f"{MODEL_PATH}"
    )

    print(
        f"Metadata saved to: "
        f"{METADATA_PATH}"
    )


# --------------------------------------------------
# RUN RANDOM FOREST TUNING
# --------------------------------------------------

if __name__ == "__main__":

    (
        grid_search,
        best_model,
        metrics,
        report,
        matrix,
        predictions,
        X_train,
        X_test,
        y_train,
        y_test,
    ) = tune_random_forest()

    print(
        "\nRANDOM FOREST TUNING COMPLETE"
    )

    print("=" * 60)

    print(
        f"\nTraining records: "
        f"{len(X_train):,}"
    )

    print(
        f"Testing records: "
        f"{len(X_test):,}"
    )

    print(
        "\nBEST PARAMETERS"
    )

    print("=" * 60)

    print(
        grid_search.best_params_
    )

    print(
        "\nBEST CV MACRO F1"
    )

    print("=" * 60)

    print(
        f"{grid_search.best_score_:.4f}"
    )

    print(
        "\nTEST METRICS"
    )

    print("=" * 60)

    for key, value in (
        metrics.items()
    ):

        print(
            f"{key}: "
            f"{value:.4f}"
        )

    print(
        "\nCLASSIFICATION REPORT"
    )

    print("=" * 60)

    print(report)

    print(
        "\nCONFUSION MATRIX"
    )

    print("=" * 60)

    print(matrix)

    # ----------------------------------------------
    # SAVE CONFUSION MATRIX IMAGE
    # ----------------------------------------------

    CONFUSION_MATRIX_PATH = Path(
            "data/exports/"
            "random_forest_confusion_matrix.png"
      )

    CONFUSION_MATRIX_PATH.parent.mkdir(
      parents=True,
      exist_ok=True
      )

    save_confusion_matrix(
      best_model,
      X_test,
      y_test,
      CONFUSION_MATRIX_PATH,
      title="Random Forest Confusion Matrix"
      )

    print(
      "\nConfusion matrix saved to: "
      f"{CONFUSION_MATRIX_PATH}"
      )


    # ----------------------------------------------
    # FEATURE IMPORTANCE
    # ----------------------------------------------

    importance = (
        get_feature_importance(
            best_model
        )
    )

    print(
        "\nTOP 20 MOST IMPORTANT FEATURES"
    )

    print("=" * 60)

    print(
        importance.head(20)
        .to_string(
            index=False
        )
    )


    # ----------------------------------------------
    # SAVE FEATURE IMPORTANCE
    # ----------------------------------------------

    FEATURE_IMPORTANCE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    importance.to_csv(
        FEATURE_IMPORTANCE_PATH,
        index=False
    )

    print(
        "\nFeature importance saved to: "
        f"{FEATURE_IMPORTANCE_PATH}"
    )


    # ----------------------------------------------
    # SAVE RANDOM FOREST MODEL
    # ----------------------------------------------

    save_random_forest_model(
        grid_search,
        best_model,
        metrics
    )