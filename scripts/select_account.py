import os
import json
import base64
from config_manager import ACCOUNT_MAP

USAGE_TRACK_FILE = "logs/account_usage_log.json"
TOKEN_DIR = "AUTH/tokens"
MAX_RECENT = 4  # Avoid reusing the last N accounts
TOKEN_PREFIX = "B64_OAUTH_TOKEN_PICKLE_"

def load_usage():
    if os.path.exists(USAGE_TRACK_FILE):
        with open(USAGE_TRACK_FILE, "r") as f:
            return json.load(f)
    return []

def save_usage(used_accounts):
    with open(USAGE_TRACK_FILE, "w") as f:
        json.dump(used_accounts[-(MAX_RECENT + 1):], f)

def decode_and_store_token(env_var_name, account_id):
    token_b64 = os.getenv(env_var_name)
    if not token_b64:
        print(f"⚠️ Skipping '{account_id}' — env var '{env_var_name}' not found.")
        return False

    os.makedirs(TOKEN_DIR, exist_ok=True)
    token_output_path = os.path.join(TOKEN_DIR, f"oauth_token_{account_id}.pickle")
    try:
        with open(token_output_path, "wb") as f:
            f.write(base64.b64decode(token_b64))
        print(f"✅ Token written for '{account_id}' → {token_output_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to decode or write token for '{account_id}': {e}")
        return False

def select_account():
    token_names_env = os.getenv("TOKEN_NAMES", "")
    valid_tokens = token_names_env.strip().split()

    print("🔍 Raw TOKEN_NAMES from ENV:")
    print(token_names_env)
    print("🔍 Parsed valid_tokens list:")
    print(valid_tokens)

    if not valid_tokens:
        raise RuntimeError("❌ No TOKEN_NAMES provided in environment.")

    # Show what the expected token names are based on ACCOUNT_MAP
    expected_tokens = [f"{TOKEN_PREFIX}{val.upper()}" for val in ACCOUNT_MAP.values()]
    print("🧩 Expected TOKEN names from ACCOUNT_MAP:")
    print(expected_tokens)

    available_accounts = [
        key for key, val in ACCOUNT_MAP.items()
        if f"{TOKEN_PREFIX}{val.upper()}" in valid_tokens
    ]

    print("🟢 Matched available_accounts:")
    print(available_accounts)

    if not available_accounts:
        raise RuntimeError("❌ No matching token names found for any ACCOUNT_MAP entries.")

    used_accounts = load_usage()
    recent = used_accounts[-MAX_RECENT:]
    print(f"🕒 Recently used accounts (last {MAX_RECENT}): {recent}")

    unused_accounts = [acc for acc in available_accounts if acc not in recent]
    print("📤 Unused accounts from matched pool:")
    print(unused_accounts)

    candidate_pool = unused_accounts or available_accounts
    selected_account = sorted(candidate_pool)[0]
    used_accounts.append(selected_account)
    save_usage(used_accounts)

    env_key = ACCOUNT_MAP[selected_account].upper()
    token_env_var = f"{TOKEN_PREFIX}{env_key}"
    if not decode_and_store_token(token_env_var, selected_account):
        raise ValueError(f"❌ Unable to use selected account '{selected_account}'. No valid token found.")

    print(f"🎯 Using account: {selected_account}")

if __name__ == "__main__":
    select_account()
