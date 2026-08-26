import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.getenv(
    "APP_NAME",
    "AI-Assisted Security Early Warning System"
)

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "security_ews")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

RAW_DATA_PATH = os.getenv(
    "RAW_DATA_PATH",
    "data/raw/Africa_aggregated_data_up_to_week_of-2026-08-08.xlsx"
)

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)