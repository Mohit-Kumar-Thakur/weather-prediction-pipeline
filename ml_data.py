import pandas as pd
import numpy as np
from database import SessionLocal
from models import WeatherData
from sklearn.model_selection import train_test_split


def load_historical_data():

    db = SessionLocal()
    try:
        records = db.query(WeatherData)\
                    .filter(WeatherData.source == "historical")\
                    .order_by(WeatherData.time.asc())\
                    .all()

        data = [{
            "time"                : r.time,
            "temperature_c"       : r.temperature_c,
            "feels_like_c"        : r.feels_like_c,
            "humidity_percent"    : r.humidity_percent,
            "precipitation_mm"    : r.precipitation_mm,
            "wind_speed_kmh"      : r.wind_speed_kmh,
            "pressure_hpa"        : r.pressure_hpa,
            "cloud_cover_percent" : r.cloud_cover_percent,
        } for r in records]

        df = pd.DataFrame(data)
        print(f"Loaded {len(df)} historical records from PostgreSQL")
        return df

    finally:
        db.close()


def create_features(df):

    df = df.copy()
    df = df.drop(columns=['feels_like_c'], errors='ignore')
    df = df.sort_values("time").reset_index(drop=True)
    df["hour"]       = df["time"].dt.hour
    df["day_of_week"] = df["time"].dt.dayofweek   # 0=Monday, 6=Sunday
    df["month"]      = df["time"].dt.month
    df["day_of_year"] = df["time"].dt.dayofyear


    df["temp_1hr_ago"]  = df["temperature_c"].shift(1)   
    df["temp_3hr_ago"]  = df["temperature_c"].shift(3)   
    df["temp_6hr_ago"]  = df["temperature_c"].shift(6)   
    df["temp_24hr_ago"] = df["temperature_c"].shift(24)  


    df["humidity_1hr_ago"]  = df["humidity_percent"].shift(1)
    df["humidity_24hr_ago"] = df["humidity_percent"].shift(24)


    df["temp_rolling_3h"]  = df["temperature_c"].rolling(window=3).mean()
    df["temp_rolling_6h"]  = df["temperature_c"].rolling(window=6).mean()
    df["temp_rolling_24h"] = df["temperature_c"].rolling(window=24).mean()


    df = df.dropna()
    df = df.reset_index(drop=True)

    print(f"Features created — {len(df)} rows, {len(df.columns)} columns")
    return df


def prepare_training_data(df):

    # define which columns are features
    feature_columns = [
    "hour",
    "day_of_week",
    "month",
    "day_of_year",
    "temp_1hr_ago",
    "temp_3hr_ago",
    "temp_6hr_ago",
    "temp_24hr_ago",
    "humidity_1hr_ago",
    "humidity_24hr_ago",
    "temp_rolling_3h",
    "temp_rolling_6h",
    "temp_rolling_24h",
    "humidity_percent",
    "wind_speed_kmh",
    "pressure_hpa",
    "cloud_cover_percent",
    "precipitation_mm"
    ]

    target_column = "temperature_c"

    X = df[feature_columns]   
    y = df[target_column]    


    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        shuffle=False
    )

    print(f"Training set   : {X_train.shape[0]} rows")
    print(f"Test set       : {X_test.shape[0]} rows")
    print(f"Features used  : {len(feature_columns)}")
    print(f"Target         : {target_column}")

    return X_train, X_test, y_train, y_test


if __name__ == "__main__":
    df_raw = load_historical_data()
    print("\nRaw data sample:")
    print(df_raw.head(3))

    df_featured = create_features(df_raw)
    print("\nFeature columns created:")
    print(list(df_featured.columns))


    print("\nPreparing train/test split...")
    X_train, X_test, y_train, y_test = prepare_training_data(df_featured)

    print("\nml_data.py working correctly — ready for train.py!")