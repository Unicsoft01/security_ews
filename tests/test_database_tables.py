from sqlalchemy import inspect

from database.connection import engine


EXPECTED_TABLES = {
    "roles",
    "users",
    "datasets",
    "locations",
    "incident_types",
    "security_incidents",
    "weekly_features",
    "model_runs",
    "model_metrics",
    "risk_assessments",
    "alerts",
    "reports",
    "audit_logs",
}


def test_database_tables_exist():

    inspector = inspect(
        engine
    )

    tables = set(
        inspector.get_table_names()
    )

    missing = (
        EXPECTED_TABLES
        - tables
    )

    assert not missing, (
        f"Missing tables: {missing}"
    )