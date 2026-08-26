from datetime import date

from database.connection import SessionLocal
from database.models import Dataset
from database.repositories import (
    create_dataset_record,
    get_dataset_by_id
)


def test_dataset_crud():

    db = SessionLocal()

    try:

        dataset = (
            create_dataset_record(
                db=db,
                file_name=
                    "test_acled.xlsx",
                source="ACLED",
                record_count=32197,
                start_date=
                    date(1997, 1, 4),
                end_date=
                    date(2026, 8, 8)
            )
        )

        assert dataset.dataset_id

        retrieved = (
            get_dataset_by_id(
                db,
                dataset.dataset_id
            )
        )

        assert retrieved is not None

        assert (
            retrieved.source
            == "ACLED"
        )

        db.delete(retrieved)

        db.commit()

    finally:

        db.close()