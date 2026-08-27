import pandas as pd
import streamlit as st

from services.alert_service import (
    generate_latest_alerts,
    get_latest_alerts,
    update_alert_status,
)

from services.audit_service import (
    log_activity
)


def show_alerts():
    """
    Display generated early-warning alerts.
    """

    st.title(
        "Early Warning Alerts"
    )

    st.caption(
        "Warnings generated from the latest "
        "AI-assisted security risk assessments."
    )

    # -----------------------------------------
    # GENERATE ALERTS
    # -----------------------------------------

    if st.button(
        "Generate Latest Alerts"
    ):

        with st.spinner(
            "Generating warning messages..."
        ):

            result = (
                generate_latest_alerts()
            )

        log_activity(
            st.session_state[
                "user_id"
            ],
            "Generated latest early-warning alerts."
        )

        if (
            result.get(
                "created",
                0
            )
            > 0
        ):

            st.success(
                f"{result['created']} "
                "new alerts generated."
            )

        else:

            st.info(
                "No new alerts were generated. "
                "Existing alerts were retained."
            )

        st.rerun()

    # -----------------------------------------
    # LOAD ALERTS
    # -----------------------------------------

    df = (
        get_latest_alerts()
    )

    if df.empty:

        st.warning(
            "No alerts are currently available."
        )

        return

    # -----------------------------------------
    # SUMMARY CARDS
    # -----------------------------------------

    high_count = (
        df[
            "alert_level"
        ]
        .eq("High")
        .sum()
    )

    medium_count = (
        df[
            "alert_level"
        ]
        .eq("Medium")
        .sum()
    )

    active_count = (
        df[
            "status"
        ]
        .eq("active")
        .sum()
    )

    col1, col2, col3, col4 = (
        st.columns(4)
    )

    col1.metric(
        "Total Alerts",
        len(df)
    )

    col2.metric(
        "High Priority",
        int(
            high_count
        )
    )

    col3.metric(
        "Monitoring",
        int(
            medium_count
        )
    )

    col4.metric(
        "Active",
        int(
            active_count
        )
    )

    st.divider()

    # -----------------------------------------
    # FILTERS
    # -----------------------------------------

    filter_col1, filter_col2 = (
        st.columns(2)
    )

    with filter_col1:

        selected_level = (
            st.selectbox(
                "Alert Level",
                [
                    "All",
                    "High",
                    "Medium",
                ]
            )
        )

    with filter_col2:

        selected_status = (
            st.selectbox(
                "Alert Status",
                [
                    "All",
                    "active",
                    "reviewed",
                    "resolved",
                ]
            )
        )

    filtered_df = (
        df.copy()
    )

    if selected_level != "All":

        filtered_df = (
            filtered_df[
                filtered_df[
                    "alert_level"
                ]
                == selected_level
            ]
        )

    if selected_status != "All":

        filtered_df = (
            filtered_df[
                filtered_df[
                    "status"
                ]
                == selected_status
            ]
        )

    # -----------------------------------------
    # DISPLAY ALERT CARDS
    # -----------------------------------------

    risk_rank = {
        "High": 1,
        "Medium": 2,
    }

    filtered_df[
        "_risk_rank"
    ] = (
        filtered_df[
            "alert_level"
        ]
        .map(
            risk_rank
        )
    )

    filtered_df = (
        filtered_df.sort_values(
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

    for _, row in (
        filtered_df.iterrows()
    ):

        confidence = (
            row[
                "confidence"
            ]
            * 100
        )

        if (
            row[
                "alert_level"
            ]
            == "High"
        ):

            icon = "🔴"

        else:

            icon = "🟠"

        with st.container(
            border=True
        ):

            st.subheader(
                f"{icon} "
                f"{row['state']} — "
                f"{row['alert_level']} Risk"
            )

            st.write(
                row[
                    "message"
                ]
            )

            detail_col1, detail_col2, detail_col3 = (
                st.columns(3)
            )

            detail_col1.metric(
                "Confidence",
                f"{confidence:.2f}%"
            )

            detail_col2.metric(
                "Forecast Week",
                str(
                    row[
                        "forecast_week"
                    ]
                )
            )

            detail_col3.metric(
                "Status",
                row[
                    "status"
                ].title()
            )

            new_status = (
                st.selectbox(
                    "Update Status",
                    [
                        "active",
                        "reviewed",
                        "resolved",
                    ],
                    index=[
                        "active",
                        "reviewed",
                        "resolved",
                    ].index(
                        row[
                            "status"
                        ]
                    ),
                    key=
                        f"alert_status_"
                        f"{row['alert_id']}"
                )
            )

            if st.button(
                "Save Status",
                key=
                    f"save_alert_"
                    f"{row['alert_id']}"
            ):

                success = (
                    update_alert_status(
                        int(
                            row[
                                "alert_id"
                            ]
                        ),
                        new_status
                    )
                )

                if success:

                    log_activity(
                        st.session_state[
                            "user_id"
                        ],
                        f"Updated alert "
                        f"{row['alert_id']} "
                        f"to {new_status}."
                    )

                    st.success(
                        "Alert status updated."
                    )

                    st.rerun()