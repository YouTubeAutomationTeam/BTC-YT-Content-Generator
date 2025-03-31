import os
import random
import logging
import json
from datetime import datetime
from pathlib import Path
from moviepy.editor import VideoFileClip, concatenate_videoclips

# === Paths & Configs ===
CLIPS_DIR = Path("downloads/clips")
OUTPUT_DIR = Path("downloads/processed_videos")
LOGS_DIR = Path("logs")
HISTORY_FILE = LOGS_DIR / "clip_usage_history.json"
COMPOSITION_HISTORY_FILE = LOGS_DIR / "video_clip_compositions.json"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# === Logging ===
logging.basicConfig(
    filename=LOGS_DIR / "video_processor_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# === Duration Constraints ===
MIN_DURATION = 600  # 10 minutes
MAX_DURATION = 1800  # 30 minutes
RECENT_VIDEO_WINDOW = 15
MAX_REPEATED_GROUP_CLIPS = 3


# === Clip History ===
def load_usage_history():
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_usage_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def update_clip_history(used_clips, history):
    for clip in used_clips:
        history.setdefault(clip, []).append(len(history.get(clip, [])) + 1)
    save_usage_history(history)


# === Composition Grouping History ===
def load_compositions():
    if COMPOSITION_HISTORY_FILE.exists():
        with open(COMPOSITION_HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_composition(clip_names):
    compositions = load_compositions()
    compositions.append(clip_names)
    with open(COMPOSITION_HISTORY_FILE, "w") as f:
        json.dump(compositions[-RECENT_VIDEO_WINDOW:], f, indent=2)  # Keep recent only


def is_clip_usable(clip_name, history, recent_limit=RECENT_VIDEO_WINDOW):
    if clip_name not in history:
        return True
    recent_count = len(history[clip_name][-recent_limit:])
    return recent_count < recent_limit


def has_repeated_grouping(candidate_clips, past_compositions):
    for comp in past_compositions:
        overlap = len(set(comp) & set(candidate_clips))
        if overlap > MAX_REPEATED_GROUP_CLIPS:
            return True
    return False


# === Load & Filter ===
def load_clip_metadata(category_dir):
    metadata_path = category_dir / "clip_metadata.json"
    if metadata_path.exists():
        with open(metadata_path, "r") as f:
            return json.load(f)
    return {}

def load_clips(category: str):
    category_dir = CLIPS_DIR / category
    if not category_dir.exists():
        raise FileNotFoundError(f"Category folder not found: {category_dir}")

    metadata = load_clip_metadata(category_dir)
    video_files = list(category_dir.glob("*.mp4"))
    if not video_files:
        raise ValueError(f"No video clips found in {category_dir}")

    filtered = [vf for vf in video_files if metadata.get(vf.name, {}).get("category") == category]
    if not filtered:
        raise ValueError(f"No matching clips with correct metadata found for category: {category}")
    return filtered


# === Compile Clips into Video ===
def compile_clips(video_files):
    history = load_usage_history()
    past_compositions = load_compositions()

    clips = []
    used_clips = []
    total_duration = 0

    for file in video_files:
        if not is_clip_usable(file.name, history):
            continue

        try:
            clip = VideoFileClip(str(file))
            clip_duration = clip.duration

            if total_duration + clip_duration > MAX_DURATION:
                continue

            clips.append(clip)
            used_clips.append(file.name)
            total_duration += clip_duration

            if MIN_DURATION <= total_duration <= MAX_DURATION:
                break

        except Exception as e:
            logging.warning(f"⚠️ Skipping corrupt clip {file.name}: {e}")

    if total_duration < MIN_DURATION:
        raise RuntimeError(f"Final video too short: {total_duration/60:.1f} minutes. Minimum is 10.")

    if has_repeated_grouping(used_clips, past_compositions):
        raise RuntimeError("🚫 Too many previously grouped clips reused together. Skipping.")

    update_clip_history(used_clips, history)
    save_composition(used_clips)

    return concatenate_videoclips(clips, method="compose"), used_clips


# === Save Final Video ===
def save_compilation(category: str, final_clip, used_clips):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = OUTPUT_DIR / f"{category.replace(' ', '_').lower()}_compilation_{timestamp}.mp4"
    final_clip.write_videofile(str(output_path), codec="libx264", audio_codec="aac")
    logging.info(f"✅ Video saved: {output_path}")
    logging.info(f"🎞️ Clips used: {used_clips}")


# === Run Processing ===
def process_category(category: str):
    logging.info(f"🎬 Processing category: {category}")
    video_files = load_clips(category)
    random.shuffle(video_files)
    final_clip, used_clips = compile_clips(video_files)
    save_compilation(category, final_clip, used_clips)


# === Entry Point ===
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", required=True, help="Video category to process")
    args = parser.parse_args()

    try:
        process_category(args.category)
    except Exception as e:
        logging.error(f"💥 Processing failed: {e}")
