from pathlib import Path

from services.model_service import (
    load_selected_model
)

from services.training import (
    chronological_split,
    prepare_modelling_data,
)


MODEL_PATH = Path(
    "models/selected_model.pkl"
)


def test_selected_model_exists():

    assert MODEL_PATH.exists()


def test_selected_model_loads():

    model = (
        load_selected_model()
    )

    assert model is not None


def test_selected_model_predicts():

    model = (
        load_selected_model()
    )

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

    predictions = (
        model.predict(
            X_test.head(10)
        )
    )

    assert len(
        predictions
    ) == 10


def test_selected_model_valid_classes():

    model = (
        load_selected_model()
    )

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