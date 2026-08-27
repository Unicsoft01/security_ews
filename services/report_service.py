from datetime import datetime
from pathlib import Path

import pandas as pd

from database.connection import (
    SessionLocal
)

from database.models import (
    Report
)

from services.alert_service import (
    get_latest_alerts
)

from services.risk_assessment_service import (
    get_latest_risk_assessments
)


EXPORT_DIR = Path(
    "data/exports/reports"
)


def build_latest_analysis():
    """
    Build a structured analysis report from
    the latest stored security risk assessments.
    """

    risk_df = (
        get_latest_risk_assessments()
    )

    if risk_df.empty:

        raise ValueError(
            "No risk assessments are available "
            "for report generation."
        )

    risk_df = risk_df.copy()

    # -----------------------------------------
    # RISK SUMMARY
    # -----------------------------------------

    total_states = len(
        risk_df
    )

    low_count = (
        risk_df[
            "risk_level"
        ]
        .eq("Low")
        .sum()
    )

    medium_count = (
        risk_df[
            "risk_level"
        ]
        .eq("Medium")
        .sum()
    )

    high_count = (
        risk_df[
            "risk_level"
        ]
        .eq("High")
        .sum()
    )

    average_confidence = (
        risk_df[
            "confidence"
        ]
        .mean()
    )

    assessment_week = (
        risk_df[
            "assessment_week"
        ]
        .iloc[0]
    )

    forecast_week = (
        risk_df[
            "forecast_week"
        ]
        .iloc[0]
    )

    summary = {
        "assessment_week":
            assessment_week,

        "forecast_week":
            forecast_week,

        "states_assessed":
            int(total_states),

        "low_risk":
            int(low_count),

        "medium_risk":
            int(medium_count),

        "high_risk":
            int(high_count),

        "average_confidence":
            float(
                average_confidence
            ),
    }

    return (
        summary,
        risk_df
    )





def get_priority_risk_analysis(
    risk_df
):
    """
    Return High and Medium risk states,
    prioritised by risk and confidence.
    """

    priority = (
        risk_df[
            risk_df[
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

    risk_rank = {
        "High": 1,
        "Medium": 2,
        "Low": 3,
    }

    priority[
        "_risk_rank"
    ] = (
        priority[
            "risk_level"
        ]
        .map(
            risk_rank
        )
    )

    priority = (
        priority.sort_values(
            [
                "_risk_rank",
                "confidence"
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

    return priority



# Create a Clean Export Table


def prepare_export_dataframe(
    risk_df
):
    """
    Prepare state-level analysis table
    for report export.
    """

    export_df = (
        risk_df[
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

    export_df[
        "confidence"
    ] = (
        export_df[
            "confidence"
        ]
        * 100
    ).round(2)

    export_df = (
        export_df.rename(
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

    risk_rank = {
        "High": 1,
        "Medium": 2,
        "Low": 3,
    }

    export_df[
        "_risk_rank"
    ] = (
        export_df[
            "Predicted Risk"
        ]
        .map(
            risk_rank
        )
    )

    export_df = (
        export_df.sort_values(
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
        .reset_index(
            drop=True
        )
    )

    return export_df




# Export CSV Report

def export_csv_report(
    risk_df
):
    """
    Export latest state-level risk
    analysis as CSV.
    """

    EXPORT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    export_df = (
        prepare_export_dataframe(
            risk_df
        )
    )

    timestamp = (
        datetime.now()
        .strftime(
            "%Y%m%d_%H%M%S"
        )
    )

    file_path = (
        EXPORT_DIR
        /
        f"security_risk_report_"
        f"{timestamp}.csv"
    )

    export_df.to_csv(
        file_path,
        index=False
    )

    return file_path


def export_excel_report(
    summary,
    risk_df
):
    """
    Export security risk analysis
    as an Excel workbook.
    """

    EXPORT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = (
        datetime.now()
        .strftime(
            "%Y%m%d_%H%M%S"
        )
    )

    file_path = (
        EXPORT_DIR
        /
        f"security_risk_report_"
        f"{timestamp}.xlsx"
    )

    export_df = (
        prepare_export_dataframe(
            risk_df
        )
    )

    priority_df = (
        get_priority_risk_analysis(
            risk_df
        )
    )

    priority_export = (
        prepare_export_dataframe(
            priority_df
        )
    )

    summary_df = pd.DataFrame(
        [
            {
                "Metric":
                    "Assessment Week",

                "Value":
                    summary[
                        "assessment_week"
                    ],
            },
            {
                "Metric":
                    "Forecast Week",

                "Value":
                    summary[
                        "forecast_week"
                    ],
            },
            {
                "Metric":
                    "States/FCT Assessed",

                "Value":
                    summary[
                        "states_assessed"
                    ],
            },
            {
                "Metric":
                    "Low Risk States",

                "Value":
                    summary[
                        "low_risk"
                    ],
            },
            {
                "Metric":
                    "Medium Risk States",

                "Value":
                    summary[
                        "medium_risk"
                    ],
            },
            {
                "Metric":
                    "High Risk States",

                "Value":
                    summary[
                        "high_risk"
                    ],
            },
            {
                "Metric":
                    "Average Confidence (%)",

                "Value":
                    round(
                        summary[
                            "average_confidence"
                        ]
                        * 100,
                        2
                    ),
            },
        ]
    )

    alerts_df = (
        get_latest_alerts()
    )

    with pd.ExcelWriter(
        file_path,
        engine="openpyxl"
    ) as writer:

        summary_df.to_excel(
            writer,
            sheet_name="Summary",
            index=False
        )

        export_df.to_excel(
            writer,
            sheet_name="State Risk Assessment",
            index=False
        )

        priority_export.to_excel(
            writer,
            sheet_name="Priority Risk Areas",
            index=False
        )

        if not alerts_df.empty:

            alert_export = (
                alerts_df[
                    [
                        "state",
                        "alert_level",
                        "message",
                        "status",
                        "forecast_week",
                        "confidence",
                    ]
                ]
                .copy()
            )

            alert_export[
                "confidence"
            ] = (
                alert_export[
                    "confidence"
                ]
                * 100
            ).round(2)

            alert_export.to_excel(
                writer,
                sheet_name="Alerts",
                index=False
            )

    return file_path




def save_report_record(
    user_id,
    report_type,
    file_path
):
    """
    Record generated report in MySQL.
    """

    db = SessionLocal()

    try:

        report = Report(
            user_id=
                user_id,

            report_type=
                report_type,

            file_name=
                str(
                    file_path
                )
        )

        db.add(
            report
        )

        db.commit()

        db.refresh(
            report
        )

        return report

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()



# Retrieve Report History      #   
def get_report_history():
    """
    Retrieve previously generated reports.
    """

    db = SessionLocal()

    try:

        records = (
            db.query(
                Report
            )
            .order_by(
                Report.created_at.desc()
            )
            .all()
        )

        data = [
            {
                "report_id":
                    report.report_id,

                "report_type":
                    report.report_type,

                "file_name":
                    report.file_name,

                "created_at":
                    report.created_at,

                "user_id":
                    report.user_id,
            }

            for report in records
        ]

        return pd.DataFrame(
            data
        )

    finally:

        db.close()