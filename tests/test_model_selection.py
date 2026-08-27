from pathlib import Path

import joblib

from services.model_comparison import (
    create_model_comparison,
    select_best_model,
)

from services.training import (
    chronological_split,
    prepare_modelling_data,
)


SELECTED_MODEL_PATH = Path(
    "models/selected_model.pkl"
)


def test_comparison_contains_models():

    comparison = (
        create_model_comparison()
    )

    models = set(
        comparison["model"]
    )

    assert models == {
        "Decision Tree",
        "Random Forest",
    }


def test_best_model_selected():

    comparison = (
        create_model_comparison()
    )

    winner, ranked = (
        select_best_model(
            comparison
        )
    )

    assert winner["model"] in {
        "Decision Tree",
        "Random Forest",
    }


def test_selected_model_exists():

    assert (
        SELECTED_MODEL_PATH.exists()
    )


def test_selected_model_predicts():

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
        SELECTED_MODEL_PATH
    )

    predictions = model.predict(
        X_test.head(10)
    )

    assert len(
        predictions
    ) == 10