from pathlib import Path

import pandas as pd

from database.connection import (
    SessionLocal
)

from database.models import (
    Dataset,
    SecurityIncident
)

from database.repositories import (
    get_dataset_by_filename,
    get_or_create_incident_type,
    get_or_create_location,
)

from services.preprocessing import (
    preprocess_nigeria_dataset,
    save_clean_dataset,
)


SOURCE_FILE_NAME = (
    "Africa_aggregated_data_up_to_week_of-2026-08-08.xlsx"
)


def none_if_nan(value):

    if pd.isna(value):
        return None

    return value


def create_dataset_record(
    db,
    df
):

    existing = get_dataset_by_filename(
        db,
        SOURCE_FILE_NAME
    )

    if existing:

        return existing, False

    dataset = Dataset(
        file_name=
            SOURCE_FILE_NAME,

        source="ACLED",

        record_count=
            len(df),

        start_date=
            df["WEEK"].min().date(),

        end_date=
            df["WEEK"].max().date(),

        status="cleaned"
    )

    db.add(dataset)

    db.flush()

    return dataset, True


def import_clean_incidents():

    clean_df, report = (
        preprocess_nigeria_dataset()
    )

    save_clean_dataset(
        clean_df
    )

    db = SessionLocal()

    try:

        dataset, created = (
            create_dataset_record(
                db,
                clean_df
            )
        )

        # Prevent accidental duplicate import
        existing_incidents = (
            db.query(
                SecurityIncident
            )
            .filter(
                SecurityIncident.dataset_id
                == dataset.dataset_id
            )
            .count()
        )

        if existing_incidents > 0:

            print(
                "\nThis dataset has already "
                "been imported."
            )

            print(
                f"Existing incident records: "
                f"{existing_incidents:,}"
            )

            return

        # --------------------------------
        # CREATE LOCATION LOOKUP
        # --------------------------------

        location_map = {}

        location_rows = (
            clean_df[
                [
                    "ADMIN1",
                    "CENTROID_LATITUDE",
                    "CENTROID_LONGITUDE"
                ]
            ]
            .drop_duplicates(
                subset=["ADMIN1"]
            )
        )

        for _, row in (
            location_rows.iterrows()
        ):

            location = (
                get_or_create_location(
                    db=db,

                    admin1=
                        row["ADMIN1"],

                    latitude=
                        none_if_nan(
                            row[
                                "CENTROID_LATITUDE"
                            ]
                        ),

                    longitude=
                        none_if_nan(
                            row[
                                "CENTROID_LONGITUDE"
                            ]
                        )
                )
            )

            location_map[
                row["ADMIN1"]
            ] = (
                location.location_id
            )

        # --------------------------------
        # CREATE INCIDENT TYPE LOOKUP
        # --------------------------------

        incident_type_map = {}

        type_rows = (
            clean_df[
                [
                    "EVENT_TYPE",
                    "SUB_EVENT_TYPE"
                ]
            ]
            .drop_duplicates()
        )

        for _, row in (
            type_rows.iterrows()
        ):

            incident_type = (
                get_or_create_incident_type(
                    db=db,

                    event_type=
                        row["EVENT_TYPE"],

                    sub_event_type=
                        row[
                            "SUB_EVENT_TYPE"
                        ]
                )
            )

            key = (
                row["EVENT_TYPE"],
                row["SUB_EVENT_TYPE"]
            )

            incident_type_map[
                key
            ] = (
                incident_type
                .incident_type_id
            )

        db.commit()

        # --------------------------------
        # BUILD INCIDENT OBJECTS
        # --------------------------------

        batch = []

        batch_size = 1000

        inserted = 0

        for _, row in (
            clean_df.iterrows()
        ):

            type_key = (
                row["EVENT_TYPE"],
                row["SUB_EVENT_TYPE"]
            )

            incident = SecurityIncident(

                dataset_id=
                    dataset.dataset_id,

                location_id=
                    location_map[
                        row["ADMIN1"]
                    ],

                incident_type_id=
                    incident_type_map[
                        type_key
                    ],

                week=
                    row["WEEK"].date(),

                events=
                    int(
                        row["EVENTS"]
                    ),

                fatalities=
                    int(
                        row["FATALITIES"]
                    ),

                population_exposure=
                    none_if_nan(
                        row[
                            "POPULATION_EXPOSURE"
                        ]
                    ),

                disorder_type=
                    none_if_nan(
                        row[
                            "DISORDER_TYPE"
                        ]
                    ),

                acled_admin_id=
                    none_if_nan(
                        row["ID"]
                    )
            )

            batch.append(
                incident
            )

            if len(batch) >= batch_size:

                db.bulk_save_objects(
                    batch
                )

                db.commit()

                inserted += len(
                    batch
                )

                print(
                    f"Imported: "
                    f"{inserted:,}"
                )

                batch = []

        # Remaining records
        if batch:

            db.bulk_save_objects(
                batch
            )

            db.commit()

            inserted += len(
                batch
            )

        dataset.status = (
            "imported"
        )

        dataset.record_count = (
            inserted
        )

        db.commit()

        print(
            "\nDATABASE IMPORT COMPLETE"
        )

        print(
            "=" * 60
        )

        print(
            f"Dataset ID: "
            f"{dataset.dataset_id}"
        )

        print(
            f"Clean incidents imported: "
            f"{inserted:,}"
        )

        print(
            f"Locations stored: "
            f"{len(location_map)}"
        )

        print(
            f"Incident type combinations: "
            f"{len(incident_type_map)}"
        )

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()


if __name__ == "__main__":

    import_clean_incidents()