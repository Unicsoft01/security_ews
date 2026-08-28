from pathlib import Path

from database.connection import (
    SessionLocal
)

from database.models import (
    Alert,
    Location,
    RiskAssessment,
    User,
)

from services.model_service import (
    load_selected_model
)


def check_file(
    path,
    description
):

    exists = Path(
        path
    ).exists()

    status = (
        "PASS"
        if exists
        else "FAIL"
    )

    print(
        f"[{status}] "
        f"{description}: "
        f"{path}"
    )

    return exists


def check_database():

    db = SessionLocal()

    try:

        locations = (
            db.query(
                Location
            )
            .count()
        )

        users = (
            db.query(
                User
            )
            .count()
        )

        assessments = (
            db.query(
                RiskAssessment
            )
            .count()
        )

        alerts = (
            db.query(
                Alert
            )
            .count()
        )

        print(
            "\nDATABASE CHECK"
        )

        print("=" * 60)

        print(
            f"Locations: {locations}"
        )

        print(
            f"Users: {users}"
        )

        print(
            f"Risk assessments: "
            f"{assessments}"
        )

        print(
            f"Alerts: {alerts}"
        )

        if locations != 37:

            raise RuntimeError(
                "Expected 37 Nigerian "
                "states/FCT."
            )

    finally:

        db.close()


def check_model():

    model = (
        load_selected_model()
    )

    print(
        "\nMODEL CHECK"
    )

    print("=" * 60)

    print(
        "Selected model loaded: PASS"
    )

    print(
        f"Pipeline: "
        f"{type(model).__name__}"
    )


def run_health_check():

    print(
        "\nAI SECURITY EWS "
        "DEFENCE HEALTH CHECK"
    )

    print("=" * 60)

    required_files = [
        (
            "models/selected_model.pkl",
            "Selected model"
        ),

        (
            "models/"
            "selected_model_metadata.json",
            "Selected model metadata"
        ),

        (
            "data/processed/"
            "acled_nigeria_state_week_features.csv",
            "Feature dataset"
        ),

        (
            "app.py",
            "Streamlit application"
        ),
    ]

    files_ok = True

    for path, description in (
        required_files
    ):

        result = check_file(
            path,
            description
        )

        files_ok = (
            files_ok
            and result
        )

    if not files_ok:

        raise RuntimeError(
            "One or more required "
            "defence files are missing."
        )

    check_database()

    check_model()

    print(
        "\n"
        "=" * 60
    )

    print(
        "DEFENCE SYSTEM STATUS: READY"
    )


if __name__ == "__main__":

    run_health_check()