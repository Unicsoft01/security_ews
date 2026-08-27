import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd


# --------------------------------------------------
# INPUT FILES
# --------------------------------------------------

DECISION_TREE_MODEL_PATH = Path(
    "models/decision_tree.pkl"
)

RANDOM_FOREST_MODEL_PATH = Path(
    "models/random_forest.pkl"
)

DECISION_TREE_METADATA_PATH = Path(
    "models/decision_tree_metadata.json"
)

RANDOM_FOREST_METADATA_PATH = Path(
    "models/random_forest_metadata.json"
)


# --------------------------------------------------
# OUTPUT FILES
# --------------------------------------------------

SELECTED_MODEL_PATH = Path(
    "models/selected_model.pkl"
)

SELECTED_METADATA_PATH = Path(
    "models/selected_model_metadata.json"
)

COMPARISON_CSV_PATH = Path(
    "data/exports/model_comparison.csv"
)

COMPARISON_PLOT_PATH = Path(
    "data/exports/model_comparison.png"
)


# --------------------------------------------------
# LOAD METADATA
# --------------------------------------------------

def load_metadata(path):

    if not path.exists():

        raise FileNotFoundError(
            f"Metadata file not found: {path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# --------------------------------------------------
# BUILD MODEL COMPARISON TABLE
# --------------------------------------------------

def create_model_comparison():

    decision_tree = load_metadata(
        DECISION_TREE_METADATA_PATH
    )

    random_forest = load_metadata(
        RANDOM_FOREST_METADATA_PATH
    )

    dt_metrics = (
        decision_tree["test_metrics"]
    )

    rf_metrics = (
        random_forest["test_metrics"]
    )

    comparison = pd.DataFrame(
        [
            {
                "model":
                    "Decision Tree",

                "accuracy":
                    dt_metrics[
                        "accuracy"
                    ],

                "precision_macro":
                    dt_metrics[
                        "precision_macro"
                    ],

                "recall_macro":
                    dt_metrics[
                        "recall_macro"
                    ],

                "f1_macro":
                    dt_metrics[
                        "f1_macro"
                    ],

                "high_risk_recall":
                    dt_metrics[
                        "high_risk_recall"
                    ],

                "cv_f1":
                    decision_tree[
                        "cross_validation_f1"
                    ],
            },

            {
                "model":
                    "Random Forest",

                "accuracy":
                    rf_metrics[
                        "accuracy"
                    ],

                "precision_macro":
                    rf_metrics[
                        "precision_macro"
                    ],

                "recall_macro":
                    rf_metrics[
                        "recall_macro"
                    ],

                "f1_macro":
                    rf_metrics[
                        "f1_macro"
                    ],

                "high_risk_recall":
                    rf_metrics[
                        "high_risk_recall"
                    ],

                "cv_f1":
                    random_forest[
                        "cross_validation_f1"
                    ],
            },
        ]
    )

    return comparison



# Model selection rule
def select_best_model(
    comparison
):
    """
    Select final model using:

    1. Macro F1
    2. High-Risk Recall
    3. Accuracy
    """

    ranked = (
        comparison.sort_values(
            by=[
                "f1_macro",
                "high_risk_recall",
                "accuracy"
            ],
            ascending=[
                False,
                False,
                False
            ]
        )
        .reset_index(
            drop=True
        )
    )

    winner = ranked.iloc[0]

    return winner, ranked


# Save the Model Comparison Table
def save_comparison_table(
    comparison
):

    COMPARISON_CSV_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    comparison.to_csv(
        COMPARISON_CSV_PATH,
        index=False
    )

    return COMPARISON_CSV_PATH

# Create the Model Comparison Chart

def save_comparison_chart(
    comparison
):

    metrics = [
        "accuracy",
        "precision_macro",
        "recall_macro",
        "f1_macro",
        "high_risk_recall",
    ]

    chart_data = (
        comparison.set_index(
            "model"
        )[metrics]
        .T
    )

    ax = chart_data.plot(
        kind="bar",
        figsize=(10, 6)
    )

    ax.set_title(
        "Decision Tree vs Random Forest Performance"
    )

    ax.set_ylabel(
        "Score"
    )

    ax.set_xlabel(
        "Evaluation Metric"
    )

    ax.set_ylim(
        0,
        1
    )

    plt.xticks(
        rotation=30,
        ha="right"
    )

    plt.tight_layout()

    COMPARISON_PLOT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    plt.savefig(
        COMPARISON_PLOT_PATH,
        dpi=300
    )

    plt.close()

    return COMPARISON_PLOT_PATH


# Save the Winning Model
def save_selected_model(
    winner
):

    winner_name = (
        winner["model"]
    )

    if winner_name == (
        "Decision Tree"
    ):

        source_model_path = (
            DECISION_TREE_MODEL_PATH
        )

        source_metadata_path = (
            DECISION_TREE_METADATA_PATH
        )

    elif winner_name == (
        "Random Forest"
    ):

        source_model_path = (
            RANDOM_FOREST_MODEL_PATH
        )

        source_metadata_path = (
            RANDOM_FOREST_METADATA_PATH
        )

    else:

        raise ValueError(
            "Unknown model selected."
        )

    if not source_model_path.exists():

        raise FileNotFoundError(
            f"Model file not found: "
            f"{source_model_path}"
        )

    # Load winning trained pipeline
    model = joblib.load(
        source_model_path
    )

    # Save under deployment name
    SELECTED_MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        model,
        SELECTED_MODEL_PATH
    )

    # Load original metadata
    metadata = load_metadata(
        source_metadata_path
    )

    # Add final-selection information
    metadata[
        "selected_for_deployment"
    ] = True

    metadata[
        "selected_model_name"
    ] = winner_name

    metadata[
        "selection_criterion"
    ] = (
        "Highest Macro F1-score, "
        "followed by High-Risk Recall "
        "and Accuracy"
    )

    # Save selected model metadata
    with open(
        SELECTED_METADATA_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metadata,
            file,
            indent=4
        )

    return (
        SELECTED_MODEL_PATH,
        SELECTED_METADATA_PATH,
    )


if __name__ == "__main__":

    comparison = (
        create_model_comparison()
    )

    winner, ranked = (
        select_best_model(
            comparison
        )
    )

    print(
        "\nFINAL MODEL EVALUATION"
    )

    print("=" * 70)

    print(
        "\nMODEL COMPARISON"
    )

    print("=" * 70)

    print(
        comparison.to_string(
            index=False
        )
    )

    print(
        "\nMODEL RANKING"
    )

    print("=" * 70)

    print(
        ranked[
            [
                "model",
                "f1_macro",
                "high_risk_recall",
                "accuracy"
            ]
        ]
        .to_string(
            index=False
        )
    )

    print(
        "\nSELECTED MODEL"
    )

    print("=" * 70)

    print(
        winner["model"]
    )

    print(
        f"\nMacro F1: "
        f"{winner['f1_macro']:.4f}"
    )

    print(
        f"High-Risk Recall: "
        f"{winner['high_risk_recall']:.4f}"
    )

    print(
        f"Accuracy: "
        f"{winner['accuracy']:.4f}"
    )

    csv_path = (
        save_comparison_table(
            comparison
        )
    )

    chart_path = (
        save_comparison_chart(
            comparison
        )
    )

    (
        selected_model_path,
        selected_metadata_path,
    ) = save_selected_model(
        winner
    )

    print(
        f"\nComparison CSV saved to: "
        f"{csv_path}"
    )

    print(
        f"Comparison chart saved to: "
        f"{chart_path}"
    )

    print(
        f"Selected model saved to: "
        f"{selected_model_path}"
    )

    print(
        f"Selected metadata saved to: "
        f"{selected_metadata_path}"
    )