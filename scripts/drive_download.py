# scripts/drive_download.py

import os
import json
import logging
import subprocess
import shlex


CONFIG_PATH = "config/storage_config.json"

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def run_gdrive_command(command, cwd=None):
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, cwd=cwd)
        return result.stdout
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {' '.join(command)}\n{e.stderr}")
        return None

def get_folder_id(name, parent_id):
    query = f"name = '{name}' and '{parent_id}' in parents and mimeType = 'application/vnd.google-apps.folder'"
    output = run_gdrive_command(["gdrive", "files", "list", "--query", query, "--skip-header"])
    if output:
        return output.split()[0]
    return None

def download_files(remote_folder_name, local_folder_name):
    logging.info(f"📥 Syncing GDrive → Local for folder: {remote_folder_name}")
    config = load_config()
    root_id = config["gdrive"]["root_folder_id"]
    parent_id = get_folder_id(remote_folder_name, root_id)

    if not parent_id:
        logging.error(f"❌ Could not find remote folder: {remote_folder_name}")
        return

    os.makedirs(local_folder_name, exist_ok=True)

    # Use only supported flags
    output = run_gdrive_command([
        "gdrive", "files", "list",
        "--parent", parent_id,
        "--skip-header"
    ])
    if not output:
        logging.warning("⚠️ No files found to download.")
        return

    for line in output.splitlines():
        parts = shlex.split(line)
        if len(parts) < 3:
            continue

        file_id = parts[0]
        name = " ".join(parts[1:-1])
        file_type = parts[-1]

        if file_type == "folder":
            logging.info(f"📁 Skipping folder: {name}")
            continue

        local_file_path = os.path.join(local_folder_name, name)
        if os.path.exists(local_file_path):
            logging.warning(f"⚠️ Skipping existing file: {local_file_path}")
            continue

        result = run_gdrive_command(["gdrive", "files", "download", file_id], cwd=local_folder_name)
        if result:
            logging.info(f"✅ Downloaded: {name}")
        else:
            logging.error(f"❌ Failed to download: {name}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Example usage: download everything from specific GDrive folders
    folders_to_download = ["metadata", "thumbnails", "watermarks"]  # Add more if needed

    for folder in folders_to_download:
        download_files(folder, os.path.join("downloads", folder))
