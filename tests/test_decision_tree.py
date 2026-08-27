from services.training import (
    chronological_split,
    prepare_modelling_data,
    train_decision_tree,
)


def test_modelling_dataset():

    df, X, y = (
        prepare_modelling_data()
    )

    assert not X.empty

    assert len(X) == len(y)


def test_no_target_in_features():

    df, X, y = (
        prepare_modelling_data()
    )

    assert (
        "target_risk"
        not in X.columns
    )


def test_no_future_severity_in_features():

    df, X, y = (
        prepare_modelling_data()
    )

    assert (
        "next_week_severity_score"
        not in X.columns
    )


def test_train_test_not_empty():

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

    assert not X_train.empty

    assert not X_test.empty


def test_decision_tree_trains():

    (
        model,
        X_train,
        X_test,
        y_train,
        y_test,
    ) = train_decision_tree()

    predictions = model.predict(
        X_test.head(10)
    )

    assert len(predictions) == 10