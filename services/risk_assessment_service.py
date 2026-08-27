import pandas as pd
from database.connection import (
    SessionLocal
)

from database.models import (
    Location,
    ModelRun,
    RiskAssessment,
)

from services.prediction import (
    generate_latest_predictions
)


def get_selected_model_run(db):
    """
    Return the model_run marked as selected.
    """

    model_run = (
        db.query(
            ModelRun
        )
        .filter(
            ModelRun.selected
            == True
        )
        .order_by(
            ModelRun.model_run_id.desc()
        )
        .first()
    )

    return model_run


def save_latest_risk_assessments():
    """
    Generate and store latest state-level
    risk predictions.
    """

    results = (
        generate_latest_predictions()
    )

    db = SessionLocal()

    try:

        model_run = (
            get_selected_model_run(
                db
            )
        )

        if model_run is None:

            raise RuntimeError(
                "No selected model_run was found "
                "in the database. Store Phase 10 "
                "model results first."
            )

        locations = (
            db.query(
                Location
            )
            .all()
        )

        location_map = {
            location.admin1:
                location.location_id

            for location
            in locations
        }

        inserted = 0
        skipped = 0

        for _, row in (
            results.iterrows()
        ):

            state = (
                row["ADMIN1"]
            )

            location_id = (
                location_map.get(
                    state
                )
            )

            if location_id is None:

                raise ValueError(
                    f"Location not found: "
                    f"{state}"
                )

            assessment_week = (
                row[
                    "assessment_week"
                ].date()
            )

            forecast_week = (
                row[
                    "forecast_week"
                ].date()
            )

            # Prevent duplicate predictions
            existing = (
                db.query(
                    RiskAssessment
                )
                .filter(
                    RiskAssessment.location_id
                    == location_id,

                    RiskAssessment.model_run_id
                    == model_run.model_run_id,

                    RiskAssessment.assessment_week
                    == assessment_week,

                    RiskAssessment.forecast_week
                    == forecast_week,
                )
                .first()
            )

            if existing:

                skipped += 1
                continue

            assessment = (
                RiskAssessment(

                    location_id=
                        location_id,

                    model_run_id=
                        model_run.model_run_id,

                    assessment_week=
                        assessment_week,

                    forecast_week=
                        forecast_week,

                    risk_level=
                        row[
                            "predicted_risk"
                        ],

                    risk_probability=
                        float(
                            row[
                                "prediction_confidence"
                            ]
                        )
                )
            )

            db.add(
                assessment
            )

            inserted += 1

        db.commit()

        print(
            "\nRISK ASSESSMENT STORAGE COMPLETE"
        )

        print("=" * 60)

        print(
            f"Inserted: {inserted}"
        )

        print(
            f"Skipped existing: {skipped}"
        )

        return {
            "inserted":
                inserted,

            "skipped":
                skipped
        }

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()


if __name__ == "__main__":

    save_latest_risk_assessments()


def get_latest_risk_assessments():
    """
    Retrieve the most recent stored risk
    assessments from MySQL.
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
                Location.admin1,
                Location.latitude,
                Location.longitude,
                RiskAssessment.assessment_week,
                RiskAssessment.forecast_week,
                RiskAssessment.risk_level,
                RiskAssessment.risk_probability,
            )
            .join(
                RiskAssessment,
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
                "state":
                    record[0],

                "latitude":
                    record[1],

                "longitude":
                    record[2],

                "assessment_week":
                    record[3],

                "forecast_week":
                    record[4],

                "risk_level":
                    record[5],

                "confidence":
                    record[6],
            }

            for record in records
        ]

        return pd.DataFrame(
            data
        )

    finally:

        db.close()