from sklearn.ensemble import (
    RandomForestClassifier
)

from sklearn.pipeline import Pipeline

from services.evaluation import (
    evaluate_classifier
)

from services.training import (
    build_preprocessor,
    chronological_split,
    prepare_modelling_data,
)


def build_random_forest_pipeline(X):
    """
    Build the baseline Random Forest pipeline.
    """

    preprocessor = (
        build_preprocessor(X)
    )

    classifier = (
        RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            class_weight="balanced",
            n_jobs=-1
        )
    )

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

    return pipeline


def train_random_forest():
    """
    Train baseline Random Forest using
    chronological train/test data.
    """

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
        build_random_forest_pipeline(
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


def run_baseline_random_forest():

    (
        model,
        X_train,
        X_test,
        y_train,
        y_test,
    ) = train_random_forest()

    (
        metrics,
        report,
        matrix,
        predictions,
    ) = evaluate_classifier(
        model,
        X_test,
        y_test
    )

    print(
        "\nRANDOM FOREST BASELINE RESULTS"
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
        "\nMETRICS"
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


if __name__ == "__main__":

    run_baseline_random_forest()