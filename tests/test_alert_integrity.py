from database.connection import (
    SessionLocal
)

from database.models import (
    Alert,
    RiskAssessment,
)


def test_alert_has_valid_assessment():

    db = SessionLocal()

    try:

        assessment_ids = {
            item.assessment_id
            for item in
            db.query(
                RiskAssessment
            )
            .all()
        }

        alerts = (
            db.query(
                Alert
            )
            .all()
        )

        for alert in alerts:

            assert (
                alert.assessment_id
                in assessment_ids
            )

    finally:

        db.close()


def test_alert_levels_valid():

    db = SessionLocal()

    try:

        alerts = (
            db.query(
                Alert
            )
            .all()
        )

        for alert in alerts:

            assert (
                alert.alert_level
                in {
                    "High",
                    "Medium",
                }
            )

    finally:

        db.close()


def test_alert_status_valid():

    db = SessionLocal()

    try:

        alerts = (
            db.query(
                Alert
            )
            .all()
        )

        valid_statuses = {
            "active",
            "reviewed",
            "resolved",
        }

        for alert in alerts:

            assert (
                alert.status
                in valid_statuses
            )

    finally:

        db.close()
        