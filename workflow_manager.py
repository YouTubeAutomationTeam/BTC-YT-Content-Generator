import os
import sys
import logging
import subprocess
import time  # Add missing import

# Set the project root dynamically
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Ensure the 'scripts' directory is added to the Python path
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, "scripts")
sys.path.insert(0, SCRIPTS_DIR)  # Use `insert(0, ...)` to prioritize it

# Now import the necessary scripts
from scripts.config_manager import load_config
from scripts.logging_manager import setup_logging
from scripts.schedule_manager import load_schedule
from scripts.thumbnail_generator import generate_thumbnail
from scripts.video_processor import process_video
from scripts.youtube_auth import authenticate_youtube
from scripts.youtube_scraper import scrape_videos
from scripts.youtube_uploader import upload_all_videos

# Versioning
SCRIPT_VERSION = "1.0.1"

# Define logs directory
LOGS_DIR = "logs"
os.makedirs(LOGS_DIR, exist_ok=True)

# Logging setup
LOG_FILE = os.path.join(LOGS_DIR, "workflow_manager_log.txt")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Workflow execution sequence
WORKFLOW_STEPS = [
    ("Load Configuration", "python scripts/config_manager.py"),
    ("Setup Logging", "python scripts/logging_manager.py"),
    ("Authenticate YouTube Account", "python scripts/youtube_auth.py"),
    ("Retrieve Scheduled Uploads", "python scripts/schedule_manager.py"),
    ("Scrape YouTube Data", "python scripts/youtube_scraper.py"),
    ("Process Videos", "python scripts/video_processor.py"),
    ("Generate Thumbnails", "python scripts/thumbnail_generator.py"),
    ("Upload Videos to YouTube", "python scripts/youtube_uploader.py"),
]

def execute_step(step_name, command):
    """Executes a given step and handles errors."""
    print(f"🚀 Starting: {step_name}...")
    logging.info(f"Starting: {step_name}")

    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        logging.info(f"✅ {step_name} completed successfully.")
        print(f"✅ {step_name} completed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ ERROR in {step_name}: {e.stderr}")
        print(f"❌ ERROR in {step_name}: {e.stderr}")

        # Retry Logic
        for attempt in range(1, 4):
            print(f"🔄 Retrying {step_name} (Attempt {attempt}/3)...")
            logging.warning(f"Retrying {step_name} (Attempt {attempt}/3)...")
            time.sleep(5)

            try:
                subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
                logging.info(f"✅ {step_name} succeeded on retry {attempt}.")
                print(f"✅ {step_name} succeeded on retry {attempt}.")
                return
            except subprocess.CalledProcessError as retry_e:
                logging.error(f"❌ Retry {attempt} failed: {retry_e.stderr}")
                print(f"❌ Retry {attempt} failed: {retry_e.stderr}")

        print(f"🚨 Critical Failure: {step_name} could not be completed after 3 retries.")
        logging.critical(f"Critical Failure: {step_name} could not be completed after 3 retries.")

def run_workflow():
    """Executes the full workflow in sequence."""
    print(f"🚀 Running Workflow Manager v{SCRIPT_VERSION}")
    logging.info(f"Running Workflow Manager v{SCRIPT_VERSION}")

    for step_name, command in WORKFLOW_STEPS:
        execute_step(step_name, command)

    print("🎉 Workflow execution completed!")
    logging.info("Workflow execution completed!")

if __name__ == "__main__":
    run_workflow()
