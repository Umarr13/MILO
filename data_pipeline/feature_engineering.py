import pandas as pd
import sqlite3
from data_pipeline.database import get_connection

def calculate_per_90_stats():
    """Derives per-90 metrics from the player_stats table."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM player_stats", conn)
    conn.close()
    
    if df.empty:
        return df
        
    df['games_equivalent'] = df['minutes_played'] / 90.0
    df['games_equivalent'] = df['games_equivalent'].replace(0, 1) # smooth for players with 0 mins
    
    df['goals_per_90'] = df['goals'] / df['games_equivalent']
    df['assists_per_90'] = df['assists'] / df['games_equivalent']
    
    return df

def get_team_rolling_form(team_id, window=5):
    """Calculates rolling form (last N matches) for a specific team."""
    conn = get_connection()
    query = f"""
        SELECT * FROM matches 
        WHERE (home_team_id = {team_id} OR away_team_id = {team_id})
        AND status = 'FINISHED'
        ORDER BY utc_date DESC
        LIMIT {window}
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        return {'points': 0, 'goals_scored': 0, 'goals_conceded': 0, 'form_string': ''}
        
    points = 0
    goals_scored = 0
    goals_conceded = 0
    form = []
    
    for _, row in df.iterrows():
        is_home = row['home_team_id'] == team_id
        scored = row['home_goals'] if is_home else row['away_goals']
        conceded = row['away_goals'] if is_home else row['home_goals']
        
        goals_scored += scored
        goals_conceded += conceded
        
        if scored > conceded:
            points += 3
            form.append('W')
        elif scored == conceded:
            points += 1
            form.append('D')
        else:
            form.append('L')
            
    return {
        'points': points,
        'goals_scored': goals_scored,
        'goals_conceded': goals_conceded,
        'form_string': ''.join(form[::-1])
    }

def get_h2h_aggregates(team_a_id, team_b_id, limit=5):
    """Calculates head-to-head aggregates between two teams."""
    conn = get_connection()
    query = f"""
        SELECT * FROM matches 
        WHERE ((home_team_id = {team_a_id} AND away_team_id = {team_b_id})
           OR (home_team_id = {team_b_id} AND away_team_id = {team_a_id}))
        AND status = 'FINISHED'
        ORDER BY utc_date DESC
        LIMIT {limit}
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        return {'team_a_wins': 0, 'team_b_wins': 0, 'draws': 0}
        
    team_a_wins = 0
    team_b_wins = 0
    draws = 0
    
    for _, row in df.iterrows():
        if row['home_goals'] == row['away_goals']:
            draws += 1
        else:
            home_won = row['home_goals'] > row['away_goals']
            if (row['home_team_id'] == team_a_id and home_won) or (row['away_team_id'] == team_a_id and not home_won):
                team_a_wins += 1
            else:
                team_b_wins += 1
                
    return {
        'team_a_wins': team_a_wins,
        'team_b_wins': team_b_wins,
        'draws': draws
    }
