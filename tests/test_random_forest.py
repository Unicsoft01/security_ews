from services.random_forest_training import (
    train_random_forest
)

from services.training import (
    chronological_split,
    prepare_modelling_data,
)


def test_random_forest_trains():

    (
        model,
        X_train,
        X_test,
        y_train,
        y_test,
    ) = train_random_forest()

    predictions = (
        model.predict(
            X_test.head(10)
        )
    )

    assert len(
        predictions
    ) == 10


def test_random_forest_valid_classes():

    (
        model,
        X_train,
        X_test,
        y_train,
        y_test,
    ) = train_random_forest()

    predictions = (
        model.predict(
            X_test.head(100)
        )
    )

    valid_classes = {
        "Low",
        "Medium",
        "High",
    }

    assert set(
        predictions
    ).issubset(
        valid_classes
    )


def test_random_forest_same_split():

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

    assert len(
        X_train
    ) > 0

    assert len(
        X_test
    ) > 0