from services.model_service import (
    load_selected_model
)

from services.training import (
    chronological_split,
    prepare_modelling_data,
)


def test_selected_model():

    # Load final model
    model = (
        load_selected_model()
    )

    # Prepare modelling dataset
    df, X, y = (
        prepare_modelling_data()
    )

    # Obtain the same chronological split
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

    # Use a small sample
    sample = (
        X_test.head(10)
    )

    actual = (
        y_test.head(10)
    )

    # Generate predictions
    predictions = (
        model.predict(
            sample
        )
    )

    print(
        "\nSELECTED MODEL PREDICTION TEST"
    )

    print("=" * 70)

    print(
        f"Number of test records: "
        f"{len(sample)}"
    )

    print(
        "\nActual Risk     Predicted Risk"
    )

    print("-" * 40)

    for actual_risk, predicted_risk in zip(
        actual,
        predictions
    ):

        print(
            f"{actual_risk:<15}"
            f"{predicted_risk}"
        )

    print(
        "\nSelected model prediction "
        "test completed successfully."
    )


if __name__ == "__main__":

    test_selected_model()