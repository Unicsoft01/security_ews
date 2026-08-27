from sqlalchemy import func

from database.connection import (
    SessionLocal
)

from database.models import (
    Alert,
    Location,
    SecurityIncident,
)


def get_dashboard_summary():
    """
    Retrieve key dashboard statistics.
    """

    db = SessionLocal()

    try:

        total_records = (
            db.query(
                func.count(
                    SecurityIncident.incident_id
                )
            )
            .scalar()
            or 0
        )

        total_events = (
            db.query(
                func.sum(
                    SecurityIncident.events
                )
            )
            .scalar()
            or 0
        )

        total_fatalities = (
            db.query(
                func.sum(
                    SecurityIncident.fatalities
                )
            )
            .scalar()
            or 0
        )

        locations = (
            db.query(
                func.count(
                    Location.location_id
                )
            )
            .scalar()
            or 0
        )

        active_alerts = (
            db.query(
                func.count(
                    Alert.alert_id
                )
            )
            .filter(
                Alert.status
                == "active"
            )
            .scalar()
            or 0
        )

        return {
            "incident_records":
                int(
                    total_records
                ),

            "represented_events":
                int(
                    total_events
                ),

            "fatalities":
                int(
                    total_fatalities
                ),

            "locations":
                int(
                    locations
                ),

            "active_alerts":
                int(
                    active_alerts
                ),
        }

    finally:

        db.close()


# Create Dashboard Data Functions
def get_events_by_state():
    """
    Return represented event totals by state.
    """

    db = SessionLocal()

    try:

        results = (
            db.query(
                Location.admin1,
                func.sum(
                    SecurityIncident.events
                )
            )
            .join(
                SecurityIncident,
                SecurityIncident.location_id
                == Location.location_id
            )
            .group_by(
                Location.admin1
            )
            .all()
        )

        return [
            {
                "state":
                    state,

                "events":
                    int(
                        events or 0
                    ),
            }

            for state, events
            in results
        ]

    finally:

        db.close()


def get_fatalities_by_state():
    """
    Return fatality totals by state.
    """

    db = SessionLocal()

    try:

        results = (
            db.query(
                Location.admin1,
                func.sum(
                    SecurityIncident.fatalities
                )
            )
            .join(
                SecurityIncident,
                SecurityIncident.location_id
                == Location.location_id
            )
            .group_by(
                Location.admin1
            )
            .all()
        )

        return [
            {
                "state":
                    state,

                "fatalities":
                    int(
                        fatalities or 0
                    ),
            }

            for state, fatalities
            in results
        ]

    finally:

        db.close()



# Create weekly trend query
def get_weekly_event_trend():
    """
    Return represented events and fatalities
    grouped by week.
    """

    db = SessionLocal()

    try:

        results = (
            db.query(
                SecurityIncident.week,
                func.sum(
                    SecurityIncident.events
                ),
                func.sum(
                    SecurityIncident.fatalities
                ),
            )
            .group_by(
                SecurityIncident.week
            )
            .order_by(
                SecurityIncident.week
            )
            .all()
        )

        return [
            {
                "week":
                    week,

                "events":
                    int(
                        events or 0
                    ),

                "fatalities":
                    int(
                        fatalities or 0
                    ),
            }

            for (
                week,
                events,
                fatalities
            )
            in results
        ]

    finally:

        db.close()



# improving the dashboard
def get_dataset_date_range():

    db = SessionLocal()

    try:

        earliest = (
            db.query(
                func.min(
                    SecurityIncident.week
                )
            )
            .scalar()
        )

        latest = (
            db.query(
                func.max(
                    SecurityIncident.week
                )
            )
            .scalar()
        )

        return (
            earliest,
            latest
        )

    finally:

        db.close()