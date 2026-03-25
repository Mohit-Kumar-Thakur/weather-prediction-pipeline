import pandas as pd
    
def clean_dataframe(df, source = "forecast"):
    df = df[~df.index.duplicated(keep='first')]
    df = df.dropna(how = 'all')
    df = df.fillna(df.mean(numeric_only = True))
    
    if 'temperature_2m' in df.columns:
        df = df[df['temperature_2m'].between(-90,60)]
        
    if 'relative_humidity_2m' in df.columns:
        df = df[df['relative_humidity_2m'].between(0,100)]
    
    if 'windspeed_10m' in df.columns:
        df = df[df['windspeed_10m']>=0]
    
    if 'pricipitation' in df.columns:
        df = df[df['precipitation']>=0]
        
    if 'cloudcover' in df.columns:
        df = df[df['cloudcover'].between(0,100)]
        
    rename_map = {
        'temperature_2m': 'temperature_c',
        'apparent_temperature': 'feels_like_c',
        'relative_humidity_2m': 'humidity_percent',
        'precipitation': 'precipitation_mm',
        'windspeed_10m': 'wind_speed_kmh',
        'pressure_msl': 'pressure_hpa',
        'cloudcover': 'cloud_cover_percent'
    }
    
    df = df.rename(columns={k: v for k,v in rename_map.items() if k in df.columns})
    
    df['source'] = source
    
    df = df.reset_index()
    df = df.rename(columns={'index' : 'time', 'time':'time'})
    return df


if __name__ == "__main__" :
    from data_request import get_weather_data
    from history_data import get_historical_data
    from utils import weather_to_dataframe
    
    print("--- Forecast Data ---")
    raw_forecast = get_weather_data(28.6139, 77.2090)
    df_forecast  = weather_to_dataframe(raw_forecast)
    clean_forecast = clean_dataframe(df_forecast, source="forecast")
    print(clean_forecast.head())
    print(f"Shape: {clean_forecast.shape}")
    print(f"Columns: {list(clean_forecast.columns)}")
    print(f"Nulls: {clean_forecast.isnull().sum().sum()}")
    
    print("\n--- Historical Data ---")
    raw_hist = get_historical_data(28.6139, 77.2090, "2024-01-01", "2024-01-07")
    df_hist  = weather_to_dataframe(raw_hist)
    clean_hist = clean_dataframe(df_hist, source="historical")
    print(clean_hist.head())
    print(f"Shape: {clean_hist.shape}")