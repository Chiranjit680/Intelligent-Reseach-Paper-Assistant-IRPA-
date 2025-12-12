from sqlalchemy import text
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
from pathlib import Path
from .db.database import get_db

app = FastAPI(title="Intelligent Research Paper Assistant API", version="1.0.0")

@app.get("/health-check")
def health_check():
    return {"status": "healthy", "message": "API is running smoothly."}

@app.get("/db-test")
def db_test(db=Depends(get_db)):
    try:
        # Simple query to test database connection
        result = db.execute(text("SELECT 1")).scalar()
        if result == 1:
            return {"status": "success", "message": "Database connection is healthy."}
        else:
            return {"status": "error", "message": "Database connection test failed."}
    except Exception as e:
        return {"status": "error", "message": f"Database connection error: {str(e)}"}

