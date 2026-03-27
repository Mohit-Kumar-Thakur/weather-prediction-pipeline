from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from database import SessionLocal
from models import WeatherData

# ─────────────────────────────────────────
# Create the FastAPI app
# ─────────────────────────────────────────
app = FastAPI(
    title="Weather Data API",
    description="Fetch, clean and serve weather data for Delhi from Open-Meteo",
    version="1.0.0"
)


# ─────────────────────────────────────────
# Response schema using Pydantic
# ─────────────────────────────────────────
class WeatherResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id                  : int
    time                : datetime
    temperature_c       : Optional[float]
    feels_like_c        : Optional[float]
    humidity_percent    : Optional[float]
    precipitation_mm    : Optional[float]
    wind_speed_kmh      : Optional[float]
    pressure_hpa        : Optional[float]
    cloud_cover_percent : Optional[float]
    source              : str



# ─────────────────────────────────────────
# Route 1 — Health check
# ─────────────────────────────────────────
@app.get("/")
def root():
    return {
        "message" : "Weather Data API is running",
        "version" : "1.0.0",
        "docs"    : "/docs"
    }


# ─────────────────────────────────────────
# Route 2 — Get all records (with limit)
# ─────────────────────────────────────────
@app.get("/weather", response_model=List[WeatherResponse])
def get_all_weather(
    limit : int = Query(default=100, le=1000, description="Max records to return")
):
    db = SessionLocal()
    try:
        records = db.query(WeatherData)\
                    .order_by(WeatherData.time.desc())\
                    .limit(limit)\
                    .all()
        return records
    finally:
        db.close()


# ─────────────────────────────────────────
# Route 3 — Get by source (forecast / historical)
# ─────────────────────────────────────────
@app.get("/weather/source/{source}", response_model=List[WeatherResponse])
def get_by_source(
    source : str,
    limit  : int = Query(default=100, le=1000)
):
    if source not in ["forecast", "historical"]:
        raise HTTPException(
            status_code=400,
            detail="source must be 'forecast' or 'historical'"
        )
    db = SessionLocal()
    try:
        records = db.query(WeatherData)\
                    .filter(WeatherData.source == source)\
                    .order_by(WeatherData.time.desc())\
                    .limit(limit)\
                    .all()
        return records
    finally:
        db.close()


# ─────────────────────────────────────────
# Route 4 — Get by date range
# ─────────────────────────────────────────
@app.get("/weather/range", response_model=List[WeatherResponse])
def get_by_date_range(
    start : datetime = Query(description="Start datetime e.g. 2024-01-01T00:00:00"),
    end   : datetime = Query(description="End datetime   e.g. 2024-01-07T00:00:00")
):
    if start >= end:
        raise HTTPException(
            status_code=400,
            detail="start date must be before end date"
        )
    db = SessionLocal()
    try:
        records = db.query(WeatherData)\
                    .filter(WeatherData.time >= start)\
                    .filter(WeatherData.time <= end)\
                    .order_by(WeatherData.time.asc())\
                    .all()
        return records
    finally:
        db.close()


# ─────────────────────────────────────────
# Route 5 — Get stats summary
# ─────────────────────────────────────────
@app.get("/weather/stats")
def get_stats():
    db = SessionLocal()
    try:
        total      = db.query(WeatherData).count()
        forecast   = db.query(WeatherData).filter(WeatherData.source == "forecast").count()
        historical = db.query(WeatherData).filter(WeatherData.source == "historical").count()
        return {
            "total_records"      : total,
            "forecast_records"   : forecast,
            "historical_records" : historical
        }
    finally:
        db.close()


# ─────────────────────────────────────────
# Route 6 — Trigger pipeline manually
# ─────────────────────────────────────────
@app.post("/pipeline/run")
def trigger_pipeline():
    try:
        from pipeline import run_pipeline
        run_pipeline()
        return {"status": "success", "message": "Pipeline ran successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))