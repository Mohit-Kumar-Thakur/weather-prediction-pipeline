from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from database import SessionLocal
from models import WeatherData
from predict import load_model, load_forecast_data, create_forecast_features, predict_temperature

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


class PredictionResponse(BaseModel):
    time                    : datetime
    actual_temperature_c    : float
    predicted_temperature_c : float
    difference_c            : float

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
    

# ─────────────────────────────────────────
# Route 7 — Get ML temperature predictions
# ─────────────────────────────────────────
@app.get("/predict", response_model=List[PredictionResponse])
def get_predictions():
    """
    Loads the trained ML model and returns temperature
    predictions for all forecast hours in the database.
    """
    try:
        # load model
        model, feature_columns = load_model()

        # load forecast data from DB
        df_forecast = load_forecast_data()

        if df_forecast.empty:
            raise HTTPException(
                status_code=404,
                detail="No forecast data found in database. Run pipeline first."
            )

        # create features
        df_featured = create_forecast_features(df_forecast)

        # predict
        results = predict_temperature(model, feature_columns, df_featured)

        # convert to list of dicts for FastAPI to return
        return results.to_dict(orient="records")

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Model file ml_model.pkl not found. Run train.py first."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))