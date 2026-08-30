import json
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# PROJECT PATHS
# ============================================================

ROOT = Path(__file__).resolve().parent.parent

MODELS_DIR = ROOT / "models"
EXPORTS_DIR = ROOT / "data" / "exports"

DT_METADATA = (
    MODELS_DIR
    / "decision_tree_metadata.json"
)

RF_METADATA = (
    MODELS_DIR
    / "random_forest_metadata.json"
)

SELECTED_METADATA = (
    MODELS_DIR
    / "selected_model_metadata.json"
)

MODEL_COMPARISON_CSV = (
    EXPORTS_DIR
    / "model_comparison.csv"
)

MODEL_COMPARISON_IMAGE = (
    EXPORTS_DIR
    / "model_comparison.png"
)

DT_CONFUSION_MATRIX = (
    EXPORTS_DIR
    / "decision_tree_confusion_matrix.png"
)

RF_CONFUSION_MATRIX = (
    EXPORTS_DIR
    / "random_forest_confusion_matrix.png"
)

DT_IMPORTANCE = (
    EXPORTS_DIR
    / "decision_tree_feature_importance.csv"
)

RF_IMPORTANCE = (
    EXPORTS_DIR
    / "random_forest_feature_importance.csv"
)


# ============================================================
# LOADERS
# ============================================================


@st.cache_data(show_spinner=False)
def _load_json(
    path_string: str,
) -> dict:
    path = Path(path_string)

    if not path.exists():
        return {}

    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        return json.load(handle)


@st.cache_data(show_spinner=False)
def _load_csv(
    path_string: str,
) -> pd.DataFrame:
    path = Path(path_string)

    if not path.exists():
        return pd.DataFrame()

    return pd.read_csv(path)


def _metric(
    metadata: dict,
    key: str,
):
    metrics = metadata.get(
        "test_metrics",
        {},
    )

    return metrics.get(key)


def _format_metric(
    value,
) -> str:
    if value is None:
        return "N/A"

    try:
        return f"{float(value):.4f}"

    except (
        TypeError,
        ValueError,
    ):
        return str(value)


def _model_name(
    metadata: dict,
    fallback: str,
) -> str:
    return (
        metadata.get(
            "selected_model_name"
        )
        or metadata.get("model")
        or fallback
    )


# ============================================================
# FEATURE IMPORTANCE
# ============================================================


def _show_feature_importance(
    path: Path,
    title: str,
) -> None:

    st.markdown(
        f"#### {title}"
    )

    if not path.exists():
        st.info(
            "Feature-importance output "
            "is not available."
        )
        return

    df = _load_csv(str(path))

    if df.empty:
        st.info(
            "Feature-importance file "
            "contains no records."
        )
        return

    st.dataframe(
        df.head(20),
        use_container_width=True,
        hide_index=True,
    )

    # Attempt automatic charting
    # without assuming exact column names.
    numeric_columns = (
        df.select_dtypes(
            include="number"
        ).columns.tolist()
    )

    text_columns = [
        column
        for column in df.columns
        if column not in numeric_columns
    ]

    if (
        numeric_columns
        and text_columns
    ):
        value_col = numeric_columns[0]
        label_col = text_columns[0]

        chart_df = (
            df[
                [
                    label_col,
                    value_col,
                ]
            ]
            .dropna()
            .sort_values(
                value_col,
                ascending=False,
            )
            .head(15)
            .set_index(label_col)
        )

        st.bar_chart(
            chart_df,
            use_container_width=True,
        )


# ============================================================
# MAIN PAGE
# ============================================================


def show_model_evaluation() -> None:
    """Render model evaluation interface."""

    st.title("Model Evaluation")

    st.caption(
        "Review the performance of the Decision Tree "
        "and Random Forest classifiers used for "
        "next-week state-level security risk prediction."
    )

    # --------------------------------------------------------
    # LOAD METADATA
    # --------------------------------------------------------

    dt_metadata = _load_json(
        str(DT_METADATA)
    )

    rf_metadata = _load_json(
        str(RF_METADATA)
    )

    selected_metadata = (
        _load_json(
            str(SELECTED_METADATA)
        )
    )

    # --------------------------------------------------------
    # SELECTED MODEL
    # --------------------------------------------------------

    st.subheader(
        "Selected Deployment Model"
    )

    selected_name = (
        selected_metadata.get(
            "selected_model_name"
        )
        or selected_metadata.get(
            "model"
        )
        or "Not available"
    )

    selection_criterion = (
        selected_metadata.get(
            "selection_criterion",
            (
                "Highest Macro F1-score, "
                "followed by High-Risk Recall "
                "and Accuracy"
            ),
        )
    )

    st.success(
        f"Selected Model: {selected_name}"
    )

    st.write(
        f"**Selection Criterion:** "
        f"{selection_criterion}"
    )

    selected_metrics = (
        selected_metadata.get(
            "test_metrics",
            {}
        )
    )

    if selected_metrics:
        col1, col2, col3 = (
            st.columns(3)
        )

        col1.metric(
            "Accuracy",
            _format_metric(
                selected_metrics.get(
                    "accuracy"
                )
            ),
        )

        col2.metric(
            "Macro F1",
            _format_metric(
                selected_metrics.get(
                    "f1_macro"
                )
            ),
        )

        col3.metric(
            "High-Risk Recall",
            _format_metric(
                selected_metrics.get(
                    "high_risk_recall"
                )
            ),
        )

        col4, col5 = st.columns(2)

        col4.metric(
            "Macro Precision",
            _format_metric(
                selected_metrics.get(
                    "precision_macro"
                )
            ),
        )

        col5.metric(
            "Macro Recall",
            _format_metric(
                selected_metrics.get(
                    "recall_macro"
                )
            ),
        )

    st.divider()

    # --------------------------------------------------------
    # MODEL COMPARISON
    # --------------------------------------------------------

    st.subheader(
        "Decision Tree vs Random Forest"
    )

    comparison_df = _load_csv(
        str(MODEL_COMPARISON_CSV)
    )

    if not comparison_df.empty:
        st.dataframe(
            comparison_df,
            use_container_width=True,
            hide_index=True,
        )

    else:
        # Fallback table generated directly
        # from metadata.
        rows = []

        for label, metadata in [
            (
                "Decision Tree",
                dt_metadata,
            ),
            (
                "Random Forest",
                rf_metadata,
            ),
        ]:
            if not metadata:
                continue

            rows.append(
                {
                    "Model": label,
                    "Accuracy": _metric(
                        metadata,
                        "accuracy",
                    ),
                    "Macro Precision": _metric(
                        metadata,
                        "precision_macro",
                    ),
                    "Macro Recall": _metric(
                        metadata,
                        "recall_macro",
                    ),
                    "Macro F1": _metric(
                        metadata,
                        "f1_macro",
                    ),
                    "High-Risk Recall": _metric(
                        metadata,
                        "high_risk_recall",
                    ),
                }
            )

        if rows:
            fallback_df = (
                pd.DataFrame(rows)
            )

            st.dataframe(
                fallback_df,
                use_container_width=True,
                hide_index=True,
            )

        else:
            st.warning(
                "Model-comparison results "
                "could not be located."
            )

    # --------------------------------------------------------
    # MODEL COMPARISON IMAGE
    # --------------------------------------------------------

    if MODEL_COMPARISON_IMAGE.exists():
        st.markdown(
            "#### Performance Comparison"
        )

        st.image(
            str(
                MODEL_COMPARISON_IMAGE
            ),
            use_container_width=True,
        )

    # --------------------------------------------------------
    # CONFUSION MATRICES
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "Confusion Matrices"
    )

    st.caption(
        "Confusion matrices show correct and "
        "incorrect classifications across the "
        "Low, Medium, and High risk classes."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            "#### Decision Tree"
        )

        if (
            DT_CONFUSION_MATRIX.exists()
        ):
            st.image(
                str(
                    DT_CONFUSION_MATRIX
                ),
                use_container_width=True,
            )

        else:
            st.info(
                "Decision Tree confusion "
                "matrix not found."
            )

    with col2:
        st.markdown(
            "#### Random Forest"
        )

        if (
            RF_CONFUSION_MATRIX.exists()
        ):
            st.image(
                str(
                    RF_CONFUSION_MATRIX
                ),
                use_container_width=True,
            )

        else:
            st.info(
                "Random Forest confusion "
                "matrix not found."
            )

    # --------------------------------------------------------
    # FEATURE IMPORTANCE
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "Feature Importance"
    )

    tab1, tab2 = st.tabs(
        [
            "Decision Tree",
            "Random Forest",
        ]
    )

    with tab1:
        _show_feature_importance(
            DT_IMPORTANCE,
            (
                "Decision Tree "
                "Feature Importance"
            ),
        )

    with tab2:
        _show_feature_importance(
            RF_IMPORTANCE,
            (
                "Random Forest "
                "Feature Importance"
            ),
        )

    # --------------------------------------------------------
    # MODEL METADATA
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "Model Configuration"
    )

    config_tab1, config_tab2 = (
        st.tabs(
            [
                "Decision Tree",
                "Random Forest",
            ]
        )
    )

    with config_tab1:
        if dt_metadata:
            st.write(
                "**Model:**",
                _model_name(
                    dt_metadata,
                    "Decision Tree",
                ),
            )

            parameters = (
                dt_metadata.get(
                    "best_parameters",
                    {},
                )
            )

            if parameters:
                st.markdown(
                    "**Best Parameters**"
                )

                st.json(parameters)

            cv_score = (
                dt_metadata.get(
                    "cross_validation_f1"
                )
            )

            if cv_score is not None:
                st.write(
                    "**Cross-Validation "
                    "Macro F1:**",
                    f"{cv_score:.4f}",
                )

        else:
            st.info(
                "Decision Tree metadata "
                "is unavailable."
            )

    with config_tab2:
        if rf_metadata:
            st.write(
                "**Model:**",
                _model_name(
                    rf_metadata,
                    "Random Forest",
                ),
            )

            parameters = (
                rf_metadata.get(
                    "best_parameters",
                    {},
                )
            )

            if parameters:
                st.markdown(
                    "**Best Parameters**"
                )

                st.json(parameters)

            cv_score = (
                rf_metadata.get(
                    "cross_validation_f1"
                )
            )

            if cv_score is not None:
                st.write(
                    "**Cross-Validation "
                    "Macro F1:**",
                    f"{cv_score:.4f}",
                )

        else:
            st.info(
                "Random Forest metadata "
                "is unavailable."
            )

    # --------------------------------------------------------
    # METRIC DEFINITIONS
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "Evaluation Metrics"
    )

    metric_df = pd.DataFrame(
        [
            {
                "Metric": "Accuracy",
                "Meaning": (
                    "Overall proportion of "
                    "correct classifications."
                ),
            },
            {
                "Metric": (
                    "Macro Precision"
                ),
                "Meaning": (
                    "Average precision across "
                    "Low, Medium, and High "
                    "risk classes."
                ),
            },
            {
                "Metric": "Macro Recall",
                "Meaning": (
                    "Average recall across "
                    "all three risk classes."
                ),
            },
            {
                "Metric": "Macro F1",
                "Meaning": (
                    "Balances precision and "
                    "recall while giving each "
                    "risk class equal weight."
                ),
            },
            {
                "Metric": (
                    "High-Risk Recall"
                ),
                "Meaning": (
                    "Ability to identify "
                    "observations that are "
                    "actually High risk."
                ),
            },
        ]
    )

    st.dataframe(
        metric_df,
        use_container_width=True,
        hide_index=True,
    )

    # --------------------------------------------------------
    # INTERPRETATION WARNING
    # --------------------------------------------------------

    st.warning(
        "Model evaluation reflects performance "
        "on the chronological historical test "
        "dataset. A High-risk prediction is a "
        "relative risk estimate and does not "
        "guarantee that a security incident "
        "will occur."
    )