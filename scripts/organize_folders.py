import os
from pathlib import Path
import shutil
import json

CATEGORIES = [
    "Awesome People",
    "Fails",
    "Cute Pets",
    "Bad Drivers",
    "Best Tool Reviews",
    "Best Projects of the Week",
    "Addon Reviews"
]

# Main directory layout
REQUIRED_DIRS = [
    "downloads/full_videos",
    "downloads/clips",
    "downloads/metadata",
    "downloads/thumbnails",
    "downloads/processed_videos",
    "logs",
    "AUTH/credentials",
    "AUTH/tokens",
    "assets/video_sources",
    "output"
]

# Create all base folders
for base in REQUIRED_DIRS:
    Path(base).mkdir(parents=True, exist_ok=True)

# Create category subfolders
for cat in CATEGORIES:
    safe_cat = cat.replace(" ", "_").lower()
    Path(f"downloads/full_videos/{safe_cat}").mkdir(parents=True, exist_ok=True)
    Path(f"downloads/clips/{safe_cat}").mkdir(parents=True, exist_ok=True)
    Path(f"downloads/metadata/{safe_cat}").mkdir(parents=True, exist_ok=True)
    Path(f"downloads/thumbnails/{safe_cat}").mkdir(parents=True, exist_ok=True)

print("✅ Folder structure created.")

# Optional: Migrate stray clips or videos from old flat structure
old_clips_path = Path("downloads/clips")
if any(file.is_file() and file.suffix == ".mp4" for file in old_clips_path.iterdir()):
    backup_path = Path("archive/flat_clips_backup")
    backup_path.mkdir(parents=True, exist_ok=True)
    for file in old_clips_path.glob("*.mp4"):
        print(f"📦 Moving stray clip: {file.name} → {backup_path}")
        shutil.move(str(file), backup_path / file.name)

# Optional: Backup old thumbnails, metadata, etc.
def backup_flat_files(folder, ext):
    flat_files = Path(folder)
    if not flat_files.exists():
        return
    for f in flat_files.glob(f"*.{ext}"):
        archive_dir = Path(f"archive/flat_{flat_files.name}_{ext}s")
        archive_dir.mkdir(parents=True, exist_ok=True)
        print(f"📦 Archiving {f.name} to {archive_dir}")
        shutil.move(str(f), archive_dir / f.name)

backup_flat_files("downloads/thumbnails", "jpg")
backup_flat_files("downloads/metadata", "json")
backup_flat_files("downloads/full_videos", "mp4")

print("✅ Flat files (if any) were archived without loss.")
