# scripts/upload_metadata.py

import os
import json
import logging
import subprocess

CONFIG_PATH = "config/storage_config.json"

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def run_gdrive_command(command, cwd=None):
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, cwd=cwd)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {' '.join(command)}\n{e.stderr}")
        return None

def get_folder_id(name, parent_id):
    query = f"name = '{name}' and '{parent_id}' in parents and mimeType = 'application/vnd.google-apps.folder'"
    output = run_gdrive_command(["gdrive", "files", "list", "--query", query, "--skip-header"])
    if output:
        return output.split()[0]  # ID is always first
    return None

def create_folder_on_gdrive(name, parent_id):
    existing_id = get_folder_id(name, parent_id)
    if existing_id:
        return existing_id

    # Create a temporary local folder to trigger GDrive's folder behavior
    temp_folder_path = os.path.join("temp_folders", name)
    os.makedirs(temp_folder_path, exist_ok=True)

    result = run_gdrive_command([
        "gdrive", "files", "upload",
        "--recursive",
        "--parent", parent_id,
        temp_folder_path
    ])

    # Clean up temp folder
    try:
        os.rmdir(temp_folder_path)
    except Exception as e:
        logging.warning(f"⚠️ Could not delete temp folder {temp_folder_path}: {e}")

    if result:
        return result.split()[0]  # Folder ID is the first token
    return None

def upload_json_files(local_folder, remote_parent_id):
    for filename in os.listdir(local_folder):
        if filename.endswith(".json"):
            filepath = os.path.join(local_folder, filename)
            logging.info(f"📤 Uploading: {filepath}")
            output = run_gdrive_command(["gdrive", "files", "upload", filepath, "--parent", remote_parent_id])
            if output:
                logging.info(f"✅ Uploaded: {filename}")
            else:
                logging.error(f"❌ Failed to upload: {filename}")

def upload_all_metadata():
    logging.info("🚀 Uploading metadata to GDrive...")
    config = load_config()
    root_id = config["gdrive"]["root_folder_id"]
    metadata_folder_name = config["gdrive"]["metadata_folder"]

    metadata_root_id = create_folder_on_gdrive(metadata_folder_name, root_id)
    if not metadata_root_id:
        logging.error("❌ Could not create/find remote metadata root folder.")
        return

    local_metadata_root = os.path.join("downloads", metadata_folder_name)
    if not os.path.isdir(local_metadata_root):
        logging.error(f"❌ Local folder does not exist: {local_metadata_root}")
        return

    for category_name in os.listdir(local_metadata_root):
        local_category_path = os.path.join(local_metadata_root, category_name)
        if not os.path.isdir(local_category_path):
            continue

        logging.info(f"📁 Processing category: {category_name}")
        category_remote_id = create_folder_on_gdrive(category_name, metadata_root_id)
        if category_remote_id:
            upload_json_files(local_category_path, category_remote_id)
        else:
            logging.error(f"❌ Could not create/find remote folder for: {category_name}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    upload_all_metadata()
