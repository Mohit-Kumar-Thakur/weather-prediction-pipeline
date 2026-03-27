from data_request import get_weather_data
from history_data import get_historical_data
from utils import weather_to_dataframe
from clean import clean_dataframe
from store import store_weather_data
from database import init_db


def run_pipeline(latitude=28.6139, longitude=77.2090,
                 history_start="2024-01-01", history_end="2024-12-31"):

    print("=" * 50)
    print("Pipeline started...")
    print("=" * 50)

    # ─────────────────────────────────────────
    # Step 1: Make sure DB table exists
    # ─────────────────────────────────────────
    print("\n[1/6] Initializing database...")
    init_db()

    # ─────────────────────────────────────────
    # Step 2: Fetch forecast data
    # ─────────────────────────────────────────
    print("\n[2/6] Fetching forecast data...")
    raw_forecast = get_weather_data(latitude, longitude)
    print(f"Fetched raw forecast — {len(raw_forecast['hourly']['time'])} hourly records")

    # ─────────────────────────────────────────
    # Step 3: Fetch historical data
    # ─────────────────────────────────────────
    print("\n[3/6] Fetching historical data...")
    raw_historical = get_historical_data(latitude, longitude, history_start, history_end)
    print(f"Fetched raw historical — {len(raw_historical['hourly']['time'])} hourly records")

    # ─────────────────────────────────────────
    # Step 4: Convert both to DataFrames
    # ─────────────────────────────────────────
    print("\n[4/6] Converting to DataFrames...")
    df_forecast   = weather_to_dataframe(raw_forecast)
    df_historical = weather_to_dataframe(raw_historical)
    print(f"      Forecast shape   : {df_forecast.shape}")
    print(f"      Historical shape : {df_historical.shape}")

    # ─────────────────────────────────────────
    # Step 5: Clean both DataFrames
    # ─────────────────────────────────────────
    print("\n[5/6] Cleaning data...")
    clean_forecast   = clean_dataframe(df_forecast,   source="forecast")
    clean_historical = clean_dataframe(df_historical, source="historical")
    print(f"Clean forecast   : {clean_forecast.shape}")
    print(f"Clean historical : {clean_historical.shape}")
    print(f"Nulls in forecast   : {clean_forecast.isnull().sum().sum()}")
    print(f"Nulls in historical : {clean_historical.isnull().sum().sum()}")

    # ─────────────────────────────────────────
    # Step 6: Store both into PostgreSQL
    # ─────────────────────────────────────────
    print("\n[6/6] Storing data into PostgreSQL...")
    store_weather_data(clean_forecast)
    store_weather_data(clean_historical)

    print("\n" + "=" * 50)
    print("Pipeline completed successfully!")
    print("=" * 50)


if __name__ == "__main__":
    run_pipeline()