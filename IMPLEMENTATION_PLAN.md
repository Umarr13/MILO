# Milo - Implementation Plan & Tracking

This document outlines the step-by-step implementation plan based on the 6 prompts provided, and tracks the current progress.

## 📝 Current Status
**Phase:** 7 - Testing & Cloud Deployment (AWS)
**Next Action:** Begin Phase 7

---

## 🗺️ Implementation Roadmap

### [x] Prompt 1: Project Scaffold + Data Pipeline
- [x] Initialize Python environment and `requirements.txt`.
- [x] Create `/data_pipeline` directory.
- [x] Build `football-data.org` API wrapper with `requests` (rate-limit-aware retry/backoff).
- [x] Set up SQLite database schema (`teams`, `players`, `matches`, `player_stats`).
- [x] Write sync script to pull and store raw JSON + parsed rows.
- [x] Implement feature engineering module (per-90 stats, rolling 5-match form, H2H aggregates).
- [x] Add `.env` config loading for API keys.
- [x] Write docstrings and pipeline execution instructions.

### [x] Prompt 2: Match Outcome Model
- [x] Create `/models/match_predictor` directory.
- [x] Extract features from SQLite (team form, H2H, rolling goals, shots, home/away flag).
- [x] Implement time-aware train/test split.
- [x] Train XGBoost multiclass classifier (Win/Draw/Loss).
- [x] Evaluate using accuracy, log-loss, and per-class precision/recall.
- [x] Ensure output is a probability distribution.
- [x] Serialize model to `/models/match_outcome_model.pkl`.
- [x] Generate evaluation report (confusion matrix, feature importance).

### [x] Prompt 3: Transfer Value Model
- [x] Create `/models/transfer_value` directory.
- [x] Integrate supplementary market value dataset (e.g., Kaggle Transfermarkt) and join with `player_stats`.
- [x] Extract features (age, position, goals, assists, mins played, appearances, tier, contract).
- [x] Train baseline LinearRegression model.
- [x] Train RandomForestRegressor model.
- [x] Compare using MAE and RMSE; select best performer.
- [x] Ensure output includes confidence range and feature importance.
- [x] Serialize winning model to `/models/transfer_value_model.pkl`.
- [x] Generate evaluation charts (predicted vs actual).

### [x] Prompt 4: Player Scouting Engine
- [x] Create `/models/scouting_engine` directory.
- [x] Build per-90 stat vectors segmented by position.
- [x] Standardize features using `StandardScaler`.
- [x] Train KMeans clustering to group playstyles.
- [x] Implement cosine similarity ranking within clusters.
- [x] Develop team-fit scoring function based on team positional statistical gaps.
- [x] Serialize KMeans model and scaler to `/models/scouting_model.pkl` and `/models/scaler.pkl`.
- [x] Write query script for similar players and best-fit teams.

### [x] Prompt 5: FastAPI Backend
- [x] Create `/backend` directory.
- [x] Initialize FastAPI application.
- [x] Implement model loading at startup (`@app.on_event("startup")`).
- [x] Build `POST /predict/value` endpoint.
- [x] Build `POST /predict/match` endpoint.
- [x] Build `GET /scout/similar/{player_id}` endpoint.
- [x] Build `GET /scout/team-fit/{player_id}/{team_id}` endpoint.
- [x] Build `GET /teams` and `GET /players` endpoints.
- [x] Build `POST /admin/refresh-data` endpoint (API key protected).
- [x] Configure CORS, in-memory caching, and OpenAPI docs.

### [x] Prompt 6: Flutter App
- [x] Initialize Flutter project `/app`.
- [x] Setup dependencies: `riverpod`, `dio`, `fl_chart`, `hive`.
- [x] Implement UI Theme (Dark theme, football aesthetic).
- [x] Build Home/Dashboard Screen.
- [x] Build Match Predictor Screen.
  - [x] Implement Physical Readiness (Stamina/Rest Days) Meter.
  - [x] Implement Interactive Poisson Scoreline Heatmap Matrix.
  - [x] Implement Dynamic Elo Momentum Sparkline Chart.
  - [x] Implement Segmented Win/Draw/Loss Probability Gauge.
  - [x] Implement Smart Insights Tactical Text Generation.
- [x] Build Value Predictor Screen.
- [x] Build Scouting Screen.
- [x] Implement state management, local caching, and error handling.

### [ ] Phase 7: Real-World Testing & Cloud Deployment (AWS)
- [ ] Save the uploaded app icon to `app/assets/icon.png` and configure `flutter_launcher_icons`.
- [ ] Connect and configure an AWS EC2 instance.
- [ ] Containerize the FastAPI backend and ML models using Docker.
- [ ] Configure Nginx reverse proxy and SSL on AWS.
- [ ] Run full end-to-end integration tests using the real-world GitHub football datasets.
