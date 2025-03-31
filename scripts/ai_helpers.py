import os
import requests
import logging

# Optional Local AI
try:
    from gpt4all import GPT4All
    USE_GPT4ALL = os.environ.get("USE_GPT4ALL", "false").lower() == "true"
    if USE_GPT4ALL:
        gpt4all_model = GPT4All("mistral-7b-instruct-v0.1.Q4_0.gguf")
    else:
        gpt4all_model = None
except ImportError:
    USE_GPT4ALL = False
    gpt4all_model = None

# === API Keys ===
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
HUGGINGFACE_API_KEY = os.environ.get("HUGGINGFACE_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

HEADERS_OPENAI = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json"
} if OPENAI_API_KEY else {}

HEADERS_HUGGINGFACE = {
    "Authorization": f"Bearer {HUGGINGFACE_API_KEY}"
} if HUGGINGFACE_API_KEY else {}

HEADERS_GEMINI = {
    "Content-Type": "application/json",
    "x-goog-api-key": GEMINI_API_KEY
} if GEMINI_API_KEY else {}

# === Logging ===
logging.basicConfig(
    filename="logs/ai_helpers_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def generate_text(prompt: str, category: str = "general") -> str:
    """Generate text using the best available AI source."""

    # --- 1. OpenAI ---
    if OPENAI_API_KEY:
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=HEADERS_OPENAI,
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant for YouTube video automation."},
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logging.warning(f"OpenAI fallback: {e}")

    # --- 2. Gemini ---
    if GEMINI_API_KEY:
        try:
            gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
            body = {"contents": [{"parts": [{"text": prompt}]}]}
            response = requests.post(gemini_url, headers=HEADERS_GEMINI, json=body)
            response.raise_for_status()
            content = response.json()
            return content["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            logging.warning(f"Gemini fallback: {e}")

    # --- 3. HuggingFace ---
    if HUGGINGFACE_API_KEY:
        try:
            HF_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"
            response = requests.post(HF_URL, headers=HEADERS_HUGGINGFACE, json={"inputs": prompt}, timeout=10)
            response.raise_for_status()
            result = response.json()
            if isinstance(result, list) and result:
                return result[0].get("generated_text", prompt).strip()
            return result.get("generated_text", prompt).strip()
        except Exception as e:
            logging.warning(f"HuggingFace fallback: {e}")

    # --- 4. GPT4All ---
    if gpt4all_model:
        try:
            return gpt4all_model.generate(prompt, max_tokens=200).strip()
        except Exception as e:
            logging.warning(f"GPT4All fallback error: {e}")

    logging.error("All AI services failed. Returning raw prompt.")
    return f"[FAILED] {prompt}"  # Slightly clearer return in failure cases

if __name__ == "__main__":
    sample_prompt = "Generate a compelling YouTube video title for a 'Fails Compilation' using the keywords: epic, hilarious, compilation."
    print("🧠 AI Output:", generate_text(sample_prompt, category="Fails"))
