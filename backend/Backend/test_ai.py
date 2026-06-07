import sys
import asyncio
sys.path.append("/Users/aayushishivnani/Desktop/Projects/AI-Attendance System/backend/Backend")
from app.routes.attendance import get_ai_models
try:
    print(get_ai_models())
except Exception as e:
    print("ERROR:", e)
