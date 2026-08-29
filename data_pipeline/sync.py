import logging
import json
import uuid
from data_pipeline.api_client import OpenFootballClient
from data_pipeline.database import get_connection, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def sync_from_github(client, conn):
    """
    Pulls data from openfootball GitHub and maps it to our schema.
    Since this is match-only data, it creates dummy players/squads 
    so the ML pipelines don't break.
    """
    data = client.get_matches_from_github()
    if not data:
        return
        
    cursor = conn.cursor()
    
    # Track teams we've seen to avoid inserting duplicates
    seen_teams = set()
    team_mapping = {} # maps string names to int IDs
    team_id_counter = 1
    
    # Process Matches
    matches = data.get('matches', [])
    for match in matches:
        home_name = match.get('team1')
        away_name = match.get('team2')
        
        # Ensure teams exist
        for t_name in [home_name, away_name]:
            if t_name not in seen_teams:
                cursor.execute('''
                    INSERT OR REPLACE INTO teams (id, name, raw_json)
                    VALUES (?, ?, ?)
                ''', (team_id_counter, t_name, json.dumps({'name': t_name})))
                seen_teams.add(t_name)
                team_mapping[t_name] = team_id_counter
                team_id_counter += 1
                
        home_id = team_mapping[home_name]
        away_id = team_mapping[away_name]
        
        score = match.get('score', {})
        home_goals = score.get('ft', [0,0])[0] if 'ft' in score else 0
        away_goals = score.get('ft', [0,0])[1] if 'ft' in score else 0
        
        # We generate a unique ID for the match since github json doesn't have one
        match_id = hash(f"{home_name}{away_name}{match.get('date')}") % 1000000
        
        cursor.execute('''
            INSERT OR REPLACE INTO matches (id, utc_date, status, home_team_id, away_team_id, home_goals, away_goals, raw_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            match_id, match.get('date', '2023-01-01'), 'FINISHED',
            home_id, away_id, home_goals, away_goals, json.dumps(match)
        ))
        
    conn.commit()
    logger.info("Matches synced from GitHub.")

def run_sync():
    init_db()
    client = OpenFootballClient()
    conn = get_connection()
    try:
        sync_from_github(client, conn)
    finally:
        conn.close()

if __name__ == "__main__":
    run_sync()
