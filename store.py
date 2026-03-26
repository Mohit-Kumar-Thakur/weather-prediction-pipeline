from database import SessionLocal
from models import WeatherData


def store_weather_data(clean_df):
    db = SessionLocal()

    try:
        records_added = 0

        for _, row in clean_df.iterrows():
            record = WeatherData(
                time                = row['time'],
                temperature_c       = row.get('temperature_c'),
                feels_like_c        = row.get('feels_like_c'),
                humidity_percent    = row.get('humidity_percent'),
                precipitation_mm    = row.get('precipitation_mm'),
                wind_speed_kmh      = row.get('wind_speed_kmh'),
                pressure_hpa        = row.get('pressure_hpa'),
                cloud_cover_percent = row.get('cloud_cover_percent'),
                source              = row['source']
            )
            db.add(record)
            records_added += 1

        db.commit()
        print(f"Successfully stored {records_added} records into PostgreSQL!")

    except Exception as e:
        db.rollback()
        print(f"Error storing data, rolled back: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    from data_request import get_weather_data
    from utils import weather_to_dataframe
    from clean import clean_dataframe

    raw   = get_weather_data(28.6139, 77.2090)
    df    = weather_to_dataframe(raw)
    clean = clean_dataframe(df, source="forecast")

    store_weather_data(clean)