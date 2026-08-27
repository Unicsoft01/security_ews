import pandas as pd
import plotly.express as px
import streamlit as st

from services.dashboard_service import (
    get_dashboard_summary,
    get_events_by_state,
    get_fatalities_by_state,
    get_weekly_event_trend,
    get_dataset_date_range
)


def show_dashboard():
    """
    Display main dashboard.
    """

    st.title(
        "Security Risk Dashboard"
    )

    st.caption(
        "Historical ACLED security incident "
        "overview for Nigeria"
    )

    summary = (
        get_dashboard_summary()
    )

    # -----------------------------------------
    # SUMMARY CARDS
    # -----------------------------------------

    col1, col2, col3, col4 = (
        st.columns(4)
    )

    col1.metric(
        "Represented Events",
        f"{summary['represented_events']:,}"
    )

    col2.metric(
        "Recorded Fatalities",
        f"{summary['fatalities']:,}"
    )

    col3.metric(
        "States / FCT",
        f"{summary['locations']:,}"
    )

    col4.metric(
        "Active Alerts",
        f"{summary['active_alerts']:,}"
    )

    st.divider()

    # -----------------------------------------
    # EVENTS BY STATE
    # -----------------------------------------

    events_data = (
        get_events_by_state()
    )

    events_df = pd.DataFrame(
        events_data
    )

    if not events_df.empty:

        top_events = (
            events_df
            .sort_values(
                "events",
                ascending=False
            )
            .head(10)
        )

        figure = px.bar(
            top_events,
            x="events",
            y="state",
            orientation="h",
            title=
                "Top 10 States by Represented Events"
        )

        figure.update_layout(
            yaxis={
                "categoryorder":
                    "total ascending"
            }
        )

        st.plotly_chart(
            figure,
            use_container_width=True
        )



      # Add Fatality Chart
    fatalities_data = (
        get_fatalities_by_state()
    )

    fatalities_df = (
        pd.DataFrame(
            fatalities_data
        )
    )

    if not fatalities_df.empty:

        top_fatalities = (
            fatalities_df
            .sort_values(
                "fatalities",
                ascending=False
            )
            .head(10)
        )

        fatality_figure = px.bar(
            top_fatalities,
            x="fatalities",
            y="state",
            orientation="h",
            title=
                "Top 10 States by Recorded Fatalities"
        )

        fatality_figure.update_layout(
            yaxis={
                "categoryorder":
                    "total ascending"
            }
        )

        st.plotly_chart(
            fatality_figure,
            use_container_width=True
        )


    # -----------------------------------------
    # WEEKLY TREND
    # -----------------------------------------

    trend_data = (
        get_weekly_event_trend()
    )

    trend_df = pd.DataFrame(
        trend_data
    )

    if not trend_df.empty:

        trend_df["week"] = (
            pd.to_datetime(
                trend_df["week"]
            )
        )

        trend_figure = px.line(
            trend_df,
            x="week",
            y="events",
            title=
                "Weekly Security Event Trend"
        )

        st.plotly_chart(
            trend_figure,
            use_container_width=True
        )


    earliest, latest = (
    get_dataset_date_range()
    )

    if earliest and latest:

        st.caption(
            f"Dataset coverage: "
            f"{earliest} to {latest}"
        )