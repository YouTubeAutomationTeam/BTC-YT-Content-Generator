import os
import json
import time
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from youtube_auth import load_oauth_token
from config_manager import get_channel_for_category, get_upload_category_config

# Constants
UPLOAD_DIR = Path("downloads/processed_videos")
METADATA_DIR = Path("downloads/metadata")
THUMBNAIL_DIR = Path("downloads/thumbnails")
WATERMARK_DIR = Path("downloads/watermarks")

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

RETRIES = 3
RETRY_DELAY = 5

def upload_video(account_name, file_path, metadata_path, thumbnail_path=None):
    creds = load_oauth_token(account_name)
    youtube = build("youtube", "v3", credentials=creds)

    with open(metadata_path, "r") as f:
        metadata = json.load(f)

    body = {
        "snippet": {
            "title": metadata["title"],
            "description": metadata["description"],
            "tags": metadata.get("tags", []),
            "categoryId": metadata.get("categoryId", "22")
        },
        "status": {
            "privacyStatus": metadata.get("privacyStatus", "private"),
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(file_path, resumable=True, chunksize=-1)

    request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media
    )

    response = None
    for attempt in range(RETRIES):
        try:
            print(f"🚀 Uploading: {file_path.name} (Attempt {attempt+1})")
            status, response = request.next_chunk()
            if "id" in response:
                print(f"✅ Upload successful: https://youtube.com/watch?v={response['id']}")
                break
        except HttpError as e:
            print(f"⚠️ Upload failed on attempt {attempt+1}: {e}")
            time.sleep(RETRY_DELAY)
    else:
        print("❌ Upload failed after retries.")

def find_assets(video_file):
    stem = video_file.stem
    metadata = METADATA_DIR / f"{stem}.json"
    thumbnail = THUMBNAIL_DIR / f"{stem}.jpg"
    return metadata, thumbnail if thumbnail.exists() else None

def upload_all_processed():
    for video_file in UPLOAD_DIR.glob("*.mp4"):
        category = video_file.name.split("_")[0]
        channel_name = get_channel_for_category(category)
        account_name = channel_name.lower()

        metadata_file, thumbnail_file = find_assets(video_file)

        if not metadata_file.exists():
            print(f"⚠️ Skipping {video_file.name}: Metadata file not found.")
            continue

        upload_video(account_name, video_file, metadata_file, thumbnail_file)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--upload-all", action="store_true", help="Upload all processed videos")
    args = parser.parse_args()

    if args.upload_all:
        upload_all_processed()
