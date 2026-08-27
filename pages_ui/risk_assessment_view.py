import pandas as pd
import plotly.express as px
import streamlit as st

from services.risk_assessment_service import (
    get_latest_risk_assessments,
    save_latest_risk_assessments,
)

from services.audit_service import (
    log_activity
)


def show_risk_assessment():
    """
    Display current next-week risk assessments.
    """

    st.title(
        "Next-Week Security Risk Assessment"
    )

    st.caption(
        "AI-assisted state-level security "
        "risk classification based on the "
        "latest available historical ACLED data."
    )

    # -----------------------------------------
    # GENERATE / REFRESH
    # -----------------------------------------

    if st.button(
        "Run Latest Risk Assessment",
        use_container_width=False
    ):

        with st.spinner(
            "Running selected machine-learning model..."
        ):

            result = (
                save_latest_risk_assessments()
            )

            log_activity(
            st.session_state[
                  "user_id"
            ],
            "Generated latest security "
            "risk assessment."
            )

        if result[
            "inserted"
        ] > 0:

            st.success(
                f"{result['inserted']} "
                "state risk assessments generated."
            )

        else:

            st.info(
                "The latest risk assessments "
                "already exist."
            )

    # -----------------------------------------
    # LOAD CURRENT RESULTS
    # -----------------------------------------

    df = (
        get_latest_risk_assessments()
    )

    if df.empty:

        st.warning(
            "No risk assessment results "
            "are currently available."
        )

        return

    # -----------------------------------------
    # SUMMARY
    # -----------------------------------------

    forecast_week = (
        df[
            "forecast_week"
        ]
        .iloc[0]
    )

    st.subheader(
        f"Forecast Week: "
        f"{forecast_week}"
    )

    low_count = (
        df[
            "risk_level"
        ]
        .eq("Low")
        .sum()
    )

    medium_count = (
        df[
            "risk_level"
        ]
        .eq("Medium")
        .sum()
    )

    high_count = (
        df[
            "risk_level"
        ]
        .eq("High")
        .sum()
    )

    col1, col2, col3, col4 = (
        st.columns(4)
    )

    col1.metric(
        "States Assessed",
        len(df)
    )

    col2.metric(
        "Low Risk",
        int(
            low_count
        )
    )

    col3.metric(
        "Medium Risk",
        int(
            medium_count
        )
    )

    col4.metric(
        "High Risk",
        int(
            high_count
        )
    )

    st.divider()

    # -----------------------------------------
    # RISK DISTRIBUTION
    # -----------------------------------------

    risk_order = [
        "Low",
        "Medium",
        "High"
    ]

    risk_counts = (
        df[
            "risk_level"
        ]
        .value_counts()
        .reindex(
            risk_order,
            fill_value=0
        )
        .reset_index()
    )

    risk_counts.columns = [
        "Risk Level",
        "States"
    ]

    figure = px.bar(
        risk_counts,
        x="Risk Level",
        y="States",
        title=
            "Predicted Security Risk Distribution"
    )

    st.plotly_chart(
        figure,
        use_container_width=True
    )

    # -----------------------------------------
    # STATE TABLE
    # -----------------------------------------

    st.subheader(
        "State-Level Risk Assessment"
    )

    display_df = (
        df[
            [
                "state",
                "assessment_week",
                "forecast_week",
                "risk_level",
                "confidence",
            ]
        ]
        .copy()
    )

    display_df[
        "confidence"
    ] = (
        display_df[
            "confidence"
        ]
        * 100
    ).round(2)

    display_df = (
        display_df.rename(
            columns={
                "state":
                    "State/FCT",

                "assessment_week":
                    "Assessment Week",

                "forecast_week":
                    "Forecast Week",

                "risk_level":
                    "Predicted Risk",

                "confidence":
                    "Confidence (%)",
            }
        )
    )

    # High first
    risk_rank = {
        "High": 1,
        "Medium": 2,
        "Low": 3,
    }

    display_df[
        "_risk_rank"
    ] = (
        display_df[
            "Predicted Risk"
        ]
        .map(
            risk_rank
        )
    )

    display_df = (
        display_df.sort_values(
            [
                "_risk_rank",
                "Confidence (%)"
            ],
            ascending=[
                True,
                False
            ]
        )
        .drop(
            columns=[
                "_risk_rank"
            ]
        )
    )


    selected_state = st.selectbox(
      "Filter by State/FCT",
      [
            "All"
      ]
      +
      sorted(
            df[
                  "state"
            ]
            .unique()
            .tolist()
      )
      )
    if selected_state != "All":

      display_df = (
        display_df[
            display_df[
                "State/FCT"
            ]
            == selected_state
        ]
    )

      selected_risk = st.selectbox(
      "Filter by Risk Level",
      [
            "All",
            "High",
            "Medium",
            "Low",
      ]
      )

      if selected_risk != "All":

       display_df = (
        display_df[
            display_df[
                "Predicted Risk"
            ]
            == selected_risk
        ]
    )

       log_activity(
      st.session_state[
            "user_id"
      ],
      "Generated latest security "
      "risk assessment."
      )



    

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )