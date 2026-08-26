from database.connection import (
    SessionLocal
)

from database.models import (
    Dataset,
    IncidentType,
    Location,
    SecurityIncident,
)


def verify_database():

    db = SessionLocal()

    try:

        datasets = (
            db.query(Dataset)
            .count()
        )

        locations = (
            db.query(Location)
            .count()
        )

        incident_types = (
            db.query(IncidentType)
            .count()
        )

        incidents = (
            db.query(
                SecurityIncident
            )
            .count()
        )

        print(
            "\nDATABASE VERIFICATION"
        )

        print("=" * 60)

        print(
            f"Datasets: {datasets:,}"
        )

        print(
            f"Locations: {locations:,}"
        )

        print(
            f"Incident type combinations: "
            f"{incident_types:,}"
        )

        print(
            f"Security incidents: "
            f"{incidents:,}"
        )

    finally:

        db.close()


if __name__ == "__main__":

    verify_database()