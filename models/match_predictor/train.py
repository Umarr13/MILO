import os
import sqlite3
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import accuracy_score, log_loss, classification_report, brier_score_loss
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from datetime import datetime

# Import our custom advanced modules
from elo_features import compute_historical_elo
from poisson_model import prepare_poisson_data, train_poisson_model, simulate_match

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = "../../milo.db"

def calculate_rest_days(df):
    """Calculates the number of rest days for home and away teams prior to each match."""
    df['utc_date'] = pd.to_datetime(df['utc_date'])
    df = df.sort_values('utc_date')
    
    last_match_date = {}
    home_rest = []
    away_rest = []
    
    for _, row in df.iterrows():
        home_id = row['home_team_id']
        away_id = row['away_team_id']
        match_date = row['utc_date']
        
        # Calculate rest days (default 14 days for start of season or long breaks)
        h_rest = (match_date - last_match_date.get(home_id, match_date - pd.Timedelta(days=14))).days
        a_rest = (match_date - last_match_date.get(away_id, match_date - pd.Timedelta(days=14))).days
        
        # Cap rest days at 14 to avoid skewing data with off-season breaks
        home_rest.append(min(h_rest, 14))
        away_rest.append(min(a_rest, 14))
        
        last_match_date[home_id] = match_date
        last_match_date[away_id] = match_date
        
    df['home_rest_days'] = home_rest
    df['away_rest_days'] = away_rest
    return df

def build_advanced_dataset():
    logger.info("Building advanced dataset...")
    
    # 1. Get Elo Ratings History
    logger.info("Computing Elo ratings...")
    df = compute_historical_elo()
    
    if df is None or len(df) == 0:
        logger.error("No data available.")
        return None
        
    # 2. Calculate Fatigue / Rest Days
    logger.info("Calculating team fatigue/rest days...")
    df = calculate_rest_days(df)
    
    # 3. Poisson Match Probabilities
    # We train a rolling Poisson model, or for simplicity, we use the global Poisson model 
    # to estimate underlying team strengths (simulated xG). 
    # A true rolling implementation takes time, so we'll use a static approximation for scaffolding.
    logger.info("Integrating Poisson expected goals...")
    poisson_data = prepare_poisson_data()
    p_model = train_poisson_model(poisson_data)
    
    poisson_home_wins, poisson_draws, poisson_away_wins = [], [], []
    for _, row in df.iterrows():
        p_a, p_d, p_h = simulate_match(p_model, row['home_team_id'], row['away_team_id'])
        poisson_home_wins.append(p_h)
        poisson_draws.append(p_d)
        poisson_away_wins.append(p_a)
        
    df['poisson_prob_home'] = poisson_home_wins
    df['poisson_prob_draw'] = poisson_draws
    df['poisson_prob_away'] = poisson_away_wins
    
    # 4. Target Variable
    def get_outcome(h, a):
        if h > a: return 2
        if h == a: return 1
        return 0
    df['outcome'] = df.apply(lambda r: get_outcome(r['home_goals'], r['away_goals']), axis=1)
    
    # Elo specific features
    df['elo_diff'] = df['home_elo_pre'] - df['away_elo_pre']
    
    return df

def train_ensemble_model():
    df = build_advanced_dataset()
    if df is None or len(df) < 50:
        logger.error("Insufficient data. Ensure the database is populated via data_pipeline/sync.py")
        return
        
    # Time-aware train/test split (80% train, 20% test)
    split_idx = int(len(df) * 0.8)
    train = df.iloc[:split_idx]
    test = df.iloc[split_idx:]
    
    feature_cols = [
        'home_elo_pre', 'away_elo_pre', 'elo_diff',
        'home_rest_days', 'away_rest_days',
        'poisson_prob_home', 'poisson_prob_draw', 'poisson_prob_away'
    ]
    
    X_train = train[feature_cols]
    y_train = train['outcome']
    X_test = test[feature_cols]
    y_test = test['outcome']
    
    logger.info(f"Training Advanced XGBoost Ensemble on {len(X_train)} samples...")
    # Adjust hyperparameters for football metrics (learning rate, depth)
    model = xgb.XGBClassifier(
        objective='multi:softprob',
        num_class=3,
        learning_rate=0.05,
        max_depth=4,
        eval_metric='mlogloss',
        seed=42
    )
    
    model.fit(X_train, y_train)
    
    # Evaluation
    logger.info("Evaluating model...")
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    ll = log_loss(y_test, y_pred_proba)
    
    # Brier Score computation for multi-class (football standard)
    y_test_dummies = pd.get_dummies(y_test).values
    brier = np.mean(np.sum((y_pred_proba - y_test_dummies)**2, axis=1))
    
    logger.info(f"Accuracy: {acc:.4f}")
    logger.info(f"Log Loss: {ll:.4f}")
    logger.info(f"Brier Score (Lower is better): {brier:.4f}")
    
    # Save Model
    logger.info("Serializing model...")
    model_path = "../../models/match_outcome_model.pkl"
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
        
    # Generate Evaluation Report (Confusion Matrix & Feature Importance)
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8,6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Away', 'Draw', 'Home'], 
                yticklabels=['Away', 'Draw', 'Home'])
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Advanced Model Confusion Matrix')
    plt.savefig('confusion_matrix_advanced.png')
    
    xgb.plot_importance(model)
    plt.title('Advanced Feature Importance')
    plt.savefig('feature_importance_advanced.png')
    
    logger.info("Advanced Match Outcome Model training complete!")

if __name__ == "__main__":
    train_ensemble_model()
