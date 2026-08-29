import pandas as pd
import sqlite3
import logging

logger = logging.getLogger(__name__)
DB_PATH = "../../milo.db"

class EloSystem:
    def __init__(self, k_factor=20, home_advantage=100, base_rating=1500):
        self.k_factor = k_factor
        self.home_advantage = home_advantage
        self.base_rating = base_rating
        self.ratings = {}

    def get_rating(self, team_id):
        return self.ratings.get(team_id, self.base_rating)

    def expected_result(self, rating_a, rating_b, is_home=False):
        """Calculate expected result (probability of win) for team A vs team B"""
        diff = rating_b - rating_a
        if is_home:
            diff -= self.home_advantage
        return 1 / (1 + 10 ** (diff / 400))

    def update_ratings(self, home_id, away_id, home_goals, away_goals):
        home_rating = self.get_rating(home_id)
        away_rating = self.get_rating(away_id)
        
        home_expected = self.expected_result(home_rating, away_rating, is_home=True)
        away_expected = 1 - home_expected
        
        if home_goals > away_goals:
            home_actual, away_actual = 1, 0
        elif home_goals == away_goals:
            home_actual, away_actual = 0.5, 0.5
        else:
            home_actual, away_actual = 0, 1
            
        # Margin of victory multiplier (to adjust for blowouts)
        goal_diff = abs(home_goals - away_goals)
        mov_multiplier = 1
        if goal_diff == 2:
            mov_multiplier = 1.5
        elif goal_diff >= 3:
            mov_multiplier = (11 + goal_diff) / 8.0

        home_new = home_rating + (self.k_factor * mov_multiplier * (home_actual - home_expected))
        away_new = away_rating + (self.k_factor * mov_multiplier * (away_actual - away_expected))
        
        self.ratings[home_id] = home_new
        self.ratings[away_id] = away_new
        
        return home_new, away_new

def compute_historical_elo():
    """Iterates through matches chronologically and computes pre-match ELO for both teams"""
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT id, utc_date, home_team_id, away_team_id, home_goals, away_goals 
        FROM matches 
        WHERE status = 'FINISHED'
        ORDER BY utc_date ASC
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

    elo_system = EloSystem()
    pre_match_elo_home = []
    pre_match_elo_away = []

    for _, row in df.iterrows():
        home_id = row['home_team_id']
        away_id = row['away_team_id']
        
        # Store pre-match ELO
        pre_match_elo_home.append(elo_system.get_rating(home_id))
        pre_match_elo_away.append(elo_system.get_rating(away_id))
        
        # Update ELO post-match
        elo_system.update_ratings(home_id, away_id, row['home_goals'], row['away_goals'])
        
    df['home_elo_pre'] = pre_match_elo_home
    df['away_elo_pre'] = pre_match_elo_away
    
    return df

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("Computing Historical ELO ratings...")
    elo_df = compute_historical_elo()
    if elo_df is not None:
        logger.info(f"Computed ELO for {len(elo_df)} matches.")
        print(elo_df[['utc_date', 'home_team_id', 'home_elo_pre', 'away_team_id', 'away_elo_pre']].tail())
