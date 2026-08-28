import logging
import json
from data_pipeline.api_client import FootballDataClient
from data_pipeline.database import get_connection, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def sync_competitions(client, conn):
    COMPETITION = "PL"
    
    # Fetch Teams
    data = client.get(f"competitions/{COMPETITION}/teams")
    if not data:
        return
        
    cursor = conn.cursor()
    for team in data.get('teams', []):
        cursor.execute('''
            INSERT OR REPLACE INTO teams (id, name, short_name, tla, raw_json)
            VALUES (?, ?, ?, ?, ?)
        ''', (team['id'], team['name'], team.get('shortName'), team.get('tla'), json.dumps(team)))
        
        # Insert Squad
        for player in team.get('squad', []):
            cursor.execute('''
                INSERT OR REPLACE INTO players (id, name, team_id, position, date_of_birth, nationality, raw_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (player['id'], player['name'], team['id'], player.get('position'), player.get('dateOfBirth'), player.get('nationality'), json.dumps(player)))
            
    conn.commit()
    logger.info("Teams and Players synced.")
    
    # Fetch Matches
    matches_data = client.get(f"competitions/{COMPETITION}/matches")
    if not matches_data:
        return
        
    for match in matches_data.get('matches', []):
        score = match.get('score', {}).get('fullTime', {})
        cursor.execute('''
            INSERT OR REPLACE INTO matches (id, competition_id, utc_date, status, matchday, home_team_id, away_team_id, home_goals, away_goals, raw_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            match['id'], match['competition']['id'], match['utcDate'], match['status'], match.get('matchday'),
            match['homeTeam']['id'], match['awayTeam']['id'],
            score.get('home'), score.get('away'), json.dumps(match)
        ))
    
    conn.commit()
    logger.info("Matches synced.")

def run_sync():
    init_db()
    client = FootballDataClient()
    conn = get_connection()
    try:
        sync_competitions(client, conn)
    finally:
        conn.close()

if __name__ == "__main__":
    run_sync()
