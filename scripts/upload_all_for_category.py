import os
import sys
import subprocess
import json
import logging
import argparse
from scripts.thumbnail_generator import generate_thumbnail

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

CONFIG_PATH = "config/storage_config.json"
import os
print("🧪 DEBUG: Current Working Directory:", os.getcwd())
print("🧪 DEBUG: scripts/ directory contents:", os.listdir(os.path.join(os.getcwd(), "scripts")))

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def run_gdrive_command(command, cwd=None):
    cwd = cwd or os.getcwd()  # fallback if not passed
    print(f"🧪 Running command in directory: {cwd}")
    result = subprocess.run(command, capture_output=True, text=True, check=True, cwd=cwd)
    print(f"✅ Output:\n{result.stdout}")
    print(f"⚠️ Errors (if any):\n{result.stderr}")
    return result

def get_or_create_remote_folder(folder_name, parent_id):
    """Checks if a folder exists in GDrive; creates it if missing."""
    query = f"name = '{folder_name}' and '{parent_id}' in parents and mimeType = 'application/vnd.google-apps.folder'"
    output = run_gdrive_command(["gdrive", "files", "list", "--query", query, "--skip-header"])

    if output:
        return output.split()[0]

    os.makedirs("temp_category_folders", exist_ok=True)
    result = run_gdrive_command(["gdrive", "files", "create", "--name", folder_name, "--parent", parent_id, "--type", "folder"])
    if result:
        return result.split()[1]  # Assuming result contains ID second
    return None

def upload_folder(local_path, remote_folder_id):
    if not os.path.exists(local_path):
        logging.warning(f"⚠️ Local path does not exist: {local_path}")
        return
    files = os.listdir(local_path)
    for file in files:
        file_path = os.path.join(local_path, file)
        if os.path.isfile(file_path):
            run_gdrive_command(["gdrive", "files", "upload", "--parent", remote_folder_id, file_path])

def process_category(category_name):
    """Uploads all assets for a single category to Google Drive."""
    logging.info(f"🚀 Uploading all assets for category: {category_name}")
    config = load_config()

    # === Thumbnail Generation and Upload ===
    try:
        from scripts.thumbnail_generator import create_thumbnail
        from scripts.upload_thumbnails import upload_thumbnail_to_drive

        thumbnail_path = create_thumbnail(category_name, seed_keywords=["highlight", "viral", "clip"])
        upload_thumbnail_to_drive(thumbnail_path, category_name)
        logging.info(f"🖼️ Thumbnail generated and uploaded for {category_name}")
    except Exception as e:
        logging.warning(f"⚠️ Thumbnail generation/upload failed for {category_name}: {str(e)}")

    root_id = config["gdrive"]["root_folder_id"]
    gdrive_cfg = config["gdrive"]

    folders = {
        "metadata": f"downloads/metadata/{category_name}/compilations",
        "thumbnails": f"downloads/thumbnails/{category_name}",
        "watermarks": f"downloads/watermarks/{category_name}",
        "compiled_videos": f"downloads/compiled_videos/{category_name}"
    }

    for key, local_path in folders.items():
        remote_root_name = gdrive_cfg.get(f"{key}_folder")
        if not remote_root_name:
            logging.error(f"❌ No config entry for key: {key}")
            continue

        remote_root_id = get_or_create_remote_folder(remote_root_name, root_id)
        remote_category_id = get_or_create_remote_folder(category_name, remote_root_id)

        if remote_category_id:
            upload_folder(local_path, remote_category_id)
        else:
            logging.error(f"❌ Could not create/find remote folder for: {category_name}")

# === CLI Entry Point ===
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", required=True, help="Category name (e.g., Cute Pets)")
    args = parser.parse_args()
    process_category(args.category)
