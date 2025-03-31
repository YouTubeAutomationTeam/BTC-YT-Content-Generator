# scripts/drive_sync.py

import subprocess
import json
import os
import logging

CONFIG_PATH = "config/storage_config.json"

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def run_gdrive_command(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {' '.join(command)}\n{e.stderr}")
        return None

def find_or_create_folder(name, parent_id):
    # Search for folder with given name under parent
    query = f"name = '{name}' and '{parent_id}' in parents and mimeType = 'application/vnd.google-apps.folder'"
    result = run_gdrive_command(["gdrive", "files", "list", "--query", query, "--skip-header"])

    if result and result.strip():
        return result.split()[0]  # First column is ID

    # Create folder if not found (using upload as folder with --type folder)
    result = run_gdrive_command([
        "gdrive", "files", "upload",
        "--name", name,
        "--type", "folder",
        "--parent", parent_id
    ])

    if result:
        # Usually returns something like: "Uploaded file 1AbcXYZ"
        parts = result.strip().split()
        if "Uploaded" in result and "file" in result:
            return parts[-1]  # The ID is usually the last word
    return None

def upload_file(file_path, parent_id):
    result = run_gdrive_command(["gdrive", "files", "upload", "--parent", parent_id, file_path])
    if result:
        logging.info(f"✅ Uploaded: {file_path}")
    else:
        logging.error(f"❌ Failed to upload: {file_path}")

def sync_folder(local_base, remote_base_folder_id):
    if not remote_base_folder_id:
        logging.error(f"🚫 Cannot sync '{local_base}' — remote folder ID is missing.")
        return

    for root, _, files in os.walk(local_base):
        for file in files:
            local_file_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_file_path, local_base)
            parts = relative_path.split(os.sep)

            current_parent_id = remote_base_folder_id

            # Create subfolder structure
            for part in parts[:-1]:  # skip actual file
                folder_id = find_or_create_folder(part, current_parent_id)
                if not folder_id:
                    logging.error(f"❌ Could not create/find subfolder: {part}")
                    break
                current_parent_id = folder_id

            upload_file(local_file_path, current_parent_id)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    config = load_config()
    gdrive = config.get("gdrive")
    provider = config.get("provider")

    if provider != "gdrive":
        logging.error("❌ Unsupported storage provider.")
        exit(1)

    root_id = gdrive["root_folder_id"]

    folder_keys = [
        "clip_folder",
        "full_videos_folder",
        "metadata_folder",
        "thumbnails_folder",
        "compiled_videos_folder",
        "processed_videos_folder",
        "watermark_folder"
    ]

    # Example: loop through all local folders and sync if they exist
    for folder_key in folder_keys:
        local_folder = gdrive.get(folder_key)
        if local_folder and os.path.exists(local_folder):
            logging.info(f"📤 Syncing local folder '{local_folder}' to GDrive")
            remote_folder_id = find_or_create_folder(local_folder, root_id)
            sync_folder(local_folder, remote_folder_id)
