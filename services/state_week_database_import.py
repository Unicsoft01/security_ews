from database.connection import (
    SessionLocal
)

from database.models import (
    Location,
    WeeklyFeature
)

from services.state_week_aggregation import (
    create_state_week_dataset
)


def import_state_week_records():

    df = (
        create_state_week_dataset()
    )

    db = SessionLocal()

    try:

        existing_count = (
            db.query(
                WeeklyFeature
            )
            .count()
        )

        if existing_count > 0:

            print(
                "weekly_features already "
                "contains records."
            )

            print(
                f"Existing records: "
                f"{existing_count:,}"
            )

            return

        locations = (
            db.query(Location)
            .all()
        )

        location_map = {
            item.admin1:
                item.location_id

            for item in locations
        }

        batch = []

        batch_size = 1000

        inserted = 0

        for _, row in (
            df.iterrows()
        ):

            location_id = (
                location_map.get(
                    row["ADMIN1"]
                )
            )

            if location_id is None:

                raise ValueError(
                    "Location not found: "
                    f"{row['ADMIN1']}"
                )

            record = WeeklyFeature(

                location_id=
                    location_id,

                week=
                    row["WEEK"].date(),

                total_events=
                    int(
                        row[
                            "total_events"
                        ]
                    ),

                total_fatalities=
                    int(
                        row[
                            "total_fatalities"
                        ]
                    ),

                battles=
                    int(
                        row[
                            "battles"
                        ]
                    ),

                violence_against_civilians=
                    int(
                        row[
                            "violence_against_civilians"
                        ]
                    ),

                explosions_remote_violence=
                    int(
                        row[
                            "explosions_remote_violence"
                        ]
                    ),

                riots=
                    int(
                        row[
                            "riots"
                        ]
                    ),

                protests=
                    int(
                        row[
                            "protests"
                        ]
                    ),

                strategic_developments=
                    int(
                        row[
                            "strategic_developments"
                        ]
                    ),

                abductions=
                    int(
                        row[
                            "abductions"
                        ]
                    ),

                armed_clashes=
                    int(
                        row[
                            "armed_clashes"
                        ]
                    ),

                attacks=
                    int(
                        row[
                            "attacks"
                        ]
                    )
            )

            batch.append(
                record
            )

            if len(batch) >= (
                batch_size
            ):

                db.bulk_save_objects(
                    batch
                )

                db.commit()

                inserted += (
                    len(batch)
                )

                print(
                    f"Imported "
                    f"{inserted:,}"
                )

                batch = []

        if batch:

            db.bulk_save_objects(
                batch
            )

            db.commit()

            inserted += (
                len(batch)
            )

        print(
            "\nSTATE-WEEK DATABASE "
            "IMPORT COMPLETE"
        )

        print("=" * 60)

        print(
            f"Records imported: "
            f"{inserted:,}"
        )

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()


if __name__ == "__main__":

    import_state_week_records()