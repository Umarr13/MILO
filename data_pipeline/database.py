import sqlite3
import logging

logger = logging.getLogger(__name__)
DB_PATH = "milo.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Teams table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY,
        name TEXT,
        short_name TEXT,
        tla TEXT,
        raw_json TEXT
    )
    ''')
    
    # Players table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY,
        name TEXT,
        team_id INTEGER,
        position TEXT,
        date_of_birth TEXT,
        nationality TEXT,
        raw_json TEXT,
        FOREIGN KEY(team_id) REFERENCES teams(id)
    )
    ''')
    
    # Matches table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY,
        competition_id INTEGER,
        utc_date TEXT,
        status TEXT,
        matchday INTEGER,
        home_team_id INTEGER,
        away_team_id INTEGER,
        home_goals INTEGER,
        away_goals INTEGER,
        raw_json TEXT,
        FOREIGN KEY(home_team_id) REFERENCES teams(id),
        FOREIGN KEY(away_team_id) REFERENCES teams(id)
    )
    ''')
    
    # Player Stats table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS player_stats (
        player_id INTEGER,
        season TEXT,
        goals INTEGER DEFAULT 0,
        assists INTEGER DEFAULT 0,
        minutes_played INTEGER DEFAULT 0,
        appearances INTEGER DEFAULT 0,
        FOREIGN KEY(player_id) REFERENCES players(id),
        PRIMARY KEY(player_id, season)
    )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database schema initialized.")

if __name__ == "__main__":
    init_db()
