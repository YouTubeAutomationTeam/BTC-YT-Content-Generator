import os

# Define all essential directories for the project
REQUIRED_DIRECTORIES = [
    "logs",
    "downloads",
    "metadata",
    "videos",
    "AUTH/logs",
    "AUTH/tokens",
    "AUTH/credentials",
    "config",
]

# .gitkeep files to preserve empty folders in version control
GITKEEP_FILE = ".gitkeep"

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"📁 Created: {path}")
    else:
        print(f"✅ Exists: {path}")

    # Create .gitkeep in each dir (to preserve it in Git if needed)
    gitkeep_path = os.path.join(path, GITKEEP_FILE)
    if not os.path.exists(gitkeep_path):
        open(gitkeep_path, "w").close()
        print(f"📝 Added .gitkeep in: {path}")

def main():
    print("🔧 Initializing workspace...")
    for directory in REQUIRED_DIRECTORIES:
        create_directory(directory)
    print("✅ Workspace is ready!")

if __name__ == "__main__":
    main()
