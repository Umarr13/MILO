import os
import sqlite3
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = "../../milo.db"

def get_scouting_data():
    """
    Pulls player stats and calculates per-90 metrics.
    Filters out players with insufficient minutes to reduce noise.
    """
    conn = sqlite3.connect(DB_PATH)
    
    query = """
        SELECT 
            p.id, p.name, p.team_id, p.position, p.nationality,
            s.goals, s.assists, s.minutes_played, s.appearances
        FROM players p
        LEFT JOIN player_stats s ON p.id = s.player_id
    """
    try:
        df = pd.read_sql_query(query, conn)
    except Exception as e:
        logger.error(f"Database query failed: {e}")
        conn.close()
        return None
        
    conn.close()
    
    if df.empty or len(df) < 50:
        logger.warning("Insufficient player data. Generating synthetic data for scouting engine.")
        return generate_synthetic_scouting_data()
        
    # Clean data
    df = df.dropna(subset=['position', 'minutes_played'])
    df = df[df['minutes_played'] > 270] # At least 3 full matches
    
    # Calculate Per-90 Vectors
    df['90s'] = df['minutes_played'] / 90.0
    df['goals_p90'] = df['goals'] / df['90s']
    df['assists_p90'] = df['assists'] / df['90s']
    
    return df

def generate_synthetic_scouting_data(n_samples=2000):
    """Fallback generator if DB is empty."""
    np.random.seed(42)
    positions = ['Attacker', 'Midfielder', 'Defender']
    data = {
        'id': range(1, n_samples + 1),
        'name': [f"Player_{i}" for i in range(1, n_samples + 1)],
        'team_id': np.random.randint(1, 21, n_samples),
        'position': np.random.choice(positions, n_samples, p=[0.25, 0.45, 0.30]),
        'nationality': np.random.choice(['ENG', 'ESP', 'GER', 'FRA', 'ITA', 'BRA', 'ARG'], n_samples),
        'minutes_played': np.random.uniform(300, 3420, n_samples),
    }
    df = pd.DataFrame(data)
    
    # Generate distinct playstyles via base stats
    df['goals'] = np.where(df['position'] == 'Attacker', np.random.poisson(10, n_samples),
                  np.where(df['position'] == 'Midfielder', np.random.poisson(4, n_samples),
                  np.random.poisson(1, n_samples)))
                  
    df['assists'] = np.where(df['position'] == 'Attacker', np.random.poisson(5, n_samples),
                    np.where(df['position'] == 'Midfielder', np.random.poisson(8, n_samples),
                    np.random.poisson(2, n_samples)))
    
    df['90s'] = df['minutes_played'] / 90.0
    df['goals_p90'] = df['goals'] / df['90s']
    df['assists_p90'] = df['assists'] / df['90s']
    
    return df

def train_scouting_engine():
    df = get_scouting_data()
    if df is None:
        return
        
    logger.info("Training Player Scouting Engine (KMeans Clustering)...")
    
    # We cluster based on output metrics. In a real system, we'd add passes, tackles, xG, etc.
    features = ['goals_p90', 'assists_p90']
    
    # Segment by position to find true playstyles (e.g. Target Man vs Winger for Attackers)
    models = {}
    scalers = {}
    
    for pos in df['position'].unique():
        if pos == 'Goalkeeper': continue
        
        pos_df = df[df['position'] == pos]
        if len(pos_df) < 10: continue
        
        X = pos_df[features].fillna(0)
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Train KMeans
        n_clusters = min(4, len(X) // 5) # E.g., 4 playstyles per position
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        
        # Save cluster assignments
        df.loc[df['position'] == pos, 'playstyle_cluster'] = kmeans.fit_predict(X_scaled)
        
        models[pos] = kmeans
        scalers[pos] = scaler
        
    # Serialize Models
    model_dir = "../../models"
    os.makedirs(model_dir, exist_ok=True)
    with open(f'{model_dir}/scouting_models.pkl', 'wb') as f:
        pickle.dump({'kmeans': models, 'scalers': scalers}, f)
        
    logger.info("Scouting Engine models serialized.")
    return df, models, scalers

def find_similar_players(player_name, df, models, scalers, top_n=5):
    """Uses Cosine Similarity within the same cluster to find identical profiles."""
    player_row = df[df['name'] == player_name]
    if player_row.empty:
        logger.error(f"Player {player_name} not found.")
        return None
        
    pos = player_row['position'].values[0]
    cluster = player_row['playstyle_cluster'].values[0]
    
    if pos not in scalers or pd.isna(cluster):
        logger.error(f"No model available for {player_name}'s position.")
        return None
        
    # Filter to same position and cluster
    pool = df[(df['position'] == pos) & (df['playstyle_cluster'] == cluster)]
    
    features = ['goals_p90', 'assists_p90']
    X_pool = pool[features].fillna(0)
    X_pool_scaled = scalers[pos].transform(X_pool)
    
    p_idx = pool.index.get_loc(player_row.index[0])
    target_vec = X_pool_scaled[p_idx].reshape(1, -1)
    
    # Calculate Cosine Similarity
    sims = cosine_similarity(target_vec, X_pool_scaled).flatten()
    pool['similarity'] = sims
    
    # Sort and return
    similar = pool[pool['name'] != player_name].sort_values('similarity', ascending=False).head(top_n)
    return similar[['name', 'team_id', 'similarity', 'goals_p90', 'assists_p90']]

def calculate_team_fit(player_name, target_team_id, df):
    """
    Evaluates how well a player fits into a team based on statistical gaps.
    If the team's midfield lacks assists, and the player provides assists, fit score is high.
    """
    player_row = df[df['name'] == player_name]
    if player_row.empty:
        return 0
        
    pos = player_row['position'].values[0]
    p_goals_p90 = player_row['goals_p90'].values[0]
    p_assists_p90 = player_row['assists_p90'].values[0]
    
    # Get target team averages for that position
    team_squad = df[(df['team_id'] == target_team_id) & (df['position'] == pos)]
    if team_squad.empty:
        return 100.0 # Huge fit if they have no one in that position
        
    team_avg_goals = team_squad['goals_p90'].mean()
    team_avg_assists = team_squad['assists_p90'].mean()
    
    # Fit Score Logic: Reward players who are significantly better than the team's average
    goal_gap = max(0, p_goals_p90 - team_avg_goals)
    assist_gap = max(0, p_assists_p90 - team_avg_assists)
    
    base_score = 50.0
    fit_score = base_score + (goal_gap * 100) + (assist_gap * 150)
    return min(100.0, fit_score)

if __name__ == "__main__":
    df, models, scalers = train_scouting_engine()
    
    if df is not None:
        # Example Query
        sample_player = df['name'].iloc[0]
        logger.info(f"\n--- Scouting Report for: {sample_player} ---")
        
        sims = find_similar_players(sample_player, df, models, scalers)
        if sims is not None:
            logger.info("\nMost Similar Players:")
            print(sims)
            
        target_team = 5
        fit = calculate_team_fit(sample_player, target_team, df)
        logger.info(f"\nTeam Fit Score for Team ID {target_team}: {fit:.1f}/100")
