"""
Portable setup checker for the AI-Assisted Security Early Warning System.

Run from the project root after installing requirements and importing the
MySQL/MariaDB database:

    python setup_check.py

The script intentionally avoids printing secrets such as DB_PASSWORD.
It exits with code 0 when all critical checks pass and code 1 otherwise.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import os
import socket
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


# -----------------------------------------------------------------------------
# PROJECT PATHS
# -----------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent
ENV_FILE = ROOT / ".env"
REQUIREMENTS_FILE = ROOT / "requirements.txt"
SQL_BACKUP = ROOT / "database" / "setup" / "security_ews.sql"
SELECTED_MODEL = ROOT / "models" / "selected_model.pkl"
SELECTED_METADATA = ROOT / "models" / "selected_model_metadata.json"
FEATURE_DATA = ROOT / "data" / "processed" / "acled_nigeria_state_week_features.csv"
RAW_DATA = ROOT / "data" / "raw" / "Africa_aggregated_data_up_to_week_of-2026-08-08.xlsx"
APP_FILE = ROOT / "app.py"

EXPECTED_DATABASE = "security_ews"
EXPECTED_LOCATION_COUNT = 37
EXPECTED_ROLES = {"Administrator", "Analyst"}
EXPECTED_TABLES = {
    "alerts",
    "audit_logs",
    "datasets",
    "incident_types",
    "locations",
    "model_metrics",
    "model_runs",
    "reports",
    "risk_assessments",
    "roles",
    "security_incidents",
    "users",
    "weekly_features",
}

# Packages needed to start/use the deployed application.
# Keys are import module names; values are friendly package names.
REQUIRED_MODULES = {
    "streamlit": "streamlit",
    "pandas": "pandas",
    "numpy": "numpy",
    "sklearn": "scikit-learn",
    "sqlalchemy": "SQLAlchemy",
    "pymysql": "PyMySQL",
    "dotenv": "python-dotenv",
    "joblib": "joblib",
    "openpyxl": "openpyxl",
    "plotly": "plotly",
    "bcrypt": "bcrypt",
}


# -----------------------------------------------------------------------------
# OUTPUT HELPERS
# -----------------------------------------------------------------------------

PASS = "PASS"
FAIL = "FAIL"
WARN = "WARN"
INFO = "INFO"

results: List[Tuple[str, str]] = []


def line(status: str, message: str, critical: bool = False) -> None:
    """Print and record a setup-check result."""
    print(f"[{status:<4}] {message}")
    if critical and status == FAIL:
        results.append((FAIL, message))
    elif status == WARN:
        results.append((WARN, message))


def section(title: str) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


# -----------------------------------------------------------------------------
# ENVIRONMENT FILE
# -----------------------------------------------------------------------------


def read_env_file(path: Path) -> Dict[str, str]:
    """
    Read a simple .env file without requiring python-dotenv.
    This lets the checker diagnose a missing dependency rather than crashing.
    """
    values: Dict[str, str] = {}

    if not path.exists():
        return values

    try:
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-16")

    for raw_line in text.splitlines():
        raw_line = raw_line.strip()
        if not raw_line or raw_line.startswith("#") or "=" not in raw_line:
            continue

        key, value = raw_line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        values[key] = value

    return values


# -----------------------------------------------------------------------------
# INDIVIDUAL CHECKS
# -----------------------------------------------------------------------------


def check_python() -> None:
    section("1. PYTHON")

    version = sys.version_info
    version_text = f"{version.major}.{version.minor}.{version.micro}"

    if (version.major, version.minor) == (3, 11):
        line(PASS, f"Python {version_text} detected.")
    else:
        line(
            FAIL,
            f"Python {version_text} detected. This project is pinned to Python 3.11.x.",
            critical=True,
        )
        print("       Install Python 3.11 and recreate the virtual environment.")

    in_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    if in_venv:
        line(PASS, f"Virtual environment active: {sys.prefix}")
    else:
        line(
            WARN,
            "No virtual environment appears to be active. Activate .venv before running the app.",
        )



def check_project_files() -> None:
    section("2. REQUIRED PROJECT FILES")

    required = [
        (APP_FILE, "Streamlit application"),
        (REQUIREMENTS_FILE, "Python requirements"),
        (ENV_FILE, "Environment configuration (.env)"),
        (SQL_BACKUP, "Database SQL backup"),
        (SELECTED_MODEL, "Selected machine-learning model"),
        (SELECTED_METADATA, "Selected-model metadata"),
        (FEATURE_DATA, "State-week feature dataset"),
        (RAW_DATA, "Raw ACLED dataset"),
    ]

    for path, description in required:
        if path.exists() and path.is_file():
            size_mb = path.stat().st_size / (1024 * 1024)
            line(PASS, f"{description}: {path.relative_to(ROOT)} ({size_mb:.2f} MB)")
        else:
            line(
                FAIL,
                f"Missing {description}: {path.relative_to(ROOT)}",
                critical=True,
            )



def check_requirements_encoding() -> None:
    section("3. REQUIREMENTS FILE")

    if not REQUIREMENTS_FILE.exists():
        line(FAIL, "requirements.txt is missing.", critical=True)
        return

    raw = REQUIREMENTS_FILE.read_bytes()

    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        line(
            WARN,
            "requirements.txt is UTF-16 encoded. Convert it to UTF-8 before publishing for the most reliable pip installation.",
        )
        encoding = "utf-16"
    else:
        encoding = "utf-8-sig"
        line(PASS, "requirements.txt encoding is suitable for pip (UTF-8/UTF-8-SIG).")

    try:
        content = REQUIREMENTS_FILE.read_text(encoding=encoding)
        package_lines = [
            row.strip()
            for row in content.splitlines()
            if row.strip() and not row.lstrip().startswith("#")
        ]
        line(PASS, f"requirements.txt contains {len(package_lines)} package entries.")
    except Exception as exc:
        line(FAIL, f"Could not read requirements.txt: {exc}", critical=True)



def check_packages() -> None:
    section("4. PYTHON DEPENDENCIES")

    missing: List[str] = []

    for module_name, package_name in REQUIRED_MODULES.items():
        if importlib.util.find_spec(module_name) is None:
            missing.append(package_name)
            line(FAIL, f"Missing package: {package_name}", critical=True)
        else:
            line(PASS, f"Installed: {package_name}")

    if missing:
        print("\n       Install missing dependencies with:")
        print("       python -m pip install -r requirements.txt")



def check_env() -> Dict[str, str]:
    section("5. ENVIRONMENT CONFIGURATION")

    env = read_env_file(ENV_FILE)

    if not ENV_FILE.exists():
        line(
            FAIL,
            ".env was not found. Create it from .env.example before running the system.",
            critical=True,
        )
        return env

    line(PASS, ".env file found.")

    # Empty DB_PASSWORD is allowed because a default XAMPP root account often
    # has no password. The variable itself should still exist.
    required_keys = ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]

    for key in required_keys:
        if key not in env:
            line(FAIL, f"Missing .env variable: {key}", critical=True)
        elif key != "DB_PASSWORD" and env[key] == "":
            line(FAIL, f".env variable is empty: {key}", critical=True)
        else:
            display_value = "<configured>" if key == "DB_PASSWORD" else env[key]
            line(PASS, f"{key} = {display_value}")

    configured_name = env.get("DB_NAME")
    if configured_name and configured_name != EXPECTED_DATABASE:
        line(
            WARN,
            f"DB_NAME is '{configured_name}', while the bundled SQL dump is for '{EXPECTED_DATABASE}'.",
        )

    raw_path = env.get("RAW_DATA_PATH")
    if raw_path:
        path = Path(raw_path)
        if not path.is_absolute():
            path = ROOT / path
        if path.exists():
            line(PASS, f"RAW_DATA_PATH resolves correctly: {path}")
        else:
            line(FAIL, f"RAW_DATA_PATH does not exist: {path}", critical=True)

    return env



def check_feature_dataset_header() -> None:
    section("6. PROCESSED FEATURE DATA")

    if not FEATURE_DATA.exists():
        line(FAIL, "Feature dataset is missing.", critical=True)
        return

    required_columns = {
        "WEEK",
        "ADMIN1",
        "total_events",
        "total_fatalities",
        "violent_events",
        "high_severity_events",
    }

    try:
        with FEATURE_DATA.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            header = next(reader)

        missing = sorted(required_columns - set(header))
        if missing:
            line(
                FAIL,
                "Feature dataset is missing expected columns: " + ", ".join(missing),
                critical=True,
            )
        else:
            line(PASS, "Feature dataset contains the expected core columns.")
            line(INFO, f"Feature dataset has {len(header)} columns.")
    except Exception as exc:
        line(FAIL, f"Could not inspect feature dataset: {exc}", critical=True)



def check_selected_model_metadata() -> None:
    section("7. SELECTED MODEL")

    if not SELECTED_METADATA.exists():
        line(FAIL, "Selected-model metadata is missing.", critical=True)
        return

    try:
        metadata = json.loads(SELECTED_METADATA.read_text(encoding="utf-8"))
        selected_name = metadata.get("selected_model_name") or metadata.get("model") or "Unknown"
        selected_flag = metadata.get("selected_for_deployment")

        line(PASS, f"Metadata loaded. Selected model: {selected_name}")

        if selected_flag is False:
            line(WARN, "Metadata does not mark the model as selected for deployment.")

        metrics = metadata.get("test_metrics", {})
        if metrics:
            macro_f1 = metrics.get("f1_macro")
            high_recall = metrics.get("high_risk_recall")
            if macro_f1 is not None:
                line(INFO, f"Recorded Macro F1: {macro_f1:.4f}")
            if high_recall is not None:
                line(INFO, f"Recorded High-Risk Recall: {high_recall:.4f}")
    except Exception as exc:
        line(FAIL, f"Could not read selected-model metadata: {exc}", critical=True)
        return

    if importlib.util.find_spec("joblib") is None or importlib.util.find_spec("sklearn") is None:
        line(
            WARN,
            "Model load test skipped because joblib/scikit-learn is not installed yet.",
        )
        return

    try:
        import joblib  # imported only after dependency check

        model = joblib.load(SELECTED_MODEL)
        line(PASS, f"selected_model.pkl loaded successfully ({type(model).__name__}).")

        if hasattr(model, "named_steps"):
            components = ", ".join(model.named_steps.keys())
            line(INFO, f"Pipeline components: {components}")
    except Exception as exc:
        line(
            FAIL,
            f"Selected model could not be loaded: {exc}",
            critical=True,
        )
        print("       Check that Python/scikit-learn versions match requirements.txt.")



def check_database(env: Dict[str, str]) -> None:
    section("8. MYSQL / XAMPP DATABASE")

    if importlib.util.find_spec("pymysql") is None:
        line(FAIL, "PyMySQL is not installed; database check cannot run.", critical=True)
        return

    required = ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]
    if any(key not in env for key in required):
        line(FAIL, "Database check skipped because .env is incomplete.", critical=True)
        return

    try:
        port = int(env.get("DB_PORT", "3306"))
    except ValueError:
        line(FAIL, f"DB_PORT is not a valid number: {env.get('DB_PORT')}", critical=True)
        return

    try:
        import pymysql

        connection = pymysql.connect(
            host=env.get("DB_HOST", "127.0.0.1"),
            port=port,
            user=env.get("DB_USER", "root"),
            password=env.get("DB_PASSWORD", ""),
            database=env.get("DB_NAME", EXPECTED_DATABASE),
            charset="utf8mb4",
            connect_timeout=5,
            cursorclass=pymysql.cursors.Cursor,
        )
    except Exception as exc:
        line(
            FAIL,
            f"Could not connect to MySQL/MariaDB: {exc}",
            critical=True,
        )
        print("       Ensure XAMPP MySQL is running and the database has been imported.")
        return

    line(PASS, f"Connected to database '{env.get('DB_NAME')}'.")

    try:
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            actual_tables = {row[0] for row in cursor.fetchall()}

            missing_tables = sorted(EXPECTED_TABLES - actual_tables)
            if missing_tables:
                line(
                    FAIL,
                    "Database is missing tables: " + ", ".join(missing_tables),
                    critical=True,
                )
            else:
                line(PASS, f"All {len(EXPECTED_TABLES)} expected tables are present.")

            # Locations: 36 states + FCT
            if "locations" in actual_tables:
                cursor.execute("SELECT COUNT(*) FROM locations")
                location_count = int(cursor.fetchone()[0])
                if location_count == EXPECTED_LOCATION_COUNT:
                    line(PASS, "Locations table contains 37 states/FCT.")
                else:
                    line(
                        FAIL,
                        f"Locations table contains {location_count} rows; expected 37.",
                        critical=True,
                    )

            # Required application roles
            if "roles" in actual_tables:
                cursor.execute("SELECT role_name FROM roles")
                roles = {row[0] for row in cursor.fetchall()}
                missing_roles = EXPECTED_ROLES - roles
                if not missing_roles:
                    line(PASS, "Administrator and Analyst roles are present.")
                else:
                    line(
                        FAIL,
                        "Missing application roles: " + ", ".join(sorted(missing_roles)),
                        critical=True,
                    )

            # At least one active user for login
            if "users" in actual_tables:
                cursor.execute("SELECT COUNT(*) FROM users WHERE status = 1")
                active_users = int(cursor.fetchone()[0])
                if active_users > 0:
                    line(PASS, f"Active user accounts available: {active_users}")
                else:
                    line(
                        FAIL,
                        "No active user account is available for login.",
                        critical=True,
                    )

            # Model run selected for deployment
            if "model_runs" in actual_tables:
                cursor.execute("SELECT COUNT(*) FROM model_runs WHERE selected = 1")
                selected_runs = int(cursor.fetchone()[0])
                if selected_runs >= 1:
                    line(PASS, f"Selected model run found in database: {selected_runs}")
                else:
                    line(
                        FAIL,
                        "No selected model_run exists in the database.",
                        critical=True,
                    )

            # Weekly features should be populated for prediction/dashboard work.
            if "weekly_features" in actual_tables:
                cursor.execute("SELECT COUNT(*) FROM weekly_features")
                feature_rows = int(cursor.fetchone()[0])
                if feature_rows > 0:
                    line(PASS, f"Weekly feature rows available: {feature_rows:,}")
                else:
                    line(FAIL, "weekly_features table is empty.", critical=True)

            # Latest stored risk assessment should normally cover all 37 states/FCT.
            if "risk_assessments" in actual_tables:
                cursor.execute("SELECT MAX(forecast_week) FROM risk_assessments")
                latest_forecast = cursor.fetchone()[0]

                if latest_forecast is None:
                    line(WARN, "No stored risk assessments exist yet.")
                else:
                    cursor.execute(
                        "SELECT COUNT(DISTINCT location_id) "
                        "FROM risk_assessments WHERE forecast_week = %s",
                        (latest_forecast,),
                    )
                    latest_count = int(cursor.fetchone()[0])

                    if latest_count == EXPECTED_LOCATION_COUNT:
                        line(
                            PASS,
                            f"Latest forecast ({latest_forecast}) contains 37 state/FCT assessments.",
                        )
                    else:
                        line(
                            WARN,
                            f"Latest forecast ({latest_forecast}) contains {latest_count} distinct locations, not 37.",
                        )

    except Exception as exc:
        line(FAIL, f"Database integrity check failed: {exc}", critical=True)
    finally:
        connection.close()



def check_streamlit_port() -> None:
    section("9. STREAMLIT PORT")

    host = "127.0.0.1"
    port = 8501

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        in_use = sock.connect_ex((host, port)) == 0
    finally:
        sock.close()

    if in_use:
        line(
            WARN,
            "Port 8501 is already in use. Streamlit may already be running, or another app is using the port.",
        )
    else:
        line(PASS, "Port 8501 is available for Streamlit.")



def final_summary() -> int:
    section("FINAL RESULT")

    failures = [message for status, message in results if status == FAIL]
    warnings = [message for status, message in results if status == WARN]

    if failures:
        print("SYSTEM STATUS: NOT READY")
        print(f"Critical failures: {len(failures)}")
        print(f"Warnings: {len(warnings)}")
        print("\nCorrect every FAIL item before starting the application.")
        return 1

    print("SYSTEM STATUS: READY")
    print("All critical setup checks passed.")

    if warnings:
        print(f"Warnings: {len(warnings)}")
        print("The application may still run, but review the WARN items above.")
    else:
        print("Warnings: 0")

    print("\nStart the system with:")
    print("    streamlit run app.py")
    print("\nThen open:")
    print("    http://localhost:8501")
    return 0


# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------


def main() -> int:
    print("\nAI-ASSISTED SECURITY EARLY WARNING SYSTEM")
    print("PORTABLE INSTALLATION / SETUP CHECK")
    print(f"Project root: {ROOT}")

    check_python()
    check_project_files()
    check_requirements_encoding()
    check_packages()
    env = check_env()
    check_feature_dataset_header()
    check_selected_model_metadata()
    check_database(env)
    check_streamlit_port()

    return final_summary()


if __name__ == "__main__":
    raise SystemExit(main())
