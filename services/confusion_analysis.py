import joblib

from sklearn.metrics import (
    confusion_matrix
)

from services.training import (
    chronological_split,
    prepare_modelling_data,
)


MODEL_PATH = (
    "models/selected_model.pkl"
)


def analyse_selected_model():

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

    model = joblib.load(
        MODEL_PATH
    )

    predictions = model.predict(
        X_test
    )

    labels = [
        "Low",
        "Medium",
        "High"
    ]

    matrix = confusion_matrix(
        y_test,
        predictions,
        labels=labels
    )

    print(
        "\nSELECTED MODEL CONFUSION MATRIX"
    )

    print("=" * 60)

    print(matrix)

    print(
        "\nINTERPRETATION"
    )

    print("=" * 60)

    for actual_index, actual in (
        enumerate(labels)
    ):

        for predicted_index, predicted in (
            enumerate(labels)
        ):

            count = matrix[
                actual_index,
                predicted_index
            ]

            print(
                f"Actual {actual} → "
                f"Predicted {predicted}: "
                f"{count:,}"
            )


if __name__ == "__main__":

    analyse_selected_model()