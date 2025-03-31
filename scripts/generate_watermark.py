import os
from datetime import datetime
from pathlib import Path
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

# Directories
PROCESSED_DIR = Path("downloads/processed_videos")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Watermark Settings
WATERMARK_FONT = "Arial-Bold"
WATERMARK_FONT_SIZE = 36
WATERMARK_COLOR = "white"
WATERMARK_POSITION = ("left", "bottom")
WATERMARK_OPACITY = 0.6

def apply_watermark(input_path, output_path, watermark_text):
    print(f"🎬 Applying watermark to {input_path.name} → {output_path.name}")
    try:
        video = VideoFileClip(str(input_path))
        txt_clip = TextClip(watermark_text, fontsize=WATERMARK_FONT_SIZE,
                            font=WATERMARK_FONT, color=WATERMARK_COLOR, size=(video.w * 0.8, None), method='caption')
        txt_clip = txt_clip.set_position(WATERMARK_POSITION).set_duration(video.duration)
        final = CompositeVideoClip([video, txt_clip.set_opacity(WATERMARK_OPACITY)])
        final.write_videofile(str(output_path), codec="libx264", audio_codec="aac", preset="superfast", verbose=False, logger=None)
        print(f"✅ Watermarked video saved: {output_path}")
    except Exception as e:
        print(f"❌ Error applying watermark: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Input video file path")
    parser.add_argument("--category", required=True, help="Category for the video")
    args = parser.parse_args()

    input_video = Path(args.input)
    if not input_video.exists():
        raise FileNotFoundError(f"Input file not found: {input_video}")

    readable_category = args.category.replace("_", " ").title()
    output_filename = f"{args.category}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_wm.mp4"
    output_path = PROCESSED_DIR / output_filename

    apply_watermark(input_video, output_path, watermark_text=f"{readable_category} Compilation")
