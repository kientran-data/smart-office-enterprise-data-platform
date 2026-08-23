import os
from datetime import date, datetime
from dotenv import load_dotenv

load_dotenv()

HISTORY_START_DATE = date.fromisoformat(os.getenv("HISTORY_START_DATE", "2025-01-01"))
HISTORY_END_DATE = date.fromisoformat(os.getenv("HISTORY_END_DATE", "2026-08-21"))
RANDOM_SEED = int(os.getenv("GENERATOR_RANDOM_SEED", "42"))
DATA_SCALE = os.getenv("DATA_SCALE", "small")

LIVE_GENERATOR_TICK_SECONDS = float(os.getenv("LIVE_GENERATOR_TICK_SECONDS", "1"))
SIMULATION_SPEED = float(os.getenv("SIMULATION_SPEED", "60"))
try:
    SIMULATION_START_TIME = datetime.fromisoformat(os.getenv("SIMULATION_START_TIME", "2026-08-22T07:00:00+07:00"))
except:
    SIMULATION_START_TIME = datetime.now()

ACCESS_EVENT_RATE = float(os.getenv("ACCESS_EVENT_RATE", "0.40"))
IOT_EVENT_RATE = float(os.getenv("IOT_EVENT_RATE", "0.95"))
BOOKING_CREATE_RATE = float(os.getenv("BOOKING_CREATE_RATE", "0.03"))
BOOKING_UPDATE_RATE = float(os.getenv("BOOKING_UPDATE_RATE", "0.08"))
DOCUMENT_CREATE_RATE = float(os.getenv("DOCUMENT_CREATE_RATE", "0.02"))
SIGNING_UPDATE_RATE = float(os.getenv("SIGNING_UPDATE_RATE", "0.06"))
EMPLOYEE_UPDATE_RATE = float(os.getenv("EMPLOYEE_UPDATE_RATE", "0.002"))
ENABLE_DELETE_DEMO = os.getenv("ENABLE_DELETE_DEMO", "false").lower() == "true"

DB_NAME = os.getenv("SOURCE_POSTGRES_DB", "smart_office")
DB_USER = os.getenv("SOURCE_POSTGRES_USER", "smartoffice_admin")
DB_PASS = os.getenv("SOURCE_POSTGRES_PASSWORD", "smartoffice_password")
DB_HOST = os.getenv("SOURCE_POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("SOURCE_POSTGRES_PORT", "5434")
