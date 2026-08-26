from database.connection import (
    SessionLocal
)

from database.models import (
    Location,
    SecurityIncident,
)


def test_locations_imported():

    db = SessionLocal()

    try:

        count = (
            db.query(Location)
            .count()
        )

        assert count == 37

    finally:

        db.close()


def test_incidents_imported():

    db = SessionLocal()

    try:

        count = (
            db.query(
                SecurityIncident
            )
            .count()
        )

        assert count > 0

    finally:

        db.close()


def test_no_negative_events_in_db():

    db = SessionLocal()

    try:

        count = (
            db.query(
                SecurityIncident
            )
            .filter(
                SecurityIncident.events
                < 0
            )
            .count()
        )

        assert count == 0

    finally:

        db.close()


def test_no_negative_fatalities_in_db():

    db = SessionLocal()

    try:

        count = (
            db.query(
                SecurityIncident
            )
            .filter(
                SecurityIncident.fatalities
                < 0
            )
            .count()
        )

        assert count == 0

    finally:

        db.close()