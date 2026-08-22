import os
from datetime import date
from dotenv import load_dotenv

load_dotenv()

HISTORY_START_DATE = date.fromisoformat(os.getenv("HISTORY_START_DATE", "2025-01-01"))
HISTORY_END_DATE = date.fromisoformat(os.getenv("HISTORY_END_DATE", "2026-08-21"))
RANDOM_SEED = int(os.getenv("GENERATOR_RANDOM_SEED", "42"))
DATA_SCALE = os.getenv("DATA_SCALE", "small")

DB_NAME = os.getenv("SOURCE_POSTGRES_DB", "smart_office")
DB_USER = os.getenv("SOURCE_POSTGRES_USER", "smartoffice_admin")
DB_PASS = os.getenv("SOURCE_POSTGRES_PASSWORD", "smartoffice_password")
DB_HOST = os.getenv("SOURCE_POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("SOURCE_POSTGRES_PORT", "5434")
