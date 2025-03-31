import os
import json
import random
import logging
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# === Setup ===
THUMBNAIL_DIR = Path("downloads/thumbnails")
TEMPLATE_DIR = Path("assets/templates")
FONT_PATH = Path("assets/fonts/Arial_Bold.ttf")
IMAGE_SIZE = (1280, 720)
FONT_SIZE = 40
THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)

# Logging
logging.basicConfig(filename="logs/thumbnail_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

# === Category-Specific Colors ===
CATEGORY_COLORS = {
    "Fails": (255, 0, 0),
    "Awesome People": (0, 255, 0),
    "Cute Pets": (255, 192, 203),
    "Bad Drivers": (255, 165, 0),
    "Best Tool Reviews": (0, 191, 255),
    "Best Projects of the Week": (138, 43, 226),
    "Addon Reviews": (169, 169, 169)
}

def generate_title_with_ai(category, seed_keywords):
    use_gpt4all = os.environ.get("USE_GPT4ALL", "false").lower() == "true"
    prompt = f"Create a compelling YouTube thumbnail title for the category '{category}' using these keywords: {', '.join(seed_keywords)}"
    if use_gpt4all:
        try:
            from gpt4all import GPT4All
            gpt = GPT4All("ggml-gpt4all-j-v1.3-groovy")
            return gpt.prompt(prompt).strip()
        except Exception as e:
            logging.warning(f"⚠️ GPT fallback: {e}")
    return f"Top {category} Moments!"

def sanitize_filename(text):
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in text)

def generate_thumbnail(title, category):
    color = CATEGORY_COLORS.get(category, (255, 255, 255))
    template_path = TEMPLATE_DIR / f"{category.replace(' ', '_').lower()}.jpg"

    if template_path.exists():
        background = Image.open(template_path).resize(IMAGE_SIZE)
    else:
        background = Image.new("RGB", IMAGE_SIZE, color=color)

    draw = ImageDraw.Draw(background)
    try:
        font = ImageFont.truetype(str(FONT_PATH), FONT_SIZE)
    except Exception as e:
        logging.warning(f"⚠️ Font load failed: {e}")
        font = ImageFont.load_default()

    text_w, text_h = draw.textsize(title, font=font)
    text_position = ((IMAGE_SIZE[0] - text_w) // 2, (IMAGE_SIZE[1] - text_h) // 2)
    draw.text(text_position, title, fill="black", font=font)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{sanitize_filename(category)}_{timestamp}.jpg"
    output_path = THUMBNAIL_DIR / filename
    background.save(output_path)
    logging.info(f"✅ Thumbnail generated: {output_path}")
    return title, output_path

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", required=True, help="Video category")
    parser.add_argument("--keywords", nargs="*", default=[], help="Seed keywords for title")
    args = parser.parse_args()

    title = generate_title_with_ai(args.category, args.keywords)
    _, output = generate_thumbnail(title, args.category)
    print(f"✅ Generated thumbnail at {output}")

