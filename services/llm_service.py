import os
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
MODEL = genai.GenerativeModel("gemini-1.5-flash")

def _build_prompt_from_history(history, new_user_text: str, max_messages: int = 12) -> str:
    """
    history: list of {"role": "user"/"assistant", "content": "..."}
    """
    trimmed = history[-max_messages:] if history else []
    parts = []
    for m in trimmed:
        role = "User" if m["role"] == "user" else "Assistant"
        parts.append(f"{role}: {m['content']}")
    parts.append(f"User: {new_user_text}")
    parts.append("Assistant:")
    return "\n".join(parts)

def generate_ai_response(history, user_text: str) -> str:
    if not GEMINI_API_KEY:
        # helpful fallback if key is missing
        return "I couldn't reach the language model because API key is missing."
    prompt = _build_prompt_from_history(history, user_text)
    resp = MODEL.generate_content(prompt)
    return (resp.text or "").strip()
