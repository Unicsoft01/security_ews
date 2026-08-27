import streamlit as st

from services.data_loader import (
    load_raw_dataset,
    filter_nigeria
)

from services.validator import (
    validate_required_columns
)


st.set_page_config(
    page_title="Dataset Inspection",
    layout="wide"
)

st.title(
    "ACLED Dataset Inspection"
)


@st.cache_data
def get_data():

    raw = load_raw_dataset()

    nigeria = filter_nigeria(raw)

    return raw, nigeria


raw_df, nigeria_df = get_data()

validation = validate_required_columns(
    raw_df
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Africa Records",
    f"{len(raw_df):,}"
)

col2.metric(
    "Nigeria Records",
    f"{len(nigeria_df):,}"
)

col3.metric(
    "States / FCT",
    nigeria_df["ADMIN1"].nunique()
)

col4.metric(
    "Columns",
    len(nigeria_df.columns)
)

st.divider()

if validation["valid"]:

    st.success(
        "All required ACLED columns are present."
    )

else:

    st.error(
        "Required columns are missing."
    )

    st.write(
        validation["missing_columns"]
    )

st.subheader(
    "Nigeria Dataset Preview"
)

st.dataframe(
    nigeria_df.head(100),
    use_container_width=True
)

st.subheader(
    "Missing Values"
)

missing = (
    nigeria_df
    .isna()
    .sum()
    .reset_index()
)

missing.columns = [
    "Column",
    "Missing Values"
]

st.dataframe(
    missing,
    use_container_width=True
)

st.subheader(
    "Event Types"
)

event_counts = (
    nigeria_df[
        "EVENT_TYPE"
    ]
    .value_counts()
)

st.bar_chart(
    event_counts
)