import requests
import pandas as pd

from utils import weather_to_dataframe

def get_weather_data(latitude, longitude, days=7):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": [
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "windspeed_10m",
            "pressure_msl",
            "cloudcover",
            "apparent_temperature"
        ],
        "daily":[
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "windspeed_10m_max"
        ],
        "forecast_days": days,
        "timezone": "auto"
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()  # Check if the request was successful
    return response.json()

if __name__ == "__main__":
    data = get_weather_data(28.6139, 77.2090)
    print(data)
    df = weather_to_dataframe(data)
    print(df.head())
    

    