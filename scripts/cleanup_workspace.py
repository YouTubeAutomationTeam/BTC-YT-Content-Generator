import os
import shutil
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# Define root structure
BASE_DOWNLOADS = "downloads"
EXPECTED_FOLDERS = ["clips", "full_videos", "metadata", "thumbnails", "processed_videos"]

# 1. Validate & fix structure
def validate_structure():
    for folder in EXPECTED_FOLDERS:
        path = os.path.join(BASE_DOWNLOADS, folder)
        if not os.path.exists(path):
            os.makedirs(path)
            logging.info(f"✅ Created missing folder: {path}")
        else:
            logging.info(f"🗂️ Folder OK: {path}")

# 2. Remove duplicate or misplaced folders
def remove_unexpected_folders():
    for item in os.listdir(BASE_DOWNLOADS):
        path = os.path.join(BASE_DOWNLOADS, item)
        if os.path.isdir(path) and item not in EXPECTED_FOLDERS:
            confirm = input(f"❌ Delete unexpected folder '{item}'? [y/N]: ").strip().lower()
            if confirm == "y":
                shutil.rmtree(path)
                logging.info(f"🧹 Deleted: {path}")

# 3. Identify unused full videos
def find_unused_full_videos():
    full_video_dir = os.path.join(BASE_DOWNLOADS, "full_videos")
    processed_dir = os.path.join(BASE_DOWNLOADS, "processed_videos")

    used_files = set()
    for video_file in os.listdir(processed_dir):
        if video_file.endswith(".mp4"):
            used_files.add(video_file)

    flagged = []
    for category in os.listdir(full_video_dir):
        cat_path = os.path.join(full_video_dir, category)
        if os.path.isdir(cat_path):
            for video in os.listdir(cat_path):
                if video.endswith(".mp4") and video not in used_files:
                    full_path = os.path.join(cat_path, video)
                    flagged.append(full_path)

    logging.info(f"📦 Found {len(flagged)} full videos not used in processed videos.")
    return flagged

# 4. Run cleanup sequence
def run_cleanup():
    print("\n🔧 Validating folder structure...")
    validate_structure()

    print("\n🧼 Checking for unexpected folders...")
    remove_unexpected_folders()

    print("\n🕵️‍♂️ Searching for unused full videos...")
    unused = find_unused_full_videos()
    if unused:
        print(f"\n⚠️ These videos are unused:")
        for vid in unused:
            print(f" - {vid}")
        confirm = input("\n🗑️ Do you want to delete these? [y/N]: ").strip().lower()
        if confirm == "y":
            for vid in unused:
                os.remove(vid)
                logging.info(f"Deleted unused video: {vid}")
    else:
        print("✅ No unused videos found.")

if __name__ == "__main__":
    run_cleanup()
