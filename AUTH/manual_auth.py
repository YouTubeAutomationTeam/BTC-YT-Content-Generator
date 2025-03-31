import os
import pickle
import json
import random
import socket
import base64
import logging
import tarfile
from datetime import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import service_account

# ------------------------------------
# Constants and Paths
# ------------------------------------
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

TOKEN_DIR = os.path.abspath("AUTH/tokens/")
CREDENTIALS_DIR = os.path.abspath("AUTH/credentials/")
LOG_FILE = os.path.join("AUTH/logs", "auth.log")
AUTHORIZED_PORTS = [8080, 5000, 7070, 9000, 8888]
GDRIVE_CONFIG_PATH = os.path.expanduser("~/.config/gdrive3")
GDRIVE_OUTPUT_TAR = os.path.join(TOKEN_DIR, "gdrive_auth_token_alexbalmaseda.tar.gz")
GDRIVE_B64_OUTPUT = os.path.join(TOKEN_DIR, "B64_GDRIVE_AUTH_TOKEN_ALEXBALMASEDA.txt")
used_ports = set()

os.makedirs(TOKEN_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# ------------------------------------
# Logging Setup
# ------------------------------------
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

def log(msg):
    print(msg)
    logging.info(msg)

# ------------------------------------
# Utils
# ------------------------------------
def find_available_port():
    random.shuffle(AUTHORIZED_PORTS)
    for port in AUTHORIZED_PORTS:
        if port not in used_ports:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                if s.connect_ex(("localhost", port)) != 0:
                    used_ports.add(port)
                    return port
    raise RuntimeError("No available port found. Ensure no conflicts.")

def is_valid_token(token_path):
    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            creds = pickle.load(token)
        return creds and creds.valid
    return False

def save_base64_version(token_path, account_name, prefix):
    with open(token_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    b64_filename = f"B64_{prefix}_TOKEN_{account_name.upper()}.txt"
    b64_path = os.path.join(TOKEN_DIR, b64_filename)

    with open(b64_path, "w") as f_out:
        f_out.write(encoded)

    log(f"📦 Base64 token written: {b64_filename}")

# ------------------------------------
# Auth Flows
# ------------------------------------
def authenticate_with_oauth(credentials_file, account_name):
    token_path = os.path.join(TOKEN_DIR, f"oauth_token_{account_name}.pickle")
    if is_valid_token(token_path):
        log(f"✅ OAuth token for '{account_name}' is still valid.")
        return

    port = find_available_port()
    flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
    creds = flow.run_local_server(port=port)

    with open(token_path, "wb") as token:
        pickle.dump(creds, token)

    save_base64_version(token_path, account_name, "OAUTH")
    log(f"✅ OAuth authentication completed for: {account_name}")
    input("🌐 Close browser tab and press Enter to continue...")

def authenticate_with_service_account(service_file, account_name):
    token_path = os.path.join(TOKEN_DIR, f"service_token_{account_name}.pickle")
    if is_valid_token(token_path):
        log(f"✅ Service token for '{account_name}' is still valid.")
        return

    creds = service_account.Credentials.from_service_account_file(
        service_file, scopes=SCOPES
    )

    with open(token_path, "wb") as token:
        pickle.dump(creds, token)

    save_base64_version(token_path, account_name, "SERVICE")
    log(f"✅ Service account authentication completed for: {account_name}")

# ------------------------------------
# GDrive Auth Packaging
# ------------------------------------
def package_gdrive_auth():
    if not os.path.exists(GDRIVE_CONFIG_PATH):
        log(f"❌ GDrive config path not found: {GDRIVE_CONFIG_PATH}")
        return

    # Create .tar.gz of the entire config folder
    with tarfile.open(GDRIVE_OUTPUT_TAR, "w:gz") as tar:
        tar.add(GDRIVE_CONFIG_PATH, arcname="gdrive3")

    # Convert to base64
    with open(GDRIVE_OUTPUT_TAR, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    with open(GDRIVE_B64_OUTPUT, "w") as f_out:
        f_out.write(encoded)

    log(f"✅ GDrive auth packed and base64 saved to {GDRIVE_B64_OUTPUT}")

# ------------------------------------
# CLI Menu
# ------------------------------------
if __name__ == "__main__":
    print("📲 Manual Auth Tool (YouTube & GDrive)")
    while True:
        print("\nOptions:")
        print("1. Authenticate a YouTube account")
        print("2. Authenticate all predefined YouTube accounts")
        print("3. Package GDrive Auth")
        print("4. Exit")
        choice = input("Select an option (1/2/3/4): ").strip()

        if choice == "1":
            auth_type = input("Auth type (oauth/service): ").strip().lower()
            account = input("Account name (lowercase): ").strip()
            cred_path = input("Full path to credentials JSON: ").strip()

            if not os.path.exists(cred_path):
                log(f"❌ Invalid path: {cred_path}")
                continue

            if auth_type == "oauth":
                authenticate_with_oauth(cred_path, account)
            elif auth_type == "service":
                authenticate_with_service_account(cred_path, account)
            else:
                log("❌ Invalid type. Choose 'oauth' or 'service'.")

        elif choice == "2":
            accounts = {
                "alxwdwrx": "YOUTUBE_OAUTH_JSON_ALXWDWRX.json",
                "alexbalmaseda": "YOUTUBE_OAUTH_JSON_ALEXBALMASEDA.json",
                "btc": "YOUTUBE_OAUTH_JSON_BTC.json",
                "3kavey": "YOUTUBE_OAUTH_JSON_3KAVEY.json",
                "513mat": "YOUTUBE_OAUTH_JSON_513MAT.json",
                "lakecarmel": "YOUTUBE_OAUTH_JSON_LAKECARMEL.json"
            }

            for account, oauth_file in accounts.items():
                oauth_path = os.path.join(CREDENTIALS_DIR, oauth_file)
                service_path = oauth_path.replace("OAUTH", "SERVICE")

                log(f"\n🔁 Authenticating: {account}")
                if os.path.exists(oauth_path):
                    authenticate_with_oauth(oauth_path, account)
                else:
                    log(f"⚠️ OAuth file missing: {oauth_file}")
                if os.path.exists(service_path):
                    authenticate_with_service_account(service_path, account)
                else:
                    log(f"⚠️ Service file missing: {service_path}")

        elif choice == "3":
            package_gdrive_auth()

        elif choice == "4":
            log("👋 Exiting authentication tool.")
            break
        else:
            log("❌ Invalid option.")
