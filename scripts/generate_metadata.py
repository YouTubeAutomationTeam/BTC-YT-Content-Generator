import os
import json
import random
import logging
from datetime import datetime
from pathlib import Path
from ai_helpers import generate_text  # 🧠 Unified AI fallback

# Optional: fallback to config templates
try:
    from scripts.config_manager import get_upload_category_config
except ImportError:
    get_upload_category_config = None

# === Logging Setup ===
LOG_FILE = Path("logs/metadata_generation_log.txt")
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# === Metadata Output Directory Base ===
METADATA_DIR = Path("downloads/metadata")

# === Default Tag Dictionary (for hard fallback) ===
DEFAULT_TAGS = {
    "Fails": ["funny", "fails", "epic", "failarmy"],
    "Awesome People": ["amazing", "talent", "incredible", "world record"],
    "Cute Pets": ["cute", "puppies", "kittens", "adorable", "funny pets"],
    "Bad Drivers": ["dashcam", "road rage", "bad drivers", "reckless"],
    "Best Tool Reviews": ["tools", "DIY", "reviews", "power tools"],
    "Best Projects of the Week": ["projects", "DIY", "engineering", "design"],
    "Addon Reviews": ["wow", "addons", "gaming", "mods"]
}


def generate_metadata(category, clip_titles):
    """Creates metadata using AI with fallback and saves to correct path."""
    safe_category = category.replace(" ", "_").lower()
    category_folder = METADATA_DIR / safe_category / "compilations"
    category_folder.mkdir(parents=True, exist_ok=True)

    prompt = (
        f"Write a compelling YouTube title, description, and tags for a compilation video "
        f"in the category '{category}' using these clip topics: {', '.join(clip_titles)}.\n\n"
        f"Return a JSON with fields: title, description, tags (list)."
    )

    try:
        result = generate_text(prompt)
        metadata = json.loads(result)

        if not all(k in metadata for k in ("title", "description", "tags")):
            raise ValueError("Incomplete metadata structure from AI.")

        if isinstance(metadata["tags"], str):
            metadata["tags"] = [tag.strip() for tag in metadata["tags"].split(",") if tag.strip()]

        logging.info(f"✅ AI-generated metadata for category: {category}")

    except Exception as e:
        logging.warning(f"⚠️ AI fallback triggered: {e}")
        config = get_upload_category_config(category) if get_upload_category_config else {}

        metadata = {
            "title": config.get("title_template", f"Best of {category} Compilation"),
            "description": config.get("description_template", f"Enjoy this collection of amazing {category.lower()} moments!"),
            "tags": config.get("tags", DEFAULT_TAGS.get(category, []))
        }

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_category}_{timestamp}.json"
    output_path = category_folder / filename

    with open(output_path, "w") as f:
        json.dump(metadata, f, indent=2)

    logging.info(f"📄 Metadata saved to: {output_path}")
    print(f"✅ Metadata saved: {output_path}")
    return output_path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--category", required=True, help="Video category")
    parser.add_argument("--clips", nargs="*", help="List of clip titles")
    args = parser.parse_args()

    if not args.clips:
        logging.warning(f"No clip titles provided for category: {args.category}")

    generate_metadata(args.category, args.clips or [])
