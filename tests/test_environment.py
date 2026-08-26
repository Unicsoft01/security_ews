from sqlalchemy import text
from database.connection import engine


def test_database_connection():
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT DATABASE();")
        )

        database_name = result.scalar()

        print(
            f"Connected successfully to database: "
            f"{database_name}"
        )


if __name__ == "__main__":
    test_database_connection()