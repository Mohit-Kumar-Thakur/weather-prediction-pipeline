import joblib
import pandas as pd
from database import SessionLocal
from models import WeatherData


# ─────────────────────────────────────────
# Step 1: Load the saved model
# ─────────────────────────────────────────
def load_model(path="ml_model.pkl"):
    saved = joblib.load(path)
    model = saved["model"]
    feature_columns = saved["feature_columns"]
    print(f"Model loaded from {path}")
    print(f"Features expected: {len(feature_columns)}")
    return model, feature_columns


# ─────────────────────────────────────────
# Step 2: Load forecast data from PostgreSQL
# ─────────────────────────────────────────
def load_forecast_data():
    db = SessionLocal()
    try:
        records = db.query(WeatherData)\
                    .filter(WeatherData.source == "forecast")\
                    .order_by(WeatherData.time.asc())\
                    .all()

        data = [{
            "time"                : r.time,
            "temperature_c"       : r.temperature_c,
            "humidity_percent"    : r.humidity_percent,
            "precipitation_mm"    : r.precipitation_mm,
            "wind_speed_kmh"      : r.wind_speed_kmh,
            "pressure_hpa"        : r.pressure_hpa,
            "cloud_cover_percent" : r.cloud_cover_percent,
        } for r in records]

        df = pd.DataFrame(data)
        df = df.sort_values("time").reset_index(drop=True)
        print(f"Loaded {len(df)} forecast records from PostgreSQL")
        return df

    finally:
        db.close()


# ─────────────────────────────────────────
# Step 3: Create same features as training
# ─────────────────────────────────────────
def create_forecast_features(df):
    """
    Creates the same feature columns that were used during training.
    Must match ml_data.py create_features() exactly.
    """
    df = df.copy()
    df = df.sort_values("time").reset_index(drop=True)

    # time features
    df["hour"] = df["time"].dt.hour
    df["day_of_week"] = df["time"].dt.dayofweek
    df["month"] = df["time"].dt.month
    df["day_of_year"] = df["time"].dt.dayofyear

    # lag features
    df["temp_1hr_ago"] = df["temperature_c"].shift(1)
    df["temp_3hr_ago"] = df["temperature_c"].shift(3)
    df["temp_6hr_ago"] = df["temperature_c"].shift(6)
    df["temp_24hr_ago"] = df["temperature_c"].shift(24)

    # humidity lag features
    df["humidity_1hr_ago"] = df["humidity_percent"].shift(1)
    df["humidity_24hr_ago"] = df["humidity_percent"].shift(24)

    # rolling features
    df["temp_rolling_3h"] = df["temperature_c"].rolling(window=3).mean()
    df["temp_rolling_6h"] = df["temperature_c"].rolling(window=6).mean()
    df["temp_rolling_24h"] = df["temperature_c"].rolling(window=24).mean()

    # fill NaN from shift/rolling with forward fill
    # we use ffill instead of dropna because we want ALL forecast hours
    df = df.ffill().bfill()

    print(f"Forecast features created — {len(df)} rows")
    return df


# ─────────────────────────────────────────
# Step 4: Make predictions
# ─────────────────────────────────────────
def predict_temperature(model, feature_columns, df_featured):
    X = df_featured[feature_columns]

    predictions = model.predict(X)

    results = pd.DataFrame({
        "time"                    : df_featured["time"].values,
        "actual_temperature_c"    : df_featured["temperature_c"].values,
        "predicted_temperature_c" : predictions.round(2)
    })

    results["difference_c"] = (
        results["predicted_temperature_c"] - results["actual_temperature_c"]
    ).round(2)

    return results


# ─────────────────────────────────────────
# Main
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("Prediction started...")
    print("=" * 50)

    # Step 1 — load model
    model, feature_columns = load_model()

    # Step 2 — load forecast data
    df_forecast = load_forecast_data()

    # Step 3 — create features
    df_featured = create_forecast_features(df_forecast)

    # Step 4 — predict
    results = predict_temperature(model, feature_columns, df_featured)

    # Step 5 — show results
    print("\nPrediction Results (first 10 hours):")
    print(results.head(10).to_string(index=False))

    print(f"\nTotal predictions made : {len(results)}")
    print(f"Avg predicted temp     : {results['predicted_temperature_c'].mean():.2f} °C")
    print(f"Min predicted temp     : {results['predicted_temperature_c'].min():.2f} °C")
    print(f"Max predicted temp     : {results['predicted_temperature_c'].max():.2f} °C")

    print("\n" + "=" * 50)
    print("Prediction complete!")
    print("=" * 50)