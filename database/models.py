from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text
)

from sqlalchemy.orm import (
    declarative_base,
    relationship
)


Base = declarative_base()


class Role(Base):
    __tablename__ = "roles"

    role_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    role_name = Column(
        String(50),
        unique=True,
        nullable=False
    )

    description = Column(
        String(255),
        nullable=True
    )

    users = relationship(
        "User",
        back_populates="role"
    )


class User(Base):
    __tablename__ = "users"

    user_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    role_id = Column(
        Integer,
        ForeignKey("roles.role_id"),
        nullable=False
    )

    full_name = Column(
        String(150),
        nullable=False
    )

    email = Column(
        String(150),
        unique=True,
        nullable=False
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    status = Column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    role = relationship(
        "Role",
        back_populates="users"
    )


class Dataset(Base):
    __tablename__ = "datasets"

    dataset_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    file_name = Column(
        String(255),
        nullable=False
    )

    source = Column(
        String(100),
        default="ACLED"
    )

    date_loaded = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    record_count = Column(
        Integer,
        nullable=True
    )

    start_date = Column(
        Date,
        nullable=True
    )

    end_date = Column(
        Date,
        nullable=True
    )

    status = Column(
        String(50),
        default="loaded"
    )


class Location(Base):
    __tablename__ = "locations"

    location_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    admin1 = Column(
        String(100),
        unique=True,
        nullable=False
    )

    latitude = Column(
        Float,
        nullable=True
    )

    longitude = Column(
        Float,
        nullable=True
    )


class IncidentType(Base):
    __tablename__ = "incident_types"

    incident_type_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    event_type = Column(
        String(150),
        nullable=False
    )

    sub_event_type = Column(
        String(150),
        nullable=False
    )


class SecurityIncident(Base):
    __tablename__ = "security_incidents"

    incident_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    dataset_id = Column(
        Integer,
        ForeignKey("datasets.dataset_id"),
        nullable=False
    )

    location_id = Column(
        Integer,
        ForeignKey("locations.location_id"),
        nullable=False
    )

    incident_type_id = Column(
        Integer,
        ForeignKey("incident_types.incident_type_id"),
        nullable=False
    )

    week = Column(
        Date,
        nullable=False
    )

    events = Column(
        Integer,
        default=0,
        nullable=False
    )

    fatalities = Column(
        Integer,
        default=0,
        nullable=False
    )

    population_exposure = Column(
        Float,
        nullable=True
    )

    disorder_type = Column(
        String(150),
        nullable=True
    )

    acled_admin_id = Column(
        String(100),
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )


class WeeklyFeature(Base):
    __tablename__ = "weekly_features"

    feature_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    location_id = Column(
        Integer,
        ForeignKey("locations.location_id"),
        nullable=False
    )

    week = Column(
        Date,
        nullable=False
    )

    total_events = Column(
        Integer,
        default=0
    )

    total_fatalities = Column(
        Integer,
        default=0
    )

    battles = Column(
        Integer,
        default=0
    )

    violence_against_civilians = Column(
        Integer,
        default=0
    )

    explosions_remote_violence = Column(
        Integer,
        default=0
    )

    riots = Column(
        Integer,
        default=0
    )

    protests = Column(
        Integer,
        default=0
    )

    strategic_developments = Column(
        Integer,
        default=0
    )

    abductions = Column(
        Integer,
        default=0
    )

    armed_clashes = Column(
        Integer,
        default=0
    )

    attacks = Column(
        Integer,
        default=0
    )

    events_lag_1 = Column(
        Float,
        nullable=True
    )

    events_lag_2 = Column(
        Float,
        nullable=True
    )

    events_lag_3 = Column(
        Float,
        nullable=True
    )

    events_lag_4 = Column(
        Float,
        nullable=True
    )

    fatalities_lag_1 = Column(
        Float,
        nullable=True
    )

    fatalities_lag_2 = Column(
        Float,
        nullable=True
    )

    events_4wk_mean = Column(
        Float,
        nullable=True
    )

    fatalities_4wk_mean = Column(
        Float,
        nullable=True
    )

    event_change_1wk = Column(
        Float,
        nullable=True
    )

    fatality_change_1wk = Column(
        Float,
        nullable=True
    )

    target_risk = Column(
        String(20),
        nullable=True
    )


class ModelRun(Base):
    __tablename__ = "model_runs"

    model_run_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    model_name = Column(
        String(100),
        nullable=False
    )

    training_start = Column(
        Date,
        nullable=True
    )

    training_end = Column(
        Date,
        nullable=True
    )

    testing_start = Column(
        Date,
        nullable=True
    )

    testing_end = Column(
        Date,
        nullable=True
    )

    trained_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    model_file = Column(
        String(255),
        nullable=True
    )

    selected = Column(
        Boolean,
        default=False
    )


class ModelMetric(Base):
    __tablename__ = "model_metrics"

    metric_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    model_run_id = Column(
        Integer,
        ForeignKey("model_runs.model_run_id"),
        nullable=False
    )

    accuracy = Column(
        Float,
        nullable=True
    )

    precision = Column(
        Float,
        nullable=True
    )

    recall = Column(
        Float,
        nullable=True
    )

    f1_score = Column(
        Float,
        nullable=True
    )

    high_risk_recall = Column(
        Float,
        nullable=True
    )


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    assessment_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    location_id = Column(
        Integer,
        ForeignKey("locations.location_id"),
        nullable=False
    )

    model_run_id = Column(
        Integer,
        ForeignKey("model_runs.model_run_id"),
        nullable=False
    )

    assessment_week = Column(
        Date,
        nullable=False
    )

    forecast_week = Column(
        Date,
        nullable=False
    )

    risk_level = Column(
        String(20),
        nullable=False
    )

    risk_probability = Column(
        Float,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )


class Alert(Base):
    __tablename__ = "alerts"

    alert_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    assessment_id = Column(
        Integer,
        ForeignKey("risk_assessments.assessment_id"),
        nullable=False
    )

    alert_level = Column(
        String(20),
        nullable=False
    )

    alert_message = Column(
        Text,
        nullable=False
    )

    status = Column(
        String(50),
        default="active"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )


class Report(Base):
    __tablename__ = "reports"

    report_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False
    )

    report_type = Column(
        String(100),
        nullable=False
    )

    file_name = Column(
        String(255),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    log_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=True
    )

    activity = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )