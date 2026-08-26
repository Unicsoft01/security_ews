from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.settings import DATABASE_URL
from sqlalchemy import text


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():
    """
    Provide a database session.
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

# 
def check_database_connection():

    try:

        with engine.connect() as connection:

            result = connection.execute(
                text(
                    "SELECT DATABASE();"
                )
            )

            database_name = (
                result.scalar()
            )

            return {
                "connected": True,
                "database":
                    database_name,
                "error": None
            }

    except Exception as exc:

        return {
            "connected": False,
            "database": None,
            "error": str(exc)
        }