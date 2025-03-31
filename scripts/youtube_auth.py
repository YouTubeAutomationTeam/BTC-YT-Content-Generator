# youtube_auth.py

import os
import pickle
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from googleapiclient.discovery import build

# Scopes for YouTube Data API usage
YOUTUBE_SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

# Resolve token path from env or default
TOKEN_PATH = Path(os.environ.get("TOKEN_PATH", "AUTH/tokens"))
TOKEN_PATH.mkdir(parents=True, exist_ok=True)

def get_youtube_service(creds):
    return build("youtube", "v3", credentials=creds)

def get_token_file(account_name: str, token_type: str = "oauth") -> Path:
    suffix = "oauth_token" if token_type == "oauth" else "service_token"
    return TOKEN_PATH / f"{account_name}_{suffix}.pickle"

def load_oauth_token(account_name: str) -> Credentials:
    """Load and refresh an OAuth token."""
    token_file = get_token_file(account_name, "oauth")
    if not token_file.exists():
        raise FileNotFoundError(f"OAuth token for {account_name} not found: {token_file}")

    with open(token_file, "rb") as f:
        creds = pickle.load(f)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_file, "wb") as f:
            pickle.dump(creds, f)

    if not creds.valid:
        raise RuntimeError(f"OAuth credentials for {account_name} are invalid even after refresh.")

    return creds

def load_service_token(account_name: str) -> ServiceAccountCredentials:
    """Load and validate a service account token."""
    token_file = get_token_file(account_name, "service")
    if not token_file.exists():
        raise FileNotFoundError(f"Service token for {account_name} not found: {token_file}")

    with open(token_file, "rb") as f:
        creds = pickle.load(f)

    if not creds.valid:
        raise RuntimeError(f"Service account credentials for {account_name} are invalid.")

    return creds

def validate_token(token_file: Path) -> str:
    """Validate a given token and refresh if needed."""
    try:
        with open(token_file, "rb") as f:
            creds = pickle.load(f)

        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_file, "wb") as f:
                pickle.dump(creds, f)
            return f"✅ Token refreshed: {token_file.name}"
        elif creds.valid:
            return f"🟢 Token is still valid: {token_file.name}"
        else:
            return f"❌ Invalid token or missing refresh: {token_file.name}"
    except Exception as e:
        return f"💥 Error validating {token_file.name}: {e}"

def validate_all_tokens():
    print("\n🔍 Validating all available tokens...")
    if not TOKEN_PATH.exists():
        print("⚠️ No token folder found.")
        return

    for token_file in TOKEN_PATH.glob("*.pickle"):
        print(validate_token(token_file))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-tokens", action="store_true", help="Validate and refresh all YouTube tokens")
    args = parser.parse_args()

    if args.validate_tokens:
        validate_all_tokens()
    else:
        parser.print_help()
