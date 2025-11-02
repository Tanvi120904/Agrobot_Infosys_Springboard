import os
import json
import difflib
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# ----------------------- Imports -----------------------
try:
    from langdetect import detect, DetectorFactory
    DetectorFactory.seed = 0
    HAS_LANGDETECT = True
except ImportError:
    HAS_LANGDETECT = False

# Google Translator (optional)
try:
    from googletrans import Translator
    TRANSLATOR = Translator()
    HAS_GOOGLETRANS = True
except Exception:
    TRANSLATOR = None
    HAS_GOOGLETRANS = False

# OpenAI setup
try:
    from openai import OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
    HAS_OPENAI = client is not None
except Exception:
    client = None
    HAS_OPENAI = False

# ----------------------- Paths -----------------------
BASE_DIR = os.path.dirname(__file__)
KB_PATH = os.path.join(BASE_DIR, "kb.json")

# ----------------------- Load Knowledge Base -----------------------
def load_kb() -> Dict[str, Dict[str, str]]:
    """Load knowledge base from JSON file"""
    if not os.path.exists(KB_PATH):
        print("⚠️ KB file not found:", KB_PATH)
        return {}

    try:
        with open(KB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print("⚠️ Invalid KB JSON format.")
        return {}

    out = {}
    if isinstance(data, list):
        for entry in data:
            keys = entry.get("keywords") or []
            if isinstance(keys, str):
                keys = [k.strip() for k in keys.split(",") if k.strip()]
            for k in keys:
                out[k.lower()] = {
                    "en": entry.get("answer_en", ""),
                    "hi": entry.get("answer_hi", ""),
                    "ta": entry.get("answer_ta", "")
                }

    elif isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, str):
                out[k.lower()] = {"en": v}
            elif isinstance(v, dict):
                out[k.lower()] = {
                    "en": v.get("answer_en", ""),
                    "hi": v.get("answer_hi", ""),
                    "ta": v.get("answer_ta", "")
                }
    return out


KB = load_kb()

# ----------------------- Language Utilities -----------------------
def detect_language(text: str) -> str:
    """Detect the language of input text"""
    if not HAS_LANGDETECT:
        return "en"
    try:
        return detect(text)
    except Exception:
        return "en"


def translate_text(text: str, dest: str) -> str:
    """Translate text to target language"""
    if not HAS_GOOGLETRANS or not TRANSLATOR:
        return text
    try:
        return TRANSLATOR.translate(text, dest=dest[:2]).text
    except Exception:
        return text


# ----------------------- KB Search -----------------------
def find_in_kb(message: str):
    """Search KB using exact and fuzzy match"""
    m = message.lower()
    best_match = None
    highest_ratio = 0.0

    for k, v in KB.items():
        if k in m:  # direct match
            return v
        ratio = difflib.SequenceMatcher(None, k, m).ratio()
        if ratio > highest_ratio:
            highest_ratio = ratio
            best_match = v

    # Accept fuzzy matches only if reasonably close
    if highest_ratio > 0.55:
        return best_match
    return None


# ----------------------- OpenAI Fallback -----------------------
def openai_fallback(user_profile: Dict[str, Any], message_text: str, target_lang: str = "en") -> str:
    """Use OpenAI GPT model if KB has no answer"""
    if not HAS_OPENAI or not client:
        return ""

    try:
        prompt = (
            f"You are an expert agronomist. "
            f"User profile: {user_profile}\n"
            f"Question: {message_text}\n"
            f"Answer concisely and factually."
        )

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an experienced agronomist assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=250,
        )

        text = resp.choices[0].message.content.strip()
        if target_lang != "en" and HAS_GOOGLETRANS:
            text = translate_text(text, target_lang)
        return text

    except Exception as e:
        print("⚠️ OpenAI Error:", e)
        return ""


# ----------------------- Message Processor -----------------------
def process_message(user_profile: Dict[str, Any], message_text: str) -> str:
    """Main chatbot function: checks KB → then GPT → else fallback message"""
    if not message_text or not message_text.strip():
        return "Please ask a question about crops, soil, or pests."

    detected = detect_language(message_text)

    # Translate to English if not English
    english_text = message_text
    if detected != "en" and HAS_GOOGLETRANS:
        english_text = translate_text(message_text, "en")

    # Step 1: Search Knowledge Base
    kb_item = find_in_kb(english_text)
    if kb_item:
        lang = (user_profile.get("preferred_language") or detected or "en")[:2]
        ans = kb_item.get(lang) or kb_item.get("en") or ""
        if not ans and kb_item.get("en") and lang != "en" and HAS_GOOGLETRANS:
            ans = translate_text(kb_item.get("en"), lang)
        return ans

    # Step 2: Fallback to OpenAI
    if HAS_OPENAI:
        resp = openai_fallback(
            user_profile or {},
            english_text,
            target_lang=(user_profile.get("preferred_language") or detected or "en")[:2],
        )
        if resp:
            return resp

    # Step 3: Default fallback
    return "I don't have that answer in KB. Try asking about a specific crop or pest."


# ----------------------- Debug -----------------------
if __name__ == "__main__":
    profile = {"name": "Farmer", "preferred_language": "en"}
    while True:
        q = input("Ask: ")
        if q.lower() in ["exit", "quit"]:
            break
        print("Bot:", process_message(profile, q))
