# main.py

import logging
from scripts import schedule_manager
from scripts.upload_all_for_category import process_category
from scripts.config_manager import get_channel_for_category

logging.basicConfig(
    filename="logs/script_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def main():
    categories = schedule_manager.get_today_categories()
    if not categories:
        logging.warning("📭 No categories scheduled for today.")
        return

    for category in categories:
        try:
            logging.info(f"🔁 Processing category: {category}")
            process_category(category)
        except Exception as e:
            logging.exception(f"❌ Error processing category {category}: {str(e)}")

if __name__ == "__main__":
    main()
