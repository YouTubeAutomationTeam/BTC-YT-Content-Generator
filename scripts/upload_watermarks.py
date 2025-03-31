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

def create_folder_on_gdrive(name, parent_id):
    existing_id = get_folder_id(name, parent_id)
    if existing_id:
        return existing_id
    temp_path = os.path.join("temp_folders", name)
    os.makedirs(temp_path, exist_ok=True)
    run_gdrive_command([
        "gdrive", "files", "upload",
        "--mime", "application/vnd.google-apps.folder",
        "--parent", parent_id,
        "--recursive",
        temp_path
    ])
    return get_folder_id(name, parent_id)

def upload_watermarks():
    logging.info("🚀 Uploading watermarks to GDrive...")
    config = load_config()
    root_id = config["gdrive"]["root_folder_id"]
    watermarks_root = config["gdrive"]["watermark_folder"]

    watermark_root_id = create_folder_on_gdrive(watermarks_root, root_id)
    local_root = os.path.join("downloads", watermarks_root)

    for category in os.listdir(local_root):
        category_path = os.path.join(local_root, category)
        if not os.path.isdir(category_path):
            continue

        logging.info(f"📁 Uploading watermarks for category: {category}")
        remote_category_id = create_folder_on_gdrive(category, watermark_root_id)

        for file in os.listdir(category_path):
            file_path = os.path.join(category_path, file)
            if os.path.isfile(file_path):
                result = run_gdrive_command(["gdrive", "files", "upload", "--parent", remote_category_id, file_path])
                if result:
                    logging.info(f"✅ Uploaded: {file}")
                else:
                    logging.error(f"❌ Failed to upload: {file}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    os.makedirs("temp_folders", exist_ok=True)
    upload_watermarks()
