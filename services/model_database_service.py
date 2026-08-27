import json
from pathlib import Path

from database.connection import (
    SessionLocal
)

from database.models import (
    ModelMetric,
    ModelRun
)


DECISION_TREE_METADATA = Path(
    "models/decision_tree_metadata.json"
)

RANDOM_FOREST_METADATA = Path(
    "models/random_forest_metadata.json"
)

SELECTED_METADATA = Path(
    "models/selected_model_metadata.json"
)


def load_json(path):

    if not path.exists():

        raise FileNotFoundError(
            f"Required metadata file not found: {path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def get_selected_model_name():

    selected_metadata = load_json(
        SELECTED_METADATA
    )

    selected_name = (
        selected_metadata.get(
            "selected_model_name"
        )
    )

    if not selected_name:

        raise ValueError(
            "selected_model_metadata.json "
            "does not contain selected_model_name."
        )

    return selected_name


def store_model_results():

    db = SessionLocal()

    try:

        selected_model_name = (
            get_selected_model_name()
        )

        models = [
            {
                "display_name":
                    "Decision Tree",

                "metadata_path":
                    DECISION_TREE_METADATA,

                "model_file":
                    "models/decision_tree.pkl",
            },
            {
                "display_name":
                    "Random Forest",

                "metadata_path":
                    RANDOM_FOREST_METADATA,

                "model_file":
                    "models/random_forest.pkl",
            },
        ]

        # Prevent duplicate inserts
        existing_count = (
            db.query(
                ModelRun
            )
            .count()
        )

        if existing_count > 0:

            print(
                "\nModel results already exist "
                "in the database."
            )

            print(
                f"Existing model runs: "
                f"{existing_count}"
            )

            return

        for item in models:

            metadata = load_json(
                item[
                    "metadata_path"
                ]
            )

            metrics = (
                metadata[
                    "test_metrics"
                ]
            )

            is_selected = (
                item[
                    "display_name"
                ]
                == selected_model_name
            )

            model_run = ModelRun(

                model_name=
                    item[
                        "display_name"
                    ],

                model_file=
                    item[
                        "model_file"
                    ],

                selected=
                    is_selected
            )

            db.add(
                model_run
            )

            db.flush()

            metric_record = (
                ModelMetric(

                    model_run_id=
                        model_run
                        .model_run_id,

                    accuracy=
                        float(
                            metrics[
                                "accuracy"
                            ]
                        ),

                    precision=
                        float(
                            metrics[
                                "precision_macro"
                            ]
                        ),

                    recall=
                        float(
                            metrics[
                                "recall_macro"
                            ]
                        ),

                    f1_score=
                        float(
                            metrics[
                                "f1_macro"
                            ]
                        ),

                    high_risk_recall=
                        float(
                            metrics[
                                "high_risk_recall"
                            ]
                        )
                )
            )

            db.add(
                metric_record
            )

        db.commit()

        print(
            "\nMODEL DATABASE STORAGE COMPLETE"
        )

        print("=" * 60)

        print(
            f"Selected model: "
            f"{selected_model_name}"
        )

        print(
            "Decision Tree and Random Forest "
            "results stored successfully."
        )

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()


if __name__ == "__main__":

    store_model_results()