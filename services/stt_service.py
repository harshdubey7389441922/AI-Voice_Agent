import os
import time
import requests

ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")

UPLOAD_URL = "https://api.assemblyai.com/v2/upload"
TRANSCRIPT_URL = "https://api.assemblyai.com/v2/transcript"

def _upload_file(file_path: str) -> str:
    headers = {
        "authorization": ASSEMBLYAI_API_KEY,
        "content-type": "application/octet-stream"
    }
    with open(file_path, "rb") as f:
        r = requests.post(UPLOAD_URL, headers=headers, data=f)
    if not r.ok:
        raise RuntimeError(f"AssemblyAI upload failed: {r.status_code} {r.text}")
    return r.json()["upload_url"]

def _request_transcript(upload_url: str) -> str:
    headers = {
        "authorization": ASSEMBLYAI_API_KEY,
        "content-type": "application/json"
    }
    payload = {"audio_url": upload_url, "language_code": "en_us"}
    r = requests.post(TRANSCRIPT_URL, headers=headers, json=payload)
    if not r.ok:
        raise RuntimeError(f"AssemblyAI transcript request failed: {r.status_code} {r.text}")
    return r.json()["id"]

def _wait_for_transcript(transcript_id: str, timeout: int = 90, interval: int = 2) -> str:
    headers = {"authorization": ASSEMBLYAI_API_KEY}
    poll_url = f"{TRANSCRIPT_URL}/{transcript_id}"
    elapsed = 0
    while elapsed < timeout:
        r = requests.get(poll_url, headers=headers)
        if not r.ok:
            raise RuntimeError(f"AssemblyAI polling failed: {r.status_code} {r.text}")
        data = r.json()
        if data.get("status") == "completed":
            return data.get("text", "")
        if data.get("status") == "error":
            raise RuntimeError(f"AssemblyAI transcription error: {data.get('error')}")
        time.sleep(interval)
        elapsed += interval
    raise TimeoutError("AssemblyAI transcription timed out")

def transcribe_audio(file_path: str) -> str:
    """
    Full STT pipeline:
    - upload -> request -> poll -> return text
    """
    if not ASSEMBLYAI_API_KEY:
        raise RuntimeError("ASSEMBLYAI_API_KEY not set.")
    upload_url = _upload_file(file_path)
    transcript_id = _request_transcript(upload_url)
    text = _wait_for_transcript(transcript_id)
    return text
