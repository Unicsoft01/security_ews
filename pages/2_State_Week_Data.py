import streamlit as st

from services.state_week_aggregation import (
    create_state_week_dataset
)


st.set_page_config(
    page_title=
        "State-Week Dataset",
    layout="wide"
)


st.title(
    "Nigeria State-Week "
    "Security Dataset"
)


@st.cache_data
def get_state_week_data():

    return (
        create_state_week_dataset()
    )


df = get_state_week_data()


col1, col2, col3, col4 = (
    st.columns(4)
)


col1.metric(
    "State-Week Records",
    f"{len(df):,}"
)


col2.metric(
    "States/FCT",
    df[
        "ADMIN1"
    ].nunique()
)


col3.metric(
    "Represented Events",
    f"{df['total_events'].sum():,}"
)


col4.metric(
    "Recorded Fatalities",
    f"{df['total_fatalities'].sum():,}"
)


st.divider()


state = st.selectbox(
    "Select State/FCT",
    sorted(
        df[
            "ADMIN1"
        ].unique()
    )
)


state_df = (
    df[
        df[
            "ADMIN1"
        ] == state
    ]
    .sort_values(
        "WEEK"
    )
)


st.subheader(
    f"{state} Weekly Records"
)


st.dataframe(
    state_df.tail(100),
    use_container_width=True
)


st.subheader(
    "Weekly Events"
)


chart_df = (
    state_df[
        [
            "WEEK",
            "total_events"
        ]
    ]
    .set_index(
        "WEEK"
    )
)


st.line_chart(
    chart_df
)
