# 🚀 BTC-YT-Content-Generator

### Developed by BTC Media Labs — a division of Business Transformation Consulting LLC

---

## 🧠 Overview
**BTC-YT-Content-Generator** is an end-to-end automation system for discovering, compiling, branding, and uploading YouTube content. This solution uses AI for content classification, title/description/tag generation, thumbnail creation, and watermark branding — all integrated with Google Drive and YouTube APIs.

> ⚙️ Designed to run on macOS and optimized for 2017 MacBook Pro hardware constraints.

---

## ✨ Key Features

- 🔍 **Content Discovery** — Finds and classifies relevant videos by category.
- 🧠 **AI-Enhanced Metadata** — Titles, descriptions, and tags are generated using local and cloud-based AI.
- 🖼️ **Thumbnail & Watermark Generation** — Custom thumbnails and branded watermarks.
- 🎬 **Video Compilation** — Edits, trims, and compiles clips into final videos.
- 🔁 **Multi-Account Rotation** — Dynamically uses multiple YouTube accounts to avoid API limits.
- 📁 **Category-Channel Mapping** — Ensures uploads follow strict publishing guidelines.
- 💾 **Google Drive Integration** — Securely loads input files and metadata.
- ⚠️ **Robust Error Handling** — Logs failures, retries uploads, and handles failover paths.

---

## 🛠️ Local Installation Guide

### 1️⃣ Requirements
- macOS (tested on MacBook Pro 2017)
- Python 3.10+
- FFmpeg
- `gdrive3` binary
- Google OAuth credentials (see below)

### 2️⃣ Clone the Repo
```bash
git clone https://github.com/YourOrg/BTC-YT-Content-Generator.git
cd BTC-YT-Content-Generator
```

### 3️⃣ Setup Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4️⃣ Configure Credentials
- Place OAuth credentials in `AUTH/credentials/`
- Store `.pickle` or `.tar.gz` tokens in `AUTH/tokens/`
- Add GitHub Secrets using base64-encoded `.pickle` files:
  - `B64_GDRIVE_AUTH_PICKLE_<ACCOUNT>`

---

## 📂 Folder Structure
```bash
BTC-YT-Content-Generator/
├── AUTH/                # OAuth credentials & tokens
├── config/              # Config templates & constants
├── downloads/           # Raw video and metadata downloads
├── logs/                # Execution logs and error outputs
├── metadata/            # JSON metadata per video
├── scripts/             # Modular automation scripts
├── videos/              # Final rendered videos
├── .github/             # Actions workflows
├── README.md            # This file
├── LICENSE              # License and third-party acknowledgments
└── requirements.txt     # All required packages
```

---

## 🔄 GitHub Actions: Workflow Usage

### ✅ Automated Upload
```yml
main.yml → Runs full scraping → processing → AI → upload pipeline
```

### 🧪 Manual Category Upload
```bash
python scripts/upload_all_for_category.py --category "Fails"
```

---

## 🔐 Authentication Naming Conventions
| Component            | Naming Format                                 |
|----------------------|-----------------------------------------------|
| **Secrets**          | `B64_GDRIVE_AUTH_PICKLE_<ACCOUNT>`            |
| **Token File**       | `oauth_token_<account>.pickle`                |
| **Channel Map**      | Stored in `config/account_channel_map.json`   |

---

## 🤖 Technologies & Acknowledgments

This project integrates:
- `gdrive3` by [glotlabs/gdrive](https://github.com/glotlabs/gdrive) — for Google Drive CLI access
- `pytube`, `moviepy`, `opencv-python` — for video processing
- `openai`, `transformers`, `gpt4all` — for local and cloud-based AI
- `GitHub Actions` — for cloud automation & CI/CD

**BTC Media Labs** acknowledges the open-source community for the tools that make this possible.

---

## 📜 License
See [LICENSE](LICENSE) for commercial use terms under BTC LLC. Some components are used under their respective open-source licenses.

---

## 🤝 Contributing
We welcome contributions! See [`CONTRIBUTING.md`](CONTRIBUTING.md) for details.

---

## 🛡️ Security
To report a vulnerability or view policies, see [`SECURITY.md`](SECURITY.md).

---

## 🌐 Website (Coming Soon)
[https://BTCMediaLabs.com](https://BTCMediaLabs.com)

