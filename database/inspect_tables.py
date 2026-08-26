from sqlalchemy import inspect

from database.connection import engine


def inspect_database():

    inspector = inspect(engine)

    tables = inspector.get_table_names()

    print(
        "\nDATABASE TABLES"
    )

    print(
        "=" * 50
    )

    for table in tables:
        print(table)

    print(
        f"\nTotal tables: {len(tables)}"
    )


if __name__ == "__main__":
    inspect_database()