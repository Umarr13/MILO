import pandas as pd
import sqlite3
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.stats import poisson
import logging

logger = logging.getLogger(__name__)
DB_PATH = "../../milo.db"

def prepare_poisson_data():
    """Restructures data for Poisson regression: one row per team per match."""
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT id, utc_date, home_team_id, away_team_id, home_goals, away_goals 
        FROM matches 
        WHERE status = 'FINISHED'
    """
    try:
        df = pd.read_sql_query(query, conn)
    except Exception as e:
        logger.error(f"Failed to query database: {e}")
        conn.close()
        return None
    conn.close()
    
    if df.empty:
        return None
        
    # To run a Poisson regression for goals scored, we need rows for home and away
    goal_model_data = pd.concat([
        df[['home_team_id', 'away_team_id', 'home_goals']].assign(home=1).rename(
            columns={'home_team_id': 'team', 'away_team_id': 'opponent', 'home_goals': 'goals'}
        ),
        df[['away_team_id', 'home_team_id', 'away_goals']].assign(home=0).rename(
            columns={'away_team_id': 'team', 'home_team_id': 'opponent', 'away_goals': 'goals'}
        )
    ])
    
    # Need to make sure IDs are treated as categories, not continuous integers
    goal_model_data['team'] = goal_model_data['team'].astype(str)
    goal_model_data['opponent'] = goal_model_data['opponent'].astype(str)
    
    return goal_model_data

def train_poisson_model(data):
    """Trains a Poisson regression model to estimate Attack and Defense strengths."""
    if data is None or len(data) < 50:
        logger.warning("Not enough data to train Poisson model.")
        return None
        
    logger.info("Training Poisson Regression model...")
    formula = "goals ~ home + team + opponent"
    model = smf.glm(formula=formula, data=data, family=sm.families.Poisson()).fit()
    return model

def simulate_match(model, home_team_id, away_team_id, max_goals=10):
    """Simulates a match and returns probabilities for Win/Draw/Loss."""
    if model is None:
        return 0.33, 0.34, 0.33
        
    home_id_str = str(home_team_id)
    away_id_str = str(away_team_id)
    
    try:
        home_goals_avg = model.predict(pd.DataFrame(data={'team': [home_id_str], 'opponent': [away_id_str], 'home': [1]}))[0]
        away_goals_avg = model.predict(pd.DataFrame(data={'team': [away_id_str], 'opponent': [home_id_str], 'home': [0]}))[0]
    except KeyError:
        # Happens if a team wasn't in the training set
        logger.warning("Team not found in Poisson model training set.")
        return 0.33, 0.34, 0.33
        
    # Calculate probability matrix
    team_pred = [[poisson.pmf(i, team_avg) for i in range(0, max_goals)] for team_avg in [home_goals_avg, away_goals_avg]]
    match_matrix = np.outer(np.array(team_pred[0]), np.array(team_pred[1]))
    
    home_win = np.sum(np.tril(match_matrix, -1))
    draw = np.sum(np.diag(match_matrix))
    away_win = np.sum(np.triu(match_matrix, 1))
    
    return float(away_win), float(draw), float(home_win)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    data = prepare_poisson_data()
    if data is not None:
        model = train_poisson_model(data)
        if model is not None:
            print(model.summary())
            # Example simulation for random teams
            home_t = data['team'].iloc[0]
            away_t = data['team'].iloc[1]
            prob_a, prob_d, prob_h = simulate_match(model, home_t, away_t)
            logger.info(f"Sim {home_t} vs {away_t}: Away {prob_a:.2f}, Draw {prob_d:.2f}, Home {prob_h:.2f}")
