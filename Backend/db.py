import mysql.connector

import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# ============================================================
#  DATABASE CONNECTION
# ============================================================

def get_connection():
    """Create and return a new MySQL database connection using env variables."""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "crm360_db"),
        use_pure=True              # ← fixes MySQL 8+ auth issues
    )

