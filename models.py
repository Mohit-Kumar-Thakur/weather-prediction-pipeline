from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base() 

class WeatherData(Base):
    __tablename__ = "weather_data"

    id                  = Column(Integer, primary_key=True, autoincrement=True)
    time                = Column(DateTime, nullable=False)
    temperature_c       = Column(Float, nullable=True)
    feels_like_c        = Column(Float, nullable=True)
    humidity_percent    = Column(Float, nullable=True)
    precipitation_mm    = Column(Float, nullable=True)
    wind_speed_kmh      = Column(Float, nullable=True)
    pressure_hpa        = Column(Float, nullable=True)
    cloud_cover_percent = Column(Float, nullable=True)
    source              = Column(String(20), nullable=False)

    def __repr__(self):
        return f"<WeatherData time={self.time} source={self.source} temp={self.temperature_c}>"