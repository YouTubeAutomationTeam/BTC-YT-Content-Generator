import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

# === Load environment variables ===
load_dotenv()

# === Logging Setup ===
LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"
os.makedirs(LOGS_DIR, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(LOGS_DIR, "config_manager_log.txt"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# === Configuration Paths ===
CONFIG_PATH = "config/config.json"
API_INDEX_TRACKER = Path("logs/api_key_index.json")

# === Mapping Loader ===
def load_mappings():
    with open("config/channel_mapping.json") as f:
        return json.load(f)

# Load mappings globally
mappings = load_mappings()
CATEGORY_CHANNEL_MAP = mappings.get("CATEGORY_CHANNEL_MAP", {})
CHANNEL_ACCOUNT_MAP = mappings.get("CHANNEL_ACCOUNT_MAP", {})
CHANNEL_ID_MAP = mappings.get("CHANNEL_ID_MAP", {})
ACCOUNT_MAP = mappings.get("ACCOUNT_MAP", {})

# === Token Helper Functions ===
def get_token_for_channel(channel_name):
    account = CHANNEL_ACCOUNT_MAP.get(channel_name)
    return ACCOUNT_MAP.get(account, {}).get("token")

def get_channel_for_category(category):
    return CATEGORY_CHANNEL_MAP.get(category)

def get_channel_id(channel_name):
    return CHANNEL_ID_MAP.get(channel_name)

def get_account_for_channel(channel_name):
    return CHANNEL_ACCOUNT_MAP.get(channel_name)

def get_account_for_category(category):
    channel = get_channel_for_category(category)
    return get_account_for_channel(channel)

def get_api_key_for_account(account_name):
    return ACCOUNT_MAP.get(account_name, {}).get("api_key")

def get_upload_url_for_account(account_name):
    return ACCOUNT_MAP.get(account_name, {}).get("upload_url")

def get_proxy_for_account(account_name):
    return ACCOUNT_MAP.get(account_name, {}).get("proxy")

def get_client_secret_for_account(account_name):
    return ACCOUNT_MAP.get(account_name, {}).get("client_secret")

def get_oauth_credentials_path(account_name):
    return ACCOUNT_MAP.get(account_name, {}).get("oauth_credentials")

def get_refresh_token_for_account(account_name):
    return ACCOUNT_MAP.get(account_name, {}).get("refresh_token")

def get_access_token_for_account(account_name):
    return ACCOUNT_MAP.get(account_name, {}).get("access_token")

def rotate_api_key():
    if not API_INDEX_TRACKER.exists():
        with open(API_INDEX_TRACKER, "w") as f:
            json.dump({"index": 0}, f)

    with open(API_INDEX_TRACKER) as f:
        index_data = json.load(f)

    keys = [acc["api_key"] for acc in ACCOUNT_MAP.values() if acc.get("api_key")]
    if not keys:
        logging.error("❌ No API keys found in ACCOUNT_MAP.")
        return None

    current_index = index_data.get("index", 0)
    selected_key = keys[current_index % len(keys)]

    # Update index
    index_data["index"] = (current_index + 1) % len(keys)
    with open(API_INDEX_TRACKER, "w") as f:
        json.dump(index_data, f)

    logging.info(f"🔁 Rotated API key: Index {index_data['index']}")
    return selected_key

def get_proxy_rotation_list():
    return [acc.get("proxy") for acc in ACCOUNT_MAP.values() if acc.get("proxy")]

def get_valid_upload_accounts():
    return [acc for acc in ACCOUNT_MAP if ACCOUNT_MAP[acc].get("upload_enabled", True)]

def get_channel_proxy(channel_name):
    account = get_account_for_channel(channel_name)
    return get_proxy_for_account(account)

def get_channel_token(channel_name):
    account = get_account_for_channel(channel_name)
    return get_token_for_channel(account)

def get_all_channel_names():
    return list(CHANNEL_ID_MAP.keys())

def get_all_categories():
    return list(CATEGORY_CHANNEL_MAP.keys())

def get_channel_credentials(channel_name):
    account = get_account_for_channel(channel_name)
    return {
        "token": get_token_for_channel(channel_name),
        "proxy": get_proxy_for_account(account),
        "api_key": get_api_key_for_account(account),
        "client_secret": get_client_secret_for_account(account),
        "refresh_token": get_refresh_token_for_account(account),
        "upload_url": get_upload_url_for_account(account),
        "oauth_credentials": get_oauth_credentials_path(account),
        "access_token": get_access_token_for_account(account)
    }

# === Storage Config Loader ===
def load_storage_config():
    try:
        with open("config/storage_config.json") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"❌ Failed to load storage_config.json: {str(e)}")
        return {}

def validate_storage_config(required_keys=None):
    config = load_storage_config()
    missing_keys = []

    if required_keys:
        for key in required_keys:
            if key not in config:
                missing_keys.append(key)

    if missing_keys:
        logging.warning(f"⚠️ Missing required keys in storage config: {missing_keys}")
    else:
        logging.info("✅ All required storage config keys are present.")

    return len(missing_keys) == 0
