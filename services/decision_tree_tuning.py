import json
from pathlib import Path

import joblib

from sklearn.model_selection import (
    GridSearchCV,
    TimeSeriesSplit,
)

from sklearn.pipeline import Pipeline

from sklearn.tree import (
    DecisionTreeClassifier
)

from services.evaluation import (
    evaluate_classifier
)

from services.training import (
    build_preprocessor,
    chronological_split,
    prepare_modelling_data,
)

from services.model_interpretation import (
    get_feature_importance
)


# --------------------------------------------------
# OUTPUT PATHS
# --------------------------------------------------

MODEL_PATH = Path(
    "models/decision_tree.pkl"
)

METADATA_PATH = Path(
    "models/decision_tree_metadata.json"
)


# --------------------------------------------------
# DECISION TREE TUNING
# --------------------------------------------------

def tune_decision_tree():
    """
    Train and tune the Decision Tree classifier
    using time-aware cross-validation.
    """

    # Prepare modelling dataset
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

    # Build preprocessing pipeline
    preprocessor = (
        build_preprocessor(
            X_train
        )
    )

    # Base classifier
    classifier = (
        DecisionTreeClassifier(
            random_state=42,
            class_weight="balanced"
        )
    )

    # Complete pipeline
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

    # Hyperparameter search space
    parameter_grid = {

        "classifier__criterion": [
            "gini",
            "entropy"
        ],

        "classifier__max_depth": [
            4,
            6,
            8,
            10,
            12,
            None
        ],

        "classifier__min_samples_split": [
            2,
            5,
            10,
            20
        ],

        "classifier__min_samples_leaf": [
            1,
            5,
            10,
            20
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

    # Train all candidate models
    grid_search.fit(
        X_train,
        y_train
    )

    # Best model
    best_model = (
        grid_search.best_estimator_
    )

    # Evaluate on unseen test data
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

def save_decision_tree_model(
    grid_search,
    best_model,
    metrics
):
    """
    Save tuned Decision Tree model and metadata.
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
            "DecisionTreeClassifier",

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
# RUN TUNING
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
    ) = tune_decision_tree()

    print(
        "\nDECISION TREE TUNING COMPLETE"
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


# --------------------------------------------------
# FEATURE IMPORTANCE
# --------------------------------------------------

importance = (
    get_feature_importance(
        best_model
    )
)

EXPORT_PATH = Path(
    "data/exports/"
    "decision_tree_feature_importance.csv"
)

EXPORT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

importance.to_csv(
    EXPORT_PATH,
    index=False
)



print(
    f"\nFeature importance saved to: "
    f"{EXPORT_PATH}"
)




print(
    "\nTOP 20 MOST IMPORTANT FEATURES"
)

print("=" * 60)

print(
    importance.head(20).to_string(
        index=False
    )
)


# --------------------------------------------------
# SAVE MODEL AND METADATA
# --------------------------------------------------

save_decision_tree_model(
    grid_search,
    best_model,
    metrics
)