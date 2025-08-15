import os
import requests

MURF_API_KEY = os.getenv("MURF_API_KEY")
MURF_VOICE_ID = os.getenv("MURF_VOICE_ID", "en-IN-rohan")
MURF_URL = "https://api.murf.ai/v1/speech/generate"

def text_to_speech(text: str) -> str:
    """
    Returns Murf-hosted audio URL.
    Murf has a ~3000 char limit; truncate to be safe.
    """
    if not MURF_API_KEY:
        raise RuntimeError("MURF_API_KEY not set.")
    if not text:
        text = "I'm having trouble connecting right now."

    if len(text) > 3000:
        text = text[:3000]

    headers = {"api-key": MURF_API_KEY, "Content-Type": "application/json"}
    payload = {"voiceId": MURF_VOICE_ID, "text": text}

    r = requests.post(MURF_URL, headers=headers, json=payload)
    if not r.ok:
        raise RuntimeError(f"Murf API error: {r.status_code} {r.text}")
    data = r.json()
    return data.get("audioFile")
