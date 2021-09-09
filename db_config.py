import os
from dotenv import load_dotenv

load_dotenv()
ADMIN_ID = os.getenv("ADMIN_ID")
HOST = os.getenv("PG_HOST")
PG_USER = os.getenv("PG_USER")
PG_PASS = os.getenv("PG_PASS")
PG_NAME = os.getenv("PG_NAME")
PG_PORT = os.getenv("PG_PORT")
DB_API_PORT = os.getenv("DB_API_PORT")
