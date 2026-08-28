# Milo - Implementation Plan & Tracking

This document outlines the step-by-step implementation plan based on the 6 prompts provided, and tracks the current progress.

## 📝 Current Status
**Phase:** 0 - Project Scaffolding
**Next Action:** Begin Prompt 1 (Data Pipeline)

---

## 🗺️ Implementation Roadmap

### [ ] Prompt 1: Project Scaffold + Data Pipeline
- [ ] Initialize Python environment and `requirements.txt`.
- [ ] Create `/data_pipeline` directory.
- [ ] Build `football-data.org` API wrapper with `requests` (rate-limit-aware retry/backoff).
- [ ] Set up SQLite database schema (`teams`, `players`, `matches`, `player_stats`).
- [ ] Write sync script to pull and store raw JSON + parsed rows.
- [ ] Implement feature engineering module (per-90 stats, rolling 5-match form, H2H aggregates).
- [ ] Add `.env` config loading for API keys.
- [ ] Write docstrings and pipeline execution instructions.

### [ ] Prompt 2: Match Outcome Model
- [ ] Create `/models/match_predictor` directory.
- [ ] Extract features from SQLite (team form, H2H, rolling goals, shots, home/away flag).
- [ ] Implement time-aware train/test split.
- [ ] Train XGBoost multiclass classifier (Win/Draw/Loss).
- [ ] Evaluate using accuracy, log-loss, and per-class precision/recall.
- [ ] Ensure output is a probability distribution.
- [ ] Serialize model to `/models/match_outcome_model.pkl`.
- [ ] Generate evaluation report (confusion matrix, feature importance).

### [ ] Prompt 3: Transfer Value Model
- [ ] Create `/models/transfer_value` directory.
- [ ] Integrate supplementary market value dataset (e.g., Kaggle Transfermarkt) and join with `player_stats`.
- [ ] Extract features (age, position, goals, assists, mins played, appearances, tier, contract).
- [ ] Train baseline LinearRegression model.
- [ ] Train RandomForestRegressor model.
- [ ] Compare using MAE and RMSE; select best performer.
- [ ] Ensure output includes confidence range and feature importance.
- [ ] Serialize winning model to `/models/transfer_value_model.pkl`.
- [ ] Generate evaluation charts (predicted vs actual).

### [ ] Prompt 4: Player Scouting Engine
- [ ] Create `/models/scouting_engine` directory.
- [ ] Build per-90 stat vectors segmented by position.
- [ ] Standardize features using `StandardScaler`.
- [ ] Train KMeans clustering to group playstyles.
- [ ] Implement cosine similarity ranking within clusters.
- [ ] Develop team-fit scoring function based on team positional statistical gaps.
- [ ] Serialize KMeans model and scaler to `/models/scouting_model.pkl` and `/models/scaler.pkl`.
- [ ] Write query script for similar players and best-fit teams.

### [ ] Prompt 5: FastAPI Backend
- [ ] Create `/backend` directory.
- [ ] Initialize FastAPI application.
- [ ] Implement model loading at startup (`@app.on_event("startup")`).
- [ ] Build `POST /predict/value` endpoint.
- [ ] Build `POST /predict/match` endpoint.
- [ ] Build `GET /scout/similar/{player_id}` endpoint.
- [ ] Build `GET /scout/team-fit/{player_id}/{team_id}` endpoint.
- [ ] Build `GET /teams` and `GET /players` endpoints.
- [ ] Build `POST /admin/refresh-data` endpoint (API key protected).
- [ ] Configure CORS, in-memory caching, and OpenAPI docs.

### [ ] Prompt 6: Flutter App
- [ ] Initialize Flutter project `/app`.
- [ ] Setup dependencies: `riverpod`, `dio`, `fl_chart`, `hive`.
- [ ] Implement UI Theme (Dark theme, football aesthetic).
- [ ] Build Home/Dashboard Screen.
- [ ] Build Match Predictor Screen.
- [ ] Build Value Predictor Screen.
- [ ] Build Scouting Screen.
- [ ] Implement state management, local caching, and error handling.
