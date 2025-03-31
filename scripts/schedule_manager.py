# schedule_manager.py

import json
from datetime import datetime
from pathlib import Path
import logging

LOG_FILE = Path("logs/schedule_log.txt")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

SCHEDULE_FILE = Path("config/schedule.json")

def load_schedule():
    """Loads the weekly publishing schedule from config."""
    if not SCHEDULE_FILE.exists():
        raise FileNotFoundError(f"❌ Schedule file not found: {SCHEDULE_FILE}")
    with open(SCHEDULE_FILE, "r") as f:
        return json.load(f)

def get_today_categories():
    """Returns list of categories scheduled for today."""
    today = datetime.now().strftime("%A")
    schedule = load_schedule()
    categories = schedule.get(today, [])
    logging.info(f"📅 Today is {today} — Categories scheduled: {categories}")
    return categories

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Get categories scheduled for today or a specific day.")
    parser.add_argument("--day", type=str, help="Override day (e.g., Monday, Tuesday)")
    args = parser.parse_args()

    schedule = load_schedule()
    day = args.day if args.day else datetime.now().strftime("%A")
    categories = schedule.get(day, [])
    print(f"📅 Categories for {day}: {categories}")
