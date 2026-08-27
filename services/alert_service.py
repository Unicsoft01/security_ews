from database.connection import (
    SessionLocal
)

from database.models import (
    Alert,
    Location,
    RiskAssessment,
)

import pandas as pd


def build_alert_message(
    state,
    risk_level,
    forecast_week,
    confidence
):
    """
    Generate an early-warning message
    from a stored risk assessment.
    """

    confidence_percent = (
        confidence * 100
    )

    if risk_level == "High":

        return (
            f"HIGH-RISK WARNING: {state} is "
            f"classified as High security risk "
            f"for the forecast week "
            f"{forecast_week} with model "
            f"confidence of "
            f"{confidence_percent:.2f}%. "
            f"Priority monitoring and security "
            f"review are recommended."
        )

    if risk_level == "Medium":

        return (
            f"MONITORING WARNING: {state} is "
            f"classified as Medium security risk "
            f"for the forecast week "
            f"{forecast_week} with model "
            f"confidence of "
            f"{confidence_percent:.2f}%. "
            f"Enhanced monitoring is recommended."
        )

    return None



# Generate alert from latest asssessment
def generate_latest_alerts():
    """
    Generate warning alerts for the latest
    High and Medium risk assessments.
    """

    db = SessionLocal()

    try:

        latest_forecast = (
            db.query(
                RiskAssessment.forecast_week
            )
            .order_by(
                RiskAssessment.forecast_week.desc()
            )
            .first()
        )

        if latest_forecast is None:

            return {
                "created": 0,
                "skipped": 0,
                "message":
                    "No risk assessments available."
            }

        latest_forecast = (
            latest_forecast[0]
        )

        assessments = (
            db.query(
                RiskAssessment,
                Location
            )
            .join(
                Location,
                RiskAssessment.location_id
                == Location.location_id
            )
            .filter(
                RiskAssessment.forecast_week
                == latest_forecast,

                RiskAssessment.risk_level.in_(
                    [
                        "High",
                        "Medium"
                    ]
                )
            )
            .all()
        )

        created = 0
        skipped = 0

        for assessment, location in (
            assessments
        ):

            # ----------------------------------
            # PREVENT DUPLICATE ALERT
            # ----------------------------------

            existing = (
                db.query(
                    Alert
                )
                .filter(
                    Alert.assessment_id
                    == assessment.assessment_id
                )
                .first()
            )

            if existing:

                skipped += 1
                continue

            message = (
                build_alert_message(
                    state=
                        location.admin1,

                    risk_level=
                        assessment.risk_level,

                    forecast_week=
                        assessment.forecast_week,

                    confidence=
                        assessment.risk_probability
                )
            )

            alert = Alert(

                assessment_id=
                    assessment.assessment_id,

                alert_level=
                    assessment.risk_level,

                alert_message=
                    message,

                status="active"
            )

            db.add(
                alert
            )

            created += 1

        db.commit()

        return {
            "created":
                created,

            "skipped":
                skipped,

            "forecast_week":
                latest_forecast
        }

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()




if __name__ == "__main__":

    result = (
        generate_latest_alerts()
    )

    print(
        "\nALERT GENERATION COMPLETE"
    )

    print("=" * 60)

    print(
        f"Created: "
        f"{result.get('created', 0)}"
    )

    print(
        f"Skipped: "
        f"{result.get('skipped', 0)}"
    )

    if (
        "forecast_week"
        in result
    ):

        print(
            f"Forecast Week: "
            f"{result['forecast_week']}"
        )



def get_latest_alerts():
    """
    Retrieve alerts associated with
    the latest forecast week.
    """

    db = SessionLocal()

    try:

        latest_forecast = (
            db.query(
                RiskAssessment.forecast_week
            )
            .order_by(
                RiskAssessment.forecast_week.desc()
            )
            .first()
        )

        if latest_forecast is None:

            return pd.DataFrame()

        latest_forecast = (
            latest_forecast[0]
        )

        records = (
            db.query(
                Alert.alert_id,
                Location.admin1,
                Alert.alert_level,
                Alert.alert_message,
                Alert.status,
                RiskAssessment.assessment_week,
                RiskAssessment.forecast_week,
                RiskAssessment.risk_probability,
                Alert.created_at,
            )
            .join(
                RiskAssessment,
                Alert.assessment_id
                == RiskAssessment.assessment_id
            )
            .join(
                Location,
                RiskAssessment.location_id
                == Location.location_id
            )
            .filter(
                RiskAssessment.forecast_week
                == latest_forecast
            )
            .all()
        )

        data = [
            {
                "alert_id":
                    row[0],

                "state":
                    row[1],

                "alert_level":
                    row[2],

                "message":
                    row[3],

                "status":
                    row[4],

                "assessment_week":
                    row[5],

                "forecast_week":
                    row[6],

                "confidence":
                    row[7],

                "created_at":
                    row[8],
            }

            for row in records
        ]

        return pd.DataFrame(
            data
        )

    finally:

        db.close()




def update_alert_status(
    alert_id,
    new_status
):
    """
    Update the status of an alert.
    """

    allowed_statuses = {
        "active",
        "reviewed",
        "resolved",
    }

    if new_status not in (
        allowed_statuses
    ):

        raise ValueError(
            "Invalid alert status."
        )

    db = SessionLocal()

    try:

        alert = (
            db.query(
                Alert
            )
            .filter(
                Alert.alert_id
                == alert_id
            )
            .first()
        )

        if alert is None:

            return False

        alert.status = (
            new_status
        )

        db.commit()

        return True

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()        