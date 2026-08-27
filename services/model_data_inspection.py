from services.training import (
    chronological_split,
    prepare_modelling_data,
)


def inspect_model_data():

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

    print(
        "\nTRAINING CLASS DISTRIBUTION"
    )

    print("=" * 60)

    print(
        y_train.value_counts()
    )

    print(
        "\nTRAINING PERCENTAGES"
    )

    print(
        y_train.value_counts(
            normalize=True
        )
        * 100
    )

    print(
        "\nTEST CLASS DISTRIBUTION"
    )

    print("=" * 60)

    print(
        y_test.value_counts()
    )

    print(
        "\nTEST PERCENTAGES"
    )

    print(
        y_test.value_counts(
            normalize=True
        )
        * 100
    )


if __name__ == "__main__":

    inspect_model_data()