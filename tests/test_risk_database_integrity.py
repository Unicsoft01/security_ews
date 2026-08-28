from database.connection import (
    SessionLocal
)

from database.models import (
    Location,
    RiskAssessment,
)


def test_latest_forecast_unique_per_state():

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

        assert (
            latest_forecast
            is not None
        )

        latest_forecast = (
            latest_forecast[0]
        )

        records = (
            db.query(
                RiskAssessment.location_id
            )
            .filter(
                RiskAssessment.forecast_week
                == latest_forecast
            )
            .all()
        )

        location_ids = [
            row[0]
            for row in records
        ]

        assert (
            len(location_ids)
            ==
            len(
                set(location_ids)
            )
        )

    finally:

        db.close()


def test_latest_assessment_locations_valid():

    db = SessionLocal()

    try:

        valid_locations = {
            location.location_id
            for location in
            db.query(Location).all()
        }

        assessments = (
            db.query(
                RiskAssessment
            )
            .all()
        )

        for assessment in assessments:

            assert (
                assessment.location_id
                in valid_locations
            )

    finally:

        db.close()