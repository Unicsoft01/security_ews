from services.evaluation import (
    evaluate_classifier
)

from services.training import (
    train_decision_tree
)


def run_baseline_decision_tree():

    (
        model,
        X_train,
        X_test,
        y_train,
        y_test,
    ) = train_decision_tree()

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
        "\nDECISION TREE BASELINE RESULTS"
    )

    print("=" * 60)

    print(
        f"Training records: "
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

    run_baseline_decision_tree()