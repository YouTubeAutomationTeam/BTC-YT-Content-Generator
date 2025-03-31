import os
import json
import logging
import subprocess
import shutil

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
        return output.split()[0]
    return None

def create_remote_folder(name, parent_id):
    # Use temp dir creation + --recursive for gdrive v3
    temp_path = os.path.join("temp_compiled", name)
    os.makedirs(temp_path, exist_ok=True)
    open(os.path.join(temp_path, ".gitkeep"), "w").close()  # dummy file to ensure folder isn't empty

    result = run_gdrive_command([
        "gdrive", "files", "upload", "--parent", parent_id, "--recursive", temp_path
    ])

    shutil.rmtree(temp_path, ignore_errors=True)

    if result:
        # parse and return the folder ID (usually second field)
        return result.split()[0]
    return None

def get_or_create_remote_folder(name, parent_id):
    folder_id = get_folder_id(name, parent_id)
    if folder_id:
        return folder_id

    temp_path = os.path.join("temp_compiled", name)
    os.makedirs(temp_path, exist_ok=True)
    dummy_file = os.path.join(temp_path, ".gitkeep")
    open(dummy_file, "w").close()

    result = run_gdrive_command([
        "gdrive", "files", "upload", "--parent", parent_id, "--recursive", temp_path
    ])
    shutil.rmtree(temp_path, ignore_errors=True)

    if result:
        # Safely search for a line that looks like a file/folder ID
        for line in result.splitlines():
            parts = line.strip().split()
            if len(parts) >= 2 and parts[0] != "Found":
                return parts[0]  # First token should be folder ID
    return None

def upload_compiled_videos(local_root, remote_root_id):
    for category in os.listdir(local_root):
        category_path = os.path.join(local_root, category)
        if not os.path.isdir(category_path):
            continue

        logging.info(f"📁 Uploading compiled videos for category: {category}")

        remote_category_id = get_or_create_remote_folder(category, remote_root_id)
        if not remote_category_id:
            logging.error(f"❌ Could not create/find remote folder for: {category}")
            continue

        for file in os.listdir(category_path):
            if not file.lower().endswith((".mp4", ".mov", ".avi", ".mkv")):
                continue

            file_path = os.path.join(category_path, file)
            logging.info(f"📤 Uploading: {file}")
            result = run_gdrive_command(["gdrive", "files", "upload", "--parent", remote_category_id, file_path])
            if result:
                logging.info(f"✅ Uploaded: {file}")
            else:
                logging.error(f"❌ Failed to upload: {file}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    config = load_config()
    root_id = config["gdrive"]["root_folder_id"]
    compiled_folder_name = config["gdrive"]["compiled_videos_folder"]

    local_compiled_path = os.path.join("downloads", compiled_folder_name)
    if not os.path.exists(local_compiled_path):
        logging.error(f"Local folder not found: {local_compiled_path}")
        exit(1)

    remote_compiled_root_id = get_or_create_remote_folder(compiled_folder_name, root_id)
    if not remote_compiled_root_id:
        logging.error("❌ Could not get or create root remote folder for compiled videos.")
        exit(1)

    upload_compiled_videos(local_compiled_path, remote_compiled_root_id)
