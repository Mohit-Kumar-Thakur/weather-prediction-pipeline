# End-to-End Data Pipeline with ML Prediction

A production-grade data pipeline that fetches real-time and historical weather data, cleans it, and stores it in PostgreSQL.

## Tech Stack
- **Python** — core language
- **requests** — API fetching
- **pandas** — data cleaning
- **PostgreSQL** — database
- **SQLAlchemy** — ORM
- **FastAPI** — REST API (in progress)

## Project Structure
```
├── Data_request.py   — fetches 7-day forecast from Open-Meteo API
├── history_data.py   — fetches historical weather data
├── utils.py          — shared helper functions
├── clean.py          — validates and cleans raw data
├── models.py         — PostgreSQL table definition
├── database.py       — database connection and setup
├── store.py          — stores clean data into PostgreSQL
├── pipeline.py       — full pipeline runner (coming soon)
└── main.py           — FastAPI REST endpoints (coming soon)
```

## Pipeline Flow
```
API → fetch → clean → validate → store in PostgreSQL
```

## Setup Instructions

1. Clone the repo
2. Install dependencies
   pip install -r requirements.txt
3. Create a .env file
   DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/weather_db
4. Create the database table
   python database.py
5. Run the pipeline
   python store.py