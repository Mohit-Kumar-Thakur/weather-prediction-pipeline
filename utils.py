import pandas as pd

def weather_to_dataframe(data):
    hourly = pd.DataFrame(data['hourly'])
    hourly['time'] = pd.to_datetime(hourly['time'])
    hourly.set_index('time', inplace = True)
    return hourly