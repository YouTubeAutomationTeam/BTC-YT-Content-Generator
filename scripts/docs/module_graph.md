# 📦 YouTube Automation Module Graph

This document tracks module interactions and validation progress for the full system.

## 🔁 Data Flow

```mermaid
flowchart TD
    main[main.py] --> scraper[youtube_scraper.py]
    main --> processor[video_processor.py]
    processor --> thumbnail[thumbnail_generator.py]
    processor --> watermark[generate_watermark.py]
    main --> metadata[metadata_generator.py]
    main --> uploader[youtube_uploader.py]
    uploader --> auth[youtube_auth.py]
    select[select_account.py] --> auth
