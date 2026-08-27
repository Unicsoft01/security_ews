import json
from datetime import datetime
from pathlib import Path

from database.connection import (
    SessionLocal
)

from database.models import (
    ModelMetric,
    ModelRun
)


MODELS = [
    {
        "name":
            "Decision Tree",

        "file":
            "models/decision_tree.pkl",

        "metadata":
            "models/"
            "decision_tree_metadata.json",
    },

    {
        "name":
            "Random Forest",

        "file":
            "models/random_forest.pkl",

        "metadata":
            "models/"
            "random_forest_metadata.json",
    },
]


def store_model_results(
    selected_model_name
):

    db = SessionLocal()

    try:

        for item in MODELS:

            metadata_path = Path(
                item["metadata"]
            )

            with open(
                metadata_path,
                "r",
                encoding="utf-8"
            ) as file:

                metadata = (
                    json.load(file)
                )

            metrics = (
                metadata[
                    "test_metrics"
                ]
            )

            model_run = ModelRun(
                model_name=
                    item["name"],

                model_file=
                    item["file"],

                selected=(
                    item["name"]
                    == selected_model_name
                ),

                trained_at=
                    datetime.utcnow()
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
                        metrics[
                            "accuracy"
                        ],

                    precision=
                        metrics[
                            "precision_macro"
                        ],

                    recall=
                        metrics[
                            "recall_macro"
                        ],

                    f1_score=
                        metrics[
                            "f1_macro"
                        ],

                    high_risk_recall=
                        metrics[
                            "high_risk_recall"
                        ],
                )
            )

            db.add(
                metric_record
            )

        db.commit()

        print(
            "Model results stored "
            "successfully."
        )

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()