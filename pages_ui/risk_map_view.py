import pandas as pd
import plotly.express as px
import streamlit as st

from services.risk_assessment_service import (
    get_latest_risk_assessments
)


RISK_COLORS = {
    "Low": "#2E8B57",
    "Medium": "#F4A261",
    "High": "#D62828",
}


RISK_ORDER = {
    "High": 1,
    "Medium": 2,
    "Low": 3,
}


def prepare_map_data():
    """
    Retrieve and validate the latest
    state-level risk assessments.
    """

    df = (
        get_latest_risk_assessments()
    )

    if df.empty:
        return df

    df = df.copy()

    required_columns = [
        "state",
        "latitude",
        "longitude",
        "assessment_week",
        "forecast_week",
        "risk_level",
        "confidence",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            "Risk map data is missing "
            f"required columns: "
            f"{missing_columns}"
        )

    # Remove records without usable coordinates
    df = df.dropna(
        subset=[
            "latitude",
            "longitude"
        ]
    ).copy()

    # Ensure numeric coordinates
    df["latitude"] = (
        pd.to_numeric(
            df["latitude"],
            errors="coerce"
        )
    )

    df["longitude"] = (
        pd.to_numeric(
            df["longitude"],
            errors="coerce"
        )
    )

    df = df.dropna(
        subset=[
            "latitude",
            "longitude"
        ]
    )

    # Defensive duplicate handling
    df = (
        df.sort_values(
            [
                "state",
                "confidence"
            ],
            ascending=[
                True,
                False
            ]
        )
        .drop_duplicates(
            subset=[
                "state"
            ],
            keep="first"
        )
        .reset_index(
            drop=True
        )
    )

    return df


def show_risk_map():
    """
    Display the geographic security-risk
    assessment for Nigerian states/FCT.
    """

    st.title(
        "Nigeria Security Risk Map"
    )

    st.caption(
        "Geographic visualisation of the "
        "latest AI-assisted next-week "
        "security risk assessment."
    )

    df = prepare_map_data()

    if df.empty:

        st.warning(
            "No stored risk assessments "
            "are available. Run the Risk "
            "Assessment page first."
        )

        return

    # -----------------------------------------
    # FORECAST INFORMATION
    # -----------------------------------------

    assessment_week = (
        df[
            "assessment_week"
        ]
        .iloc[0]
    )

    forecast_week = (
        df[
            "forecast_week"
        ]
        .iloc[0]
    )

    st.info(
        f"Assessment Week: {assessment_week}  |  "
        f"Forecast Week: {forecast_week}"
    )

    # -----------------------------------------
    # SUMMARY CARDS
    # -----------------------------------------

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
        "States/FCT Mapped",
        len(df)
    )

    col2.metric(
        "Low Risk",
        int(low_count)
    )

    col3.metric(
        "Medium Risk",
        int(medium_count)
    )

    col4.metric(
        "High Risk",
        int(high_count)
    )

    st.divider()

    # -----------------------------------------
    # STATE SELECTION
    # -----------------------------------------

    selected_state = st.selectbox(
        "Highlight State/FCT",
        [
            "All States"
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

    # -----------------------------------------
    # STATE SUMMARY
    # -----------------------------------------

    if selected_state != (
        "All States"
    ):

        state_record = (
            df[
                df[
                    "state"
                ]
                == selected_state
            ]
            .iloc[0]
        )

        st.subheader(
            f"{selected_state} Risk Summary"
        )

        state_col1, state_col2, state_col3 = (
            st.columns(3)
        )

        state_col1.metric(
            "Predicted Risk",
            state_record[
                "risk_level"
            ]
        )

        state_col2.metric(
            "Confidence",
            f"{state_record['confidence'] * 100:.2f}%"
        )

        state_col3.metric(
            "Forecast Week",
            str(
                state_record[
                    "forecast_week"
                ]
            )
        )

        st.divider()

    # -----------------------------------------
    # RISK-LEVEL FILTER
    # -----------------------------------------

    selected_risks = (
        st.multiselect(
            "Display Risk Levels",
            options=[
                "High",
                "Medium",
                "Low"
            ],
            default=[
                "High",
                "Medium",
                "Low"
            ]
        )
    )

    filtered_df = (
        df[
            df[
                "risk_level"
            ]
            .isin(
                selected_risks
            )
        ]
        .copy()
    )

    # If a specific state is selected,
    # keep that state in focus.
    if selected_state != (
        "All States"
    ):

        filtered_df = (
            filtered_df[
                filtered_df[
                    "state"
                ]
                == selected_state
            ]
            .copy()
        )

    if filtered_df.empty:

        st.warning(
            "No states match the selected "
            "map filters."
        )

        return

    # Convert confidence for display
    filtered_df[
        "confidence_percent"
    ] = (
        filtered_df[
            "confidence"
        ]
        * 100
    ).round(2)

    # -----------------------------------------
    # GEOGRAPHIC RISK MAP
    # -----------------------------------------

    figure = px.scatter_geo(
        filtered_df,
        lat="latitude",
        lon="longitude",
        color="risk_level",
        size="confidence",
        hover_name="state",

        hover_data={
            "risk_level": True,
            "confidence_percent": True,
            "latitude": False,
            "longitude": False,
            "confidence": False,
        },

        color_discrete_map=
            RISK_COLORS,

        category_orders={
            "risk_level": [
                "High",
                "Medium",
                "Low"
            ]
        },

        labels={
            "risk_level":
                "Risk Level",

            "confidence_percent":
                "Confidence (%)",
        },

        title=
            "Predicted Next-Week Security Risk "
            "by Nigerian State/FCT"
    )

    figure.update_geos(
        visible=True,
        resolution=50,
        showcountries=True,
        countrycolor="gray",
        showcoastlines=True,
        coastlinecolor="gray",
        showland=True,
        landcolor="#F4F4F4",

        lataxis_range=[
            4,
            14.5
        ],

        lonaxis_range=[
            2,
            15
        ]
    )

    figure.update_layout(
        height=650,

        margin={
            "l": 0,
            "r": 0,
            "t": 60,
            "b": 0
        }
    )

    st.plotly_chart(
        figure,
        use_container_width=True
    )

    st.caption(
        "Markers represent state/FCT centroid "
        "coordinates from the ACLED dataset; "
        "they do not represent exact incident "
        "locations. Marker size represents "
        "model classification confidence."
    )

    # -----------------------------------------
    # RISK INTERPRETATION
    # -----------------------------------------

    st.markdown(
        """
        **Risk Interpretation**

        - 🟢 **Low:** comparatively lower predicted
          security threat level for the forecast week.
        - 🟠 **Medium:** elevated conditions requiring
          closer monitoring.
        - 🔴 **High:** comparatively higher predicted
          security threat requiring priority attention.
        """
    )

    st.divider()

    # -----------------------------------------
    # PRIORITY RISK AREAS
    # -----------------------------------------

    st.subheader(
        "Priority Risk Areas"
    )

    priority_df = (
        df[
            df[
                "risk_level"
            ]
            .isin(
                [
                    "High",
                    "Medium"
                ]
            )
        ]
        .copy()
    )

    priority_df[
        "_risk_rank"
    ] = (
        priority_df[
            "risk_level"
        ]
        .map(
            RISK_ORDER
        )
    )

    priority_df = (
        priority_df.sort_values(
            [
                "_risk_rank",
                "confidence"
            ],
            ascending=[
                True,
                False
            ]
        )
    )

    priority_df[
        "confidence"
    ] = (
        priority_df[
            "confidence"
        ]
        * 100
    ).round(2)

    priority_df = (
        priority_df[
            [
                "state",
                "risk_level",
                "confidence",
                "forecast_week"
            ]
        ]
        .rename(
            columns={
                "state":
                    "State/FCT",

                "risk_level":
                    "Risk Level",

                "confidence":
                    "Confidence (%)",

                "forecast_week":
                    "Forecast Week",
            }
        )
    )

    if priority_df.empty:

        st.info(
            "No High or Medium risk states "
            "are present in the latest assessment."
        )

    else:

        st.dataframe(
            priority_df,
            use_container_width=True,
            hide_index=True
        )