from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# PROJECT PATHS
# ============================================================

ROOT = Path(__file__).resolve().parent.parent

PROCESSED_DIR = ROOT / "data" / "processed"

CLEAN_DATA = (
    PROCESSED_DIR
    / "acled_nigeria_clean.csv"
)

STATE_WEEK_DATA = (
    PROCESSED_DIR
    / "acled_nigeria_state_week.csv"
)

FEATURE_DATA = (
    PROCESSED_DIR
    / "acled_nigeria_state_week_features.csv"
)

ML_DATA = (
    PROCESSED_DIR
    / "acled_nigeria_ml_dataset.csv"
)


# ============================================================
# DATA LOADING
# ============================================================


@st.cache_data(show_spinner=False)
def _load_csv(
    path_string: str,
) -> pd.DataFrame:
    return pd.read_csv(path_string)


def _safe_load(
    path: Path,
) -> pd.DataFrame | None:
    if not path.exists():
        return None

    try:
        return _load_csv(str(path))

    except Exception:
        return None


def _date_range(
    df: pd.DataFrame,
) -> str:
    if "WEEK" not in df.columns:
        return "Not available"

    dates = pd.to_datetime(
        df["WEEK"],
        errors="coerce",
    ).dropna()

    if dates.empty:
        return "Not available"

    return (
        f"{dates.min():%d %b %Y} — "
        f"{dates.max():%d %b %Y}"
    )


# ============================================================
# FEATURE GROUP IDENTIFICATION
# ============================================================


def _identify_feature_groups(
    columns: list[str],
) -> dict[str, list[str]]:

    lag_features = [
        column
        for column in columns
        if (
            "lag" in column.lower()
            or "_1wk" in column.lower()
        )
    ]

    rolling_features = [
        column
        for column in columns
        if any(
            token in column.lower()
            for token in [
                "rolling",
                "roll_",
                "mean_",
                "avg_",
            ]
        )
    ]

    trend_features = [
        column
        for column in columns
        if any(
            token in column.lower()
            for token in [
                "change",
                "trend",
                "pct_change",
            ]
        )
    ]

    temporal_features = [
        column
        for column in columns
        if any(
            token in column.lower()
            for token in [
                "year",
                "month",
                "week_of_year",
                "quarter",
            ]
        )
    ]

    event_features = [
        column
        for column in columns
        if any(
            token in column.lower()
            for token in [
                "event",
                "fatal",
                "battle",
                "violence",
                "attack",
                "abduction",
                "riot",
                "protest",
                "explosion",
                "suicide",
                "armed",
            ]
        )
    ]

    return {
        "Lag Features": sorted(
            set(lag_features)
        ),
        "Rolling Features": sorted(
            set(rolling_features)
        ),
        "Trend Features": sorted(
            set(trend_features)
        ),
        "Temporal Features": sorted(
            set(temporal_features)
        ),
        "Event / Severity Features": sorted(
            set(event_features)
        ),
    }


# ============================================================
# MAIN PAGE
# ============================================================


def show_data_processing() -> None:
    """Render Data Processing page."""

    st.title("Data Processing")

    st.caption(
        "Review the transformation of historical "
        "security-event records into the state-week "
        "features used by the machine-learning models."
    )

    st.info(
        "Processing shown on this page reflects the "
        "prepared project datasets. The interface does "
        "not modify the deployed model or source data."
    )

    # --------------------------------------------------------
    # PROCESS FLOW
    # --------------------------------------------------------

    st.subheader(
        "Data Processing Pipeline"
    )

    st.code(
        """
ACLED Africa Dataset
        ↓
Nigeria Filtering
        ↓
Data Cleaning
        ↓
State-Week Aggregation
        ↓
Feature Engineering
        ↓
Next-Week Risk Labelling
        ↓
Machine-Learning Dataset
""",
        language="text",
    )

    # --------------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------------

    clean_df = _safe_load(
        CLEAN_DATA
    )

    state_week_df = _safe_load(
        STATE_WEEK_DATA
    )

    feature_df = _safe_load(
        FEATURE_DATA
    )

    ml_df = _safe_load(
        ML_DATA
    )

    # --------------------------------------------------------
    # PROCESSING STAGES
    # --------------------------------------------------------

    st.subheader(
        "Processing Stage Summary"
    )

    stages = [
        {
            "Stage": "Clean Nigeria Data",
            "File": (
                "acled_nigeria_clean.csv"
            ),
            "Status": (
                "Available"
                if clean_df is not None
                else "Missing"
            ),
            "Rows": (
                len(clean_df)
                if clean_df is not None
                else 0
            ),
            "Columns": (
                len(clean_df.columns)
                if clean_df is not None
                else 0
            ),
        },
        {
            "Stage": "State-Week Aggregation",
            "File": (
                "acled_nigeria_state_week.csv"
            ),
            "Status": (
                "Available"
                if state_week_df
                is not None
                else "Missing"
            ),
            "Rows": (
                len(state_week_df)
                if state_week_df
                is not None
                else 0
            ),
            "Columns": (
                len(state_week_df.columns)
                if state_week_df
                is not None
                else 0
            ),
        },
        {
            "Stage": "Feature Engineering",
            "File": (
                "acled_nigeria_"
                "state_week_features.csv"
            ),
            "Status": (
                "Available"
                if feature_df is not None
                else "Missing"
            ),
            "Rows": (
                len(feature_df)
                if feature_df
                is not None
                else 0
            ),
            "Columns": (
                len(feature_df.columns)
                if feature_df
                is not None
                else 0
            ),
        },
        {
            "Stage": (
                "Machine-Learning Dataset"
            ),
            "File": (
                "acled_nigeria_ml_dataset.csv"
            ),
            "Status": (
                "Available"
                if ml_df is not None
                else "Missing"
            ),
            "Rows": (
                len(ml_df)
                if ml_df is not None
                else 0
            ),
            "Columns": (
                len(ml_df.columns)
                if ml_df is not None
                else 0
            ),
        },
    ]

    stage_df = pd.DataFrame(stages)

    stage_df["Rows"] = (
        stage_df["Rows"]
        .map(lambda value: f"{value:,}")
    )

    st.dataframe(
        stage_df,
        use_container_width=True,
        hide_index=True,
    )

    if feature_df is None:
        st.error(
            "The engineered feature dataset "
            "could not be located."
        )
        return

    # --------------------------------------------------------
    # FEATURE DATA METRICS
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "Engineered Feature Dataset"
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Observations",
        f"{len(feature_df):,}",
    )

    col2.metric(
        "Feature Columns",
        f"{len(feature_df.columns):,}",
    )

    if "ADMIN1" in feature_df.columns:
        locations = (
            feature_df["ADMIN1"]
            .dropna()
            .nunique()
        )
    else:
        locations = 0

    col3.metric(
        "States / FCT",
        locations,
    )

    col4.metric(
        "Missing Values",
        f"{int(feature_df.isna().sum().sum()):,}",
    )

    st.caption(
        f"Feature-data coverage: "
        f"{_date_range(feature_df)}"
    )

    # --------------------------------------------------------
    # CORE SECURITY FEATURES
    # --------------------------------------------------------

    st.subheader(
        "Core Security Features"
    )

    core_features = [
        "total_events",
        "total_fatalities",
        "violent_events",
        "high_severity_events",
        "battles",
        "violence_against_civilians",
        "explosions_remote_violence",
        "riots",
        "protests",
        "armed_clashes",
        "attacks",
        "abductions",
        "remote_explosives_ied",
        "suicide_bombs",
    ]

    existing_core = [
        feature
        for feature in core_features
        if feature in feature_df.columns
    ]

    if existing_core:
        core_df = pd.DataFrame(
            {
                "Feature": existing_core,
                "Non-Null Values": [
                    int(
                        feature_df[feature]
                        .notna()
                        .sum()
                    )
                    for feature
                    in existing_core
                ],
                "Missing Values": [
                    int(
                        feature_df[feature]
                        .isna()
                        .sum()
                    )
                    for feature
                    in existing_core
                ],
            }
        )

        st.dataframe(
            core_df,
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.warning(
            "No expected core feature names "
            "were detected."
        )

    # --------------------------------------------------------
    # FEATURE GROUPS
    # --------------------------------------------------------

    st.subheader(
        "Engineered Feature Groups"
    )

    feature_groups = (
        _identify_feature_groups(
            list(feature_df.columns)
        )
    )

    group_summary = pd.DataFrame(
        [
            {
                "Feature Group": group,
                "Detected Columns": len(
                    columns
                ),
            }
            for group, columns
            in feature_groups.items()
        ]
    )

    st.dataframe(
        group_summary,
        use_container_width=True,
        hide_index=True,
    )

    for group, columns in (
        feature_groups.items()
    ):
        with st.expander(
            f"{group} ({len(columns)})"
        ):
            if columns:
                st.code(
                    "\n".join(columns),
                    language="text",
                )
            else:
                st.caption(
                    "No columns detected in "
                    "this feature group."
                )

    # --------------------------------------------------------
    # MISSING DATA
    # --------------------------------------------------------

    st.subheader(
        "Missing-Value Inspection"
    )

    missing = (
        feature_df
        .isna()
        .sum()
        .sort_values(
            ascending=False
        )
    )

    missing = missing[
        missing > 0
    ]

    if missing.empty:
        st.success(
            "No missing values were detected "
            "in the engineered feature dataset."
        )

    else:
        missing_df = (
            missing
            .rename(
                "Missing Values"
            )
            .reset_index()
            .rename(
                columns={
                    "index": "Column"
                }
            )
        )

        missing_df[
            "Missing Percentage"
        ] = (
            missing_df[
                "Missing Values"
            ]
            / len(feature_df)
            * 100
        ).round(2)

        st.dataframe(
            missing_df,
            use_container_width=True,
            hide_index=True,
        )

    # --------------------------------------------------------
    # DATA PREVIEW
    # --------------------------------------------------------

    st.subheader(
        "Processed Feature Preview"
    )

    display_columns = [
        column
        for column in [
            "WEEK",
            "ADMIN1",
            "total_events",
            "total_fatalities",
            "violent_events",
            "high_severity_events",
        ]
        if column in feature_df.columns
    ]

    if display_columns:
        preview_df = (
            feature_df[
                display_columns
            ]
            .tail(50)
        )

    else:
        preview_df = (
            feature_df.tail(50)
        )

    st.dataframe(
        preview_df,
        use_container_width=True,
        hide_index=True,
    )

    # --------------------------------------------------------
    # METHODOLOGICAL NOTE
    # --------------------------------------------------------

    st.warning(
        "Temporal Integrity: Lag, rolling, and "
        "trend features must be generated using "
        "historical information only. Future-week "
        "information must not be allowed to leak "
        "into predictors for an earlier week."
    )