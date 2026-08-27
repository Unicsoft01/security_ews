from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
import matplotlib.pyplot as plt
from sklearn.metrics import (
    ConfusionMatrixDisplay
)


def evaluate_classifier(
    model,
    X_test,
    y_test
):

    predictions = model.predict(
        X_test
    )

    metrics = {
        "accuracy":
            accuracy_score(
                y_test,
                predictions
            ),

        "precision_macro":
            precision_score(
                y_test,
                predictions,
                average="macro",
                zero_division=0
            ),

        "recall_macro":
            recall_score(
                y_test,
                predictions,
                average="macro",
                zero_division=0
            ),

        "f1_macro":
            f1_score(
                y_test,
                predictions,
                average="macro",
                zero_division=0
            ),
    }

    report = (
        classification_report(
            y_test,
            predictions,
            zero_division=0
        )
    )

    matrix = (
        confusion_matrix(
            y_test,
            predictions,
            labels=[
                "Low",
                "Medium",
                "High"
            ]
        )
    )

    high_risk_recall = recall_score(
            y_test,
            predictions,
            labels=["High"],
            average="macro",
            zero_division=0
      )
    metrics[
      "high_risk_recall"
      ] = high_risk_recall

    return (
        metrics,
        report,
        matrix,
        predictions,
    )



def save_confusion_matrix(
    model,
    X_test,
    y_test,
    output_path,
    title="Confusion Matrix"
):

    predictions = model.predict(
        X_test
    )

    ConfusionMatrixDisplay.from_predictions(
        y_test,
        predictions,
        labels=[
            "Low",
            "Medium",
            "High"
        ]
    )

    plt.title(
        title
    )

    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=300
    )

    plt.close()
