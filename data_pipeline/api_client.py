import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenFootballClient:
    """
    Fetches open-source football data directly from public GitHub repositories.
    No API keys required.
    """
    def __init__(self):
        self.session = requests.Session()
        
    def get_matches_from_github(self, year="2023-24", league="en.1"):
        """Fetches English Premier League (or other) match data from openfootball github."""
        url = f"https://raw.githubusercontent.com/openfootball/football.json/master/{year}/{league}.json"
        try:
            logger.info(f"Fetching open-source match data from GitHub: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch GitHub data: {e}")
            return None
