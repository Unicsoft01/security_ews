from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from services.audit_service import (
    log_activity
)

from services.report_service import (
    build_latest_analysis,
    export_csv_report,
    export_excel_report,
    get_priority_risk_analysis,
    get_report_history,
    prepare_export_dataframe,
    save_report_record,
)


def show_reports():
    """
    Display report analysis and
    export interface.
    """

    st.title(
        "Security Risk Analysis Reports"
    )

    st.caption(
        "Review and export the latest "
        "AI-assisted security risk assessment."
    )

    try:

        (
            summary,
            risk_df
        ) = build_latest_analysis()

    except ValueError as error:

        st.warning(
            str(error)
        )

        return

    # -----------------------------------------
    # REPORT PERIOD
    # -----------------------------------------

    st.info(
        f"Assessment Week: "
        f"{summary['assessment_week']}  |  "
        f"Forecast Week: "
        f"{summary['forecast_week']}"
    )

    # -----------------------------------------
    # SUMMARY CARDS
    # -----------------------------------------

    col1, col2, col3, col4 = (
        st.columns(4)
    )

    col1.metric(
        "States/FCT",
        summary[
            "states_assessed"
        ]
    )

    col2.metric(
        "Low Risk",
        summary[
            "low_risk"
        ]
    )

    col3.metric(
        "Medium Risk",
        summary[
            "medium_risk"
        ]
    )

    col4.metric(
        "High Risk",
        summary[
            "high_risk"
        ]
    )

    st.metric(
        "Average Model Confidence",
        f"{summary['average_confidence'] * 100:.2f}%"
    )

    st.divider()

    # -----------------------------------------
    # RISK DISTRIBUTION
    # -----------------------------------------

    distribution = (
        risk_df[
            "risk_level"
        ]
        .value_counts()
        .reindex(
            [
                "Low",
                "Medium",
                "High"
            ],
            fill_value=0
        )
        .reset_index()
    )

    distribution.columns = [
        "Risk Level",
        "States"
    ]

    figure = px.bar(
        distribution,
        x="Risk Level",
        y="States",
        title=
            "Latest Security Risk Distribution"
    )

    st.plotly_chart(
        figure,
        use_container_width=True
    )

    # -----------------------------------------
    # PRIORITY RISK ANALYSIS
    # -----------------------------------------

    st.subheader(
        "Priority Risk Analysis"
    )

    priority_df = (
        get_priority_risk_analysis(
            risk_df
        )
    )

    if priority_df.empty:

        st.info(
            "No High or Medium risk states "
            "were identified."
        )

    else:

        priority_display = (
            prepare_export_dataframe(
                priority_df
            )
        )

        st.dataframe(
            priority_display,
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    # -----------------------------------------
    # FULL STATE REPORT
    # -----------------------------------------

    st.subheader(
        "State-Level Risk Assessment"
    )

    report_df = (
        prepare_export_dataframe(
            risk_df
        )
    )

    st.dataframe(
        report_df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # -----------------------------------------
    # EXPORT REPORTS
    # -----------------------------------------

    st.subheader(
        "Export Analysis"
    )

    export_col1, export_col2 = (
        st.columns(2)
    )

    # -----------------------------------------
    # CSV EXPORT
    # -----------------------------------------

    with export_col1:

        if st.button(
            "Prepare CSV Report",
            use_container_width=True
        ):

            csv_path = (
                export_csv_report(
                    risk_df
                )
            )

            save_report_record(
                user_id=
                    st.session_state[
                        "user_id"
                    ],

                report_type=
                    "CSV Risk Analysis",

                file_path=
                    csv_path
            )

            log_activity(
                st.session_state[
                    "user_id"
                ],
                "Generated CSV security "
                "risk analysis report."
            )

            st.session_state[
                "csv_report_path"
            ] = str(
                csv_path
            )

    # -----------------------------------------
    # EXCEL EXPORT
    # -----------------------------------------

    with export_col2:

        if st.button(
            "Prepare Excel Report",
            use_container_width=True
        ):

            excel_path = (
                export_excel_report(
                    summary,
                    risk_df
                )
            )

            save_report_record(
                user_id=
                    st.session_state[
                        "user_id"
                    ],

                report_type=
                    "Excel Risk Analysis",

                file_path=
                    excel_path
            )

            log_activity(
                st.session_state[
                    "user_id"
                ],
                "Generated Excel security "
                "risk analysis report."
            )

            st.session_state[
                "excel_report_path"
            ] = str(
                excel_path
            )

    # -----------------------------------------
    # DOWNLOAD CSV
    # -----------------------------------------

    csv_path = (
        st.session_state.get(
            "csv_report_path"
        )
    )

    if csv_path:

        csv_file = Path(
            csv_path
        )

        if csv_file.exists():

            with open(
                csv_file,
                "rb"
            ) as file:

                st.download_button(
                    label=
                        "Download CSV Report",

                    data=
                        file.read(),

                    file_name=
                        csv_file.name,

                    mime=
                        "text/csv",

                    use_container_width=True
                )

    # -----------------------------------------
    # DOWNLOAD EXCEL
    # -----------------------------------------

    excel_path = (
        st.session_state.get(
            "excel_report_path"
        )
    )

    if excel_path:

        excel_file = Path(
            excel_path
        )

        if excel_file.exists():

            with open(
                excel_file,
                "rb"
            ) as file:

                st.download_button(
                    label=
                        "Download Excel Report",

                    data=
                        file.read(),

                    file_name=
                        excel_file.name,

                    mime=
                        "application/vnd.openxmlformats-"
                        "officedocument.spreadsheetml.sheet",

                    use_container_width=True
                )

    st.divider()

    # -----------------------------------------
    # REPORT HISTORY
    # -----------------------------------------

    st.subheader(
        "Report History"
    )

    history_df = (
        get_report_history()
    )

    if history_df.empty:

        st.info(
            "No reports have been generated yet."
        )

    else:

        st.dataframe(
            history_df[
                [
                    "report_id",
                    "report_type",
                    "created_at",
                    "file_name",
                ]
            ],
            use_container_width=True,
            hide_index=True
        )