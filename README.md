# Milo — Matchday Insights, Lineups & Odds

**Milo** is a comprehensive football analytics platform that combines real-time data pipelines, advanced machine learning models, a high-performance FastAPI backend, and a sleek, cross-platform Flutter application.

## 🚀 Project Overview

Milo provides actionable insights into football through three core predictive and analytical modules:

1. **Match Outcome Predictor**: Predicts Win/Draw/Loss probabilities using XGBoost, factoring in recent form, head-to-head records, and rolling team stats.
2. **Transfer Value Predictor**: Estimates player market value based on performance metrics, age, and contract status using a Random Forest Regressor.
3. **Player Scouting Engine**: Discovers statistically similar players using KMeans clustering and cosine similarity, and scores team fit based on positional statistical needs.

## 🏗️ Architecture Stack

- **Data Layer**: Python (Pandas), SQLite (Dev), API integrations (`football-data.org`, Kaggle datasets)
- **Machine Learning**: `scikit-learn`, `xgboost`, `pandas`
- **Backend API**: FastAPI (Python), `uvicorn`, `joblib` for model serving
- **Frontend App**: Flutter (Dart) with Riverpod (State Management) and Dio (Networking)

## 📁 Repository Structure (Planned)

```text
milo/
├── data_pipeline/         # API wrappers, rate-limiting, SQLite schema, sync scripts
├── feature_engineering/   # Deriving per-90 stats, rolling form, H2H aggregates
├── models/                # Trained .pkl models, training scripts, and evaluation charts
│   ├── match_predictor/   
│   ├── transfer_value/    
│   └── scouting_engine/   
├── backend/               # FastAPI application serving ML predictions
└── app/                   # Flutter mobile application
```

## ⚙️ Quick Start

*(Detailed setup instructions will be added as each module is implemented)*

1. **Data Sync**: Configure your `.env` with `FOOTBALL_DATA_API_KEY` and run `data_pipeline/sync.py`.
2. **Train Models**: Execute the training scripts in the `models/` directory.
3. **Start Backend**: Run `uvicorn main:app --reload` in the `backend/` directory.
4. **Run App**: Launch the Flutter app using `flutter run` in the `app/` directory.
