import os
import json
import logging
from pathlib import Path
from datetime import datetime
from pytube import YouTube, Search
from config_manager import get_scraped_videos, save_scraped_video, load_config

# === Paths ===
DOWNLOAD_DIR = Path("downloads/full_videos")
METADATA_LOG = Path("logs/clip_metadata.json")
LOG_FILE = Path("logs/scraper_log.txt")

# === Logging ===
Path("logs").mkdir(exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# === Load Config ===
config = load_config()
CATEGORY_QUERIES = config.get("search_queries", {})

# === Ensure folders ===
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# === Core Functions ===
def fetch_youtube_videos(category, limit=10):
    """Search and return YouTube video objects for a given category."""
    queries = CATEGORY_QUERIES.get(category, [])
    results = []
    for query in queries:
        try:
            search = Search(query)
            results.extend(search.results[:limit])
        except Exception as e:
            logging.warning(f"🔍 Search failed for query '{query}': {e}")
    return results[:limit]

def download_video(yt: YouTube, category: str, retries=3):
    """Download a YouTube video with retries and save its metadata."""
    video_id = yt.video_id
    filename = f"{video_id}.mp4"
    category_dir = DOWNLOAD_DIR / category
    category_dir.mkdir(parents=True, exist_ok=True)
    output_path = category_dir / filename

    if output_path.exists():
        logging.info(f"⚠️ Already downloaded: {filename}")
        return None

    for attempt in range(retries):
        try:
            stream = yt.streams.filter(file_extension='mp4', progressive=True).get_highest_resolution()
            stream.download(output_path=str(output_path))
            save_scraped_video(video_id)
            save_metadata(yt, category, str(output_path))
            logging.info(f"✅ Downloaded: {yt.title}")
            return str(output_path)
        except Exception as e:
            logging.warning(f"❌ Attempt {attempt+1} failed for {yt.watch_url}: {e}")

    logging.error(f"⛔ Giving up on download: {yt.watch_url}")
    return None

def save_metadata(yt: YouTube, category: str, file_path: str):
    """Save clip metadata to central metadata log."""
    clip_data = {
        "id": yt.video_id,
        "title": yt.title,
        "author": yt.author,
        "length": yt.length,
        "url": yt.watch_url,
        "downloaded_at": datetime.utcnow().isoformat(),
        "file_path": file_path,
        "category": category
    }

    if METADATA_LOG.exists():
        with open(METADATA_LOG, "r") as f:
            existing = json.load(f)
    else:
        existing = []

    existing.append(clip_data)

    with open(METADATA_LOG, "w") as f:
        json.dump(existing, f, indent=2)

def scrape_category(category: str, limit=10):
    logging.info(f"🔎 Scraping category: {category}")
    scraped_ids = get_scraped_videos()
    videos = fetch_youtube_videos(category, limit)

    for yt in videos:
        if yt.video_id in scraped_ids:
            logging.info(f"⏭️ Skipping duplicate: {yt.video_id}")
            continue
        download_video(yt, category)

# === CLI Entrypoint ===
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", required=True, help="Category to scrape videos for")
    parser.add_argument("--limit", type=int, default=10, help="Number of videos to fetch")
    args = parser.parse_args()

    try:
        scrape_category(args.category, args.limit)
    except Exception as e:
        logging.error(f"💥 Scraping failed: {e}")
