import os
import time
import requests
import logging
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
BASE_URL = "https://api.football-data.org/v4"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FootballDataClient:
    def __init__(self, api_key=API_KEY):
        self.api_key = api_key
        self.headers = {"X-Auth-Token": self.api_key}
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.last_request_time = 0
        self.rate_limit_delay = 6.0  # 10 requests per minute = 1 request every 6 seconds

    def _wait_for_rate_limit(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()

    def get(self, endpoint, params=None):
        url = f"{BASE_URL}/{endpoint}"
        self._wait_for_rate_limit()
        
        try:
            logger.info(f"Fetching data from {endpoint}")
            response = self.session.get(url, params=params)
            
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                logger.warning(f"Rate limited. Retrying after {retry_after} seconds.")
                time.sleep(retry_after)
                return self.get(endpoint, params)
                
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API Request failed: {e}")
            return None
