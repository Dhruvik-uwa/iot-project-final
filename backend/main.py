from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

import schemas
import supabase_store
from supabase_store import SupabaseError

app = FastAPI(title="Smart Flood Sentinel Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=schemas.HealthRead)
def health():
    return supabase_store.health_status()


@app.post("/api/telemetry", response_model=schemas.TelemetryRead)
def receive_telemetry(payload: schemas.TelemetryCreate):
    try:
        return supabase_store.create_telemetry(payload)
    except SupabaseError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/telemetry/latest", response_model=schemas.TelemetryRead)
def latest_telemetry():
    try:
        telemetry = supabase_store.get_latest_telemetry()
        if telemetry is None:
            raise HTTPException(status_code=404, detail="No telemetry has been recorded yet.")
        return telemetry
    except SupabaseError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/telemetry/history", response_model=list[schemas.TelemetryRead])
def telemetry_history(limit: int = Query(default=50, ge=1, le=500)):
    try:
        return supabase_store.get_telemetry_history(limit)
    except SupabaseError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/alerts", response_model=list[schemas.AlertRead])
def alert_history(limit: int = Query(default=50, ge=1, le=500)):
    try:
        return supabase_store.get_alerts(limit)
    except SupabaseError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
