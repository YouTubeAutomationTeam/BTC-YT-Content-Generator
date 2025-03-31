#!/bin/bash

ZIP_NAME="youtube_automation_scripts.zip"

echo "📦 Zipping scripts into: $ZIP_NAME"

zip -r $ZIP_NAME \
  scripts/ \
  config/ \
  workflow_manager.py \
  main.py \
  .gitignore \
  requirements.txt \
  main.yml \
  README.md \
  project_structure.txt \
  cleanup_project.sh \
  --exclude "*.env" \
  "AUTH/**" \
  "downloads/**" \
  "archive/**" \
  "*.mp4" "*.webm" "*.jpg" "*.png" "*.json" "*.ytdl" \
  ".venv/**" "venv/**" \
  "*.DS_Store" \
  "*.txt" \
  "__pycache__/**"

echo "✅ Archive created: $ZIP_NAME"
