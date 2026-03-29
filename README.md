# End-to-End Weather Data Pipeline with ML Prediction

A production-grade data pipeline that fetches real-time and historical weather 
data, cleans it, stores it in PostgreSQL, and predicts temperature using 
a Machine Learning model served via a REST API.

---

## Live Demo
> Live API: https://weather-prediction-pipeline.onrender.com
> API Docs: https://weather-prediction-pipeline.onrender.com/docs

---

## ML Results
| Model | RMSE | MAE | R² |
|---|---|---|---|
| Linear Regression | 0.30°C | 0.22°C | 0.9975 |
| Random Forest | 0.51°C | 0.37°C | 0.9926 |
| XGBoost | 0.45°C | 0.35°C | 0.9940 |

Best model: **Linear Regression** — predicts Delhi temperature with only 0.30°C average error

---

## Tech Stack
| Layer | Tool |
|---|---|
| Language | Python |
| API Fetching | requests |
| Data Cleaning | pandas |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| ML Models | scikit-learn, XGBoost |
| Model Saving | joblib |
| REST API | FastAPI |
| Server | Uvicorn |

---

## Pipeline Flow
```
Open-Meteo API
      ↓
Data_request.py / history_data.py  — fetch forecast + historical
      ↓
clean.py                           — validate, rename, remove nulls
      ↓
PostgreSQL (weather_data table)    — store 8900+ records
      ↓
ml_data.py                         — feature engineering (18 features)
      ↓
train.py                           — train 3 models, save best
      ↓
predict.py                         — load model, predict temperature
      ↓
FastAPI /predict endpoint          — serve predictions via REST API
```

---

## Project Structure
```
├── Data_request.py   — fetches 7-day forecast from Open-Meteo API
├── history_data.py   — fetches full year historical weather data
├── utils.py          — shared weather_to_dataframe() helper
├── clean.py          — validates, renames and cleans raw data
├── models.py         — PostgreSQL table definition (SQLAlchemy)
├── database.py       — DB connection, session, table creation
├── store.py          — stores clean DataFrame into PostgreSQL
├── pipeline.py       — runs full fetch → clean → store pipeline
├── ml_data.py        — pulls DB data, creates 18 ML features
├── train.py          — trains 3 models, evaluates, saves best
├── predict.py        — loads model, predicts on forecast data
├── main.py           — FastAPI REST API with 7 endpoints
├── ml_model.pkl      — saved trained model (auto generated)
├── .env              — database URL and secrets (not in git)
└── requirements.txt  — all dependencies
```

---

## API Endpoints
| Method | Endpoint | Description |
|---|---|---|
| GET | / | Health check |
| GET | /weather | Get all weather records |
| GET | /weather/source/{source} | Filter by forecast or historical |
| GET | /weather/range | Filter by date range |
| GET | /weather/stats | Record count summary |
| GET | /predict | ML temperature predictions |
| POST | /pipeline/run | Trigger pipeline manually |

---

## Database Schema
```
weather_data table
├── id                  SERIAL PRIMARY KEY
├── time                TIMESTAMP NOT NULL
├── temperature_c       FLOAT
├── feels_like_c        FLOAT
├── humidity_percent    FLOAT
├── precipitation_mm    FLOAT
├── wind_speed_kmh      FLOAT
├── pressure_hpa        FLOAT
├── cloud_cover_percent FLOAT
└── source              VARCHAR(20) NOT NULL
```

---

## Setup Instructions

1. Clone the repo
```bash
git clone https://github.com/yourusername/end-to-end-data-pipeline.git
cd end-to-end-data-pipeline
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Create `.env` file
```
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/weather_db
```

4. Create database table
```bash
python database.py
```

5. Run the full pipeline
```bash
python pipeline.py
```

6. Train the ML model
```bash
python train.py
```

7. Start the API
```bash
uvicorn main:app --reload
```

8. Open API docs
```
http://localhost:8000/docs
```

---

## Key Features
- Fetches 8900+ hourly weather records from Open-Meteo API
- Cleans and validates data — removes nulls, validates ranges
- Stores structured data in PostgreSQL using SQLAlchemy ORM
- Engineers 18 features including lag and rolling averages
- Trains and compares 3 ML models — picks best automatically
- Achieves R² of 0.9975 — 99.75% temperature prediction accuracy
- Serves predictions live via FastAPI REST endpoint
- Interactive API docs auto-generated at /docs