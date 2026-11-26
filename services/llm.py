import json
import time
from google import genai
from google.genai import types
from config import Config

client = genai.Client(api_key=Config.GEMINI_API_KEY)

# Pehle behtar models, busy hone par halke (lite) models par chale jao.
MODEL_CHAIN = [
    "gemini-3.8-flash",
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite",
]


def generate_text(prompt, temperature=0.5, json_mode=False, rounds=2, wait=5):
    """Models ko ek ek karke try karta hai. Kamyab hone par text, warna None."""
    config_kwargs = {"temperature": temperature}
    if json_mode:
        config_kwargs["response_mime_type"] = "application/json"

    last_error = None
    for round_no in range(rounds):
        for model in MODEL_CHAIN:
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(**config_kwargs),
                )
                text = (response.text or "").strip()
                if text:
                    print(f"[LLM] answered by {model}")
                    return text
            except Exception as e:
                last_error = e
                print(f"[LLM] {model} failed: {str(e)[:100]}")
        if round_no < rounds - 1:
            time.sleep(wait)

    print("[LLM] all models failed:", last_error)
    return None


def parse_json(raw):
    """Gemini ke jawab se JSON nikalta hai (markdown fences ho to hata deta hai)."""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1].strip()
        if raw.lower().startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())