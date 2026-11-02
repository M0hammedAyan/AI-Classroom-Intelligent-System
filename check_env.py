import os, sys
os.chdir(r"D:\CipherTECH\Projects\AI-Classroom-Intelligent-System\vista")
from pathlib import Path
from dotenv import load_dotenv

# Simulate exactly what main.py does
load_dotenv()
load_dotenv(Path(__file__).resolve().parents[3] / ".env")
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

print(f"VISTA_DB_URL = {os.getenv('VISTA_DB_URL', 'NOT SET')}")
print(f"DATABASE_URL = {os.getenv('DATABASE_URL', 'NOT SET')}")

# Check what db.py would use
sys.path.insert(0, r"D:\CipherTECH\Projects\AI-Classroom-Intelligent-System\vista")
from backend.app.db import DB_URL
print(f"db.py DB_URL = {DB_URL}")
