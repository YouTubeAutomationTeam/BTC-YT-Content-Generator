# 🎥 YouTube Content Automation Framework

## 🔧 Overview

This project is an end-to-end automation framework designed to collect, enhance, and publish curated YouTube content using AI. It enables creators and media teams to scale video operations efficiently across multiple channels using modular scripts, intelligent scheduling, and multi-account management.

> **Built and maintained by [BTC Digital Media](https://btcdigitalmedia.com), a division of Business Transformation Consulting LLC.**

---

## ✨ Key Features

- 📥 **Video Discovery & Scraping**
  - Automatically pulls trending or category-based videos from configured sources.

- ✂️ **Video Enhancement**
  - Auto-edits, trims, watermarks, and compiles video content.

- 🧠 **AI Metadata Optimization**
  - Uses GPT4All or OpenAI to generate titles, descriptions, and tags.

- 🖼️ **Thumbnail Generation**
  - Generates thumbnails using static templates or dynamic AI overlays.

- 🔄 **Multi-Channel Upload**
  - Uploads to mapped channels with category-to-channel rules.

- 📊 **Engagement Insights (Optional)**
  - Analyze CTR & retention (future enhancement).

---

## 📁 Folder Structure

```
YouTubeAutomation/
├── AUTH/             → Secure token & credential storage (gitignored)
├── config/           → Configuration files
├── metadata/         → Auto-generated metadata files
├── scripts/          → Modular pipeline scripts
├── videos/           → Processed and source videos
├── logs/             → Script logs
├── downloads/        → Scraped content (gitignored)
```

---

## 🚀 Quick Start

### 🛠️ Setup

```bash
git clone https://github.com/YouTubeAutomationTeam/btc-yt-content-generator.git
cd btc-yt-content-generator-core
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 🔐 Auth Configuration

- Add your token `.pickle` files to `AUTH/tokens/`
- Or load credentials securely via GitHub Secrets:
  - `B64_GDRIVE_AUTH_PICKLE_<ACCOUNTNAME>`
  - `B64_OAUTH_TOKEN_PICKLE_<ACCOUNTNAME>`

---

## 📜 License

This project is licensed under a **custom commercial license** by BTC Digital Media.  
Open-source components (see below) are used under their respective licenses.

---

## 📣 Attribution

This project leverages the following open-source tools:

| Tool / Lib       | License       | Link |
|------------------|---------------|------|
| `gdrive3`        | MIT           | https://github.com/glotlabs/gdrive |
| `moviepy`        | MIT           | https://github.com/Zulko/moviepy |
| `pytube`         | MIT           | https://github.com/pytube/pytube |
| `gpt4all`        | Apache-2.0    | https://github.com/nomic-ai/gpt4all |
| `transformers`   | Apache-2.0    | https://github.com/huggingface/transformers |

---

## 🤝 Contributions

We welcome contributions from the open-source community!

Please review the [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before submitting a PR.

---

## 🛡️ Security

See our [SECURITY.md](SECURITY.md) for guidelines on reporting vulnerabilities or concerns.

---

## 👥 Maintainers

Developed and maintained by **Alex Balmaseda** and the team at  
**BTC Digital Media** — a division of Business Transformation Consulting LLC.

---
