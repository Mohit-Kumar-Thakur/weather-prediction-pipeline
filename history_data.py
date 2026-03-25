import pandas as pd
import requests


def get_historical_data(latitude, longitude, start_date, end_date) :
    url = "https://archive-api.open-meteo.com/v1/archive"
    
    params = {
        "latitude" : latitude,
        "longitude" : longitude,
        "start_date" : start_date,
        "end_date" : end_date,
        "hourly" : [
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "windspeed_10m",
            "pressure_msl",
            "cloudcover"
        ],
        "timezone" : "auto"
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
     from utils import weather_to_dataframe
     hist_data = get_historical_data(28.6139, 77.2090, "2024-01-01",  "2024-12-31")
     hist_df = weather_to_dataframe(hist_data)
     print(hist_df.head())

