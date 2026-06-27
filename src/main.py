"""
main.py
-------
FastAPI server on port 7005.

Run with:
    python src/main.py
or:
    uvicorn main:app --app-dir src --host 0.0.0.0 --port 7005

Endpoints:
    GET  /              — health check
    GET  /status        — check Gemma model availability
    GET  /logs          — view recent app or model logs
    POST /report        — full astrology report (story + predictions + quote)
    POST /quote         — daily quote (today or tomorrow)
    POST /sun-sign      — quick sun sign from DOB only
"""

import os
import json
import time
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn

from orchestrator import generate_full_report, get_daily_quote, get_quick_sun_sign
from llm_client import check_model_status, LOG_FILE as GEMMA_LOG_FILE


# ---------- App-level request/response logging ----------
# Each API call is appended as one JSON line to logs/app.jsonl,
# capturing the endpoint, the request input, and the response output.

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
APP_LOG_FILE = os.path.join(LOG_DIR, "app.jsonl")
os.makedirs(LOG_DIR, exist_ok=True)


def log_app(endpoint: str, request_data, response_data, seconds: float) -> None:
    record = {
        "timestamp": datetime.now().isoformat(),
        "endpoint": endpoint,
        "input": request_data,
        "output": response_data,
        "seconds": round(seconds, 2),
    }
    try:
        with open(APP_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[main] failed to write app log: {e}")


app = FastAPI(
    title="Astrology Daily Quotes API",
    description="Astrology reports + daily motivational quotes powered by Swiss Ephemeris and Gemma 4 E2B-IT",
    version="1.0.0",
)

# CORS — allow frontend to call from anywhere (tighten for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Request models ----------

class ReportRequest(BaseModel):
    name: str = Field(..., description="Full name", example="Arjun Sharma")
    dob: str = Field(..., description="Date of birth (YYYY-MM-DD)", example="1995-05-15")
    tob: str = Field(..., description="Time of birth (HH:MM 24-hour)", example="10:30")
    place: Optional[str] = Field(None, description="Birth place (optional)", example="Jaipur")


class QuoteRequest(BaseModel):
    zodiac: str = Field(..., description="Zodiac sign", example="Taurus")
    tomorrow: bool = Field(False, description="If True, get tomorrow's quote")


class SunSignRequest(BaseModel):
    dob: str = Field(..., description="Date of birth (YYYY-MM-DD)", example="1995-05-15")


# ---------- Endpoints ----------

@app.get("/")
def root():
    return {
        "service": "Astrology Daily Quotes API",
        "version": "1.0.0",
        "endpoints": ["/status", "/logs", "/report", "/quote", "/sun-sign"],
    }


@app.get("/status")
def status():
    """Check whether the Gemma model is loaded."""
    return check_model_status()


@app.get("/logs")
def get_logs(type: str = "app", limit: int = 50):
    """
    Return the most recent log entries.

    Query params:
        type   — "app" (default) for API request/response log,
                 "gemma" for the model input/output log
        limit  — max number of entries to return (default 50)
    """
    files = {"app": APP_LOG_FILE, "gemma": GEMMA_LOG_FILE}
    if type not in files:
        return {"success": False, "error": "type must be 'app' or 'gemma'"}

    path = files[type]
    if not os.path.exists(path):
        return {"success": True, "type": type, "count": 0, "entries": []}

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    entries = []
    for line in lines[-max(1, limit):]:
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    return {"success": True, "type": type, "count": len(entries), "entries": entries}


@app.post("/report")
def report(req: ReportRequest):
    """
    Generate a full astrology report:
        - Personalized story
        - Future predictions
        - Today's motivational quote
    """
    start = time.time()
    result = generate_full_report(req.name, req.dob, req.tob, req.place)
    log_app("/report", req.model_dump(), result, time.time() - start)
    return result


@app.post("/quote")
def quote(req: QuoteRequest):
    """Get today's or tomorrow's motivational quote for a zodiac sign."""
    start = time.time()
    result = get_daily_quote(req.zodiac, tomorrow=req.tomorrow)
    log_app("/quote", req.model_dump(), result, time.time() - start)
    return result


@app.post("/sun-sign")
def sun_sign(req: SunSignRequest):
    """Fast sun-sign lookup from DOB only — no LLM, no ephemeris."""
    start = time.time()
    result = get_quick_sun_sign(req.dob)
    log_app("/sun-sign", req.model_dump(), result, time.time() - start)
    return result


# ---------- Run ----------

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=7005, reload=False)
