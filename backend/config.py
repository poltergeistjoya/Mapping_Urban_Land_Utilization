import os
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Database configuration
DB_USER = "postgres"
DB_PASSWORD = "yourpassword"
DB_HOST = "db"  # Use 'localhost' for local development, 'db' for docker
DB_PORT = "5432"
DB_NAME = "urban_utilization"

# Database URLs
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
DATABASE_URL_ASYNC = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Other configuration
LOCAL_IP = os.getenv("LOCAL_IP", "localhost")  # Fallback to localhost if not set
BATCH_SIZE = 5000  # For database operations 
