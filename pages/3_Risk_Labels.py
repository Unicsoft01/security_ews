import streamlit as st

from services.risk_labelling import (
    create_labelled_dataset
)


st.set_page_config(
    page_title="Risk Labels",
    layout="wide"
)


st.title(
    "Next-Week Security Risk Labels"
)


@st.cache_data
def get_data():

    return (
        create_labelled_dataset()
    )


df, thresholds = get_data()


labelled = (
    df[
        df[
            "target_risk"
        ]
        .notna()
    ]
)


col1, col2, col3 = (
    st.columns(3)
)


col1.metric(
    "Low Risk",
    f"{(labelled['target_risk'] == 'Low').sum():,}"
)


col2.metric(
    "Medium Risk",
    f"{(labelled['target_risk'] == 'Medium').sum():,}"
)


col3.metric(
    "High Risk",
    f"{(labelled['target_risk'] == 'High').sum():,}"
)


st.subheader(
    "Risk Thresholds"
)


st.write(
    thresholds
)


st.subheader(
    "Risk Distribution"
)


st.bar_chart(
    labelled[
        "target_risk"
    ]
    .value_counts()
)