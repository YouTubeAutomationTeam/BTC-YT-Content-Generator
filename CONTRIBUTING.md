# 🤝 Contributing to BTC-YT-Content-Generator

Thank you for considering contributing to the BTC-YT-Content-Generator project! This system automates YouTube content creation, leveraging AI and Google APIs with a modular, secure design.

## 🚀 Getting Started

1. **Fork the repository**
2. **Clone your fork**  
   ```bash
   git clone https://github.com/your-username/BTC-YT-Content-Generator.git
   cd BTC-YT-Content-Generator
   ```

3. **Set up a virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Create a new branch**
   ```bash
   git checkout -b your-feature-name
   ```

## 📂 Project Structure

Keep all changes modular:
- Scripts go under `scripts/`
- Secrets are never committed.
- Logs go to `logs/` (gitignored)

## ✅ Coding Guidelines
- Use `snake_case` for Python files and functions.
- Include docstrings and inline comments.
- Write reusable, testable functions.
- Run linting: `flake8 scripts/`

## 🧪 Testing
Before submitting a PR, ensure your changes don’t break the automation workflow:
```bash
python scripts/main.py --dry-run
```

## 📝 Submitting a Pull Request

1. Ensure your branch is up to date:
   ```bash
   git pull origin main
   ```
2. Push your feature branch:
   ```bash
   git push origin your-feature-name
   ```
3. Open a pull request from your fork.

---

Thanks for helping BTC Media Labs build this incredible project! 🚀
```

---
