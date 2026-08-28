from pathlib import Path

from database.connection import (
    SessionLocal
)

from database.models import (
    Alert,
    Location,
    RiskAssessment,
    Role,
    User,
)

from services.model_service import (
    load_selected_model
)

from services.risk_assessment_service import (
    get_latest_risk_assessments
)


MODEL_PATH = Path(
    "models/selected_model.pkl"
)


def test_selected_model_file_exists():

    assert MODEL_PATH.exists()


def test_selected_model_loads():

    model = load_selected_model()

    assert model is not None


def test_37_locations_exist():

    db = SessionLocal()

    try:

        count = (
            db.query(
                Location
            )
            .count()
        )

        assert count == 37

    finally:

        db.close()


def test_system_roles_exist():

    db = SessionLocal()

    try:

        roles = {
            role.role_name
            for role in
            db.query(Role).all()
        }

        assert (
            "Administrator"
            in roles
        )

        assert (
            "Analyst"
            in roles
        )

    finally:

        db.close()


def test_active_user_exists():

    db = SessionLocal()

    try:

        count = (
            db.query(User)
            .filter(
                User.status
                == True
            )
            .count()
        )

        assert count > 0

    finally:

        db.close()


def test_latest_risk_assessment_has_37_states():

    df = (
        get_latest_risk_assessments()
    )

    assert not df.empty

    assert len(df) == 37

    assert (
        df[
            "state"
        ]
        .nunique()
        == 37
    )


def test_risk_probabilities_valid():

    df = (
        get_latest_risk_assessments()
    )

    assert (
        df[
            "confidence"
        ]
        .between(
            0,
            1
        )
        .all()
    )


def test_risk_classes_valid():

    df = (
        get_latest_risk_assessments()
    )

    valid_classes = {
        "Low",
        "Medium",
        "High",
    }

    assert set(
        df[
            "risk_level"
        ]
    ).issubset(
        valid_classes
    )