from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# PROJECT PATHS
# ============================================================

ROOT = Path(__file__).resolve().parent.parent

RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"

RAW_DATA = (
    RAW_DIR
    / "Africa_aggregated_data_up_to_week_of-2026-08-08.xlsx"
)

PROCESSED_FILES = {
    "Nigeria Raw Data": (
        PROCESSED_DIR / "acled_nigeria_raw.csv"
    ),
    "Nigeria Clean Data": (
        PROCESSED_DIR / "acled_nigeria_clean.csv"
    ),
    "State-Week Dataset": (
        PROCESSED_DIR / "acled_nigeria_state_week.csv"
    ),
    "State-Week Features": (
        PROCESSED_DIR
        / "acled_nigeria_state_week_features.csv"
    ),
    "Machine-Learning Dataset": (
        PROCESSED_DIR
        / "acled_nigeria_ml_dataset.csv"
    ),
}


# ============================================================
# HELPERS
# ============================================================


def _file_size_mb(path: Path) -> float:
    """Return file size in MB."""
    if not path.exists():
        return 0.0

    return path.stat().st_size / (1024 * 1024)


@st.cache_data(show_spinner=False)
def _load_csv(path_string: str) -> pd.DataFrame:
    """Load CSV data."""
    return pd.read_csv(path_string)


@st.cache_data(show_spinner=False)
def _load_excel(path_string: str) -> pd.DataFrame:
    """Load Excel data."""
    return pd.read_excel(path_string)


def _load_dataset(path: Path) -> pd.DataFrame:
    """Load a supported project dataset."""
    suffix = path.suffix.lower()

    if suffix == ".csv":
        return _load_csv(str(path))

    if suffix in {".xlsx", ".xls"}:
        return _load_excel(str(path))

    raise ValueError(
        f"Unsupported file format: {suffix}"
    )


def _format_date_range(
    df: pd.DataFrame,
) -> str:
    """Return WEEK date range where available."""
    if "WEEK" not in df.columns:
        return "Not available"

    dates = pd.to_datetime(
        df["WEEK"],
        errors="coerce",
    ).dropna()

    if dates.empty:
        return "Not available"

    start = dates.min().strftime("%d %b %Y")
    end = dates.max().strftime("%d %b %Y")

    return f"{start} — {end}"


def _download_dataset(
    df: pd.DataFrame,
    file_name: str,
    key: str,
) -> None:
    """Render safe CSV download."""
    csv_data = df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Download Current Dataset as CSV",
        data=csv_data,
        file_name=file_name,
        mime="text/csv",
        key=key,
        use_container_width=True,
    )


# ============================================================
# MAIN PAGE
# ============================================================


def show_dataset_management() -> None:
    """Render Dataset Management page."""

    st.title("Dataset Management")

    st.caption(
        "Inspect the historical ACLED source data and "
        "processed datasets used by the security-risk "
        "assessment pipeline."
    )

    st.info(
        "This interface is intentionally read-only. "
        "The deployed research dataset cannot be "
        "overwritten from this page."
    )

    # --------------------------------------------------------
    # DATASET INVENTORY
    # --------------------------------------------------------

    st.subheader("Dataset Inventory")

    inventory = []

    all_files = {
        "Original ACLED Africa Dataset": RAW_DATA,
        **PROCESSED_FILES,
    }

    for name, path in all_files.items():
        inventory.append(
            {
                "Dataset": name,
                "Status": (
                    "Available"
                    if path.exists()
                    else "Missing"
                ),
                "Format": (
                    path.suffix.upper()
                    .replace(".", "")
                ),
                "Size (MB)": round(
                    _file_size_mb(path),
                    2,
                ),
                "Location": str(
                    path.relative_to(ROOT)
                ),
            }
        )

    inventory_df = pd.DataFrame(inventory)

    st.dataframe(
        inventory_df,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    # --------------------------------------------------------
    # SELECT DATASET
    # --------------------------------------------------------

    st.subheader("Inspect Dataset")

    available_files = {
        name: path
        for name, path in all_files.items()
        if path.exists()
    }

    if not available_files:
        st.error(
            "No project datasets were found."
        )
        return

    selected_name = st.selectbox(
        "Select dataset",
        options=list(
            available_files.keys()
        ),
    )

    selected_path = available_files[
        selected_name
    ]

    with st.spinner(
        "Loading dataset..."
    ):
        try:
            df = _load_dataset(
                selected_path
            )

        except Exception as exc:
            st.error(
                "The selected dataset could not "
                f"be loaded: {exc}"
            )
            return

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Rows",
        f"{len(df):,}",
    )

    col2.metric(
        "Columns",
        f"{len(df.columns):,}",
    )

    col3.metric(
        "Missing Values",
        f"{int(df.isna().sum().sum()):,}",
    )

    if "ADMIN1" in df.columns:
        states = (
            df["ADMIN1"]
            .dropna()
            .astype(str)
            .nunique()
        )

        col4.metric(
            "States / FCT",
            states,
        )

    else:
        col4.metric(
            "File Size",
            f"{_file_size_mb(selected_path):.2f} MB",
        )

    st.caption(
        f"Date coverage: "
        f"{_format_date_range(df)}"
    )

    # --------------------------------------------------------
    # PREVIEW
    # --------------------------------------------------------

    st.subheader("Dataset Preview")

    preview_rows = st.slider(
        "Rows to preview",
        min_value=5,
        max_value=100,
        value=20,
        step=5,
    )

    st.dataframe(
        df.head(preview_rows),
        use_container_width=True,
        hide_index=True,
    )

    # --------------------------------------------------------
    # COLUMN INFORMATION
    # --------------------------------------------------------

    with st.expander(
        "View Column Information"
    ):
        column_info = pd.DataFrame(
            {
                "Column": df.columns,
                "Data Type": [
                    str(dtype)
                    for dtype
                    in df.dtypes
                ],
                "Missing Values": [
                    int(
                        df[column]
                        .isna()
                        .sum()
                    )
                    for column
                    in df.columns
                ],
                "Unique Values": [
                    int(
                        df[column]
                        .nunique(
                            dropna=True
                        )
                    )
                    for column
                    in df.columns
                ],
            }
        )

        st.dataframe(
            column_info,
            use_container_width=True,
            hide_index=True,
        )

    # --------------------------------------------------------
    # NIGERIA COVERAGE
    # --------------------------------------------------------

    if "ADMIN1" in df.columns:
        with st.expander(
            "View State / FCT Coverage"
        ):
            states = sorted(
                df["ADMIN1"]
                .dropna()
                .astype(str)
                .unique()
            )

            st.write(
                f"**Distinct ADMIN1 units:** "
                f"{len(states)}"
            )

            state_df = pd.DataFrame(
                {
                    "State / FCT": states
                }
            )

            st.dataframe(
                state_df,
                use_container_width=True,
                hide_index=True,
            )

    # --------------------------------------------------------
    # DOWNLOAD
    # --------------------------------------------------------

    st.divider()

    st.subheader("Export Dataset")

    st.caption(
        "Exports a copy for inspection. "
        "The project source dataset is not modified."
    )

    safe_name = (
        selected_name
        .lower()
        .replace(" ", "_")
        .replace("/", "_")
    )

    _download_dataset(
        df,
        f"{safe_name}.csv",
        f"download_{safe_name}",
    )