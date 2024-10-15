import requests
import time
import csv
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from requests.exceptions import RequestException

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Constants
api_key = os.getenv("ODDS_API_KEY", "your_api_key_here")
sport_key = "soccer_uefa_nations_league"
api_url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds"
fetch_interval_minutes = 1

def fetch_games(max_retries: int = 3, delay: int = 5) -> Optional[List[Dict]]:
    """
    Fetches the latest game data from the Odds API.
    """
    params = {
        "apiKey": api_key,
        "regions": "eu",
        "markets": "h2h"
    }
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(api_url, params=params)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            logging.error(f"Request error: {e}")
            retries += 1
            time.sleep(delay)
    logging.error("Max retries reached. Failed to fetch data.")
    return None

def track_odds(game: Dict) -> List[Dict]:
    """
    Extracts and tracks the odds data for a specific game.
    """
    odds_data = []
    current_time = datetime.now()
   
    for bookmaker in game.get("bookmakers", []):
        for market in bookmaker.get("markets", []):
            if market.get("key") == "h2h":
                for outcome in market.get("outcomes", []):
                    odds_data.append({
                        "id": game["id"],
                        "home_team": game["home_team"],
                        "away_team": game["away_team"],
                        "time": current_time.isoformat(),
                        "bookmaker": bookmaker["title"],
                        "team": outcome["name"],
                        "odds": outcome["price"]
                    })
    return odds_data

def save_to_csv(data: List[Dict], filename: str = "odds_data.csv") -> None:
    """
    Saves the odds data to a CSV file.
    """
    fieldnames = ["id", "home_team", "away_team", "time", "bookmaker", "team", "odds"]
    file_exists = os.path.exists(filename)
    
    with open(filename, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerows(data)

def get_time_to_sleep(fetch_interval: int) -> float:
    """
    Calculates the time to sleep until the next interval.
    """
    next_interval = (datetime.now() + timedelta(minutes=fetch_interval)).replace(second=0, microsecond=0)
    return (next_interval - datetime.now()).total_seconds()

# Main loop
def main():
    while True:
        games = fetch_games()
        if games:
            for game in games:
                odds_data = track_odds(game)
                save_to_csv(odds_data)
                
                # Update the terminal message
                logging.info(f"Odds saved from {game['home_team']} vs {game['away_team']} on {datetime.now().isoformat()}")
        
        sleep_time = get_time_to_sleep(fetch_interval_minutes)
        time.sleep(sleep_time)

if __name__ == "__main__":
    main()
