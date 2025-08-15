import os
import tempfile
import uuid
import logging
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Logging config
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | ai-voice-agent | %(message)s"
)
logger = logging.getLogger("ai-voice-agent")

# Import service modules
from services.stt_service import transcribe_audio
from services.tts_service import text_to_speech
from services.ai_service import get_ai_response

# In-memory chat history store
chat_history = {}

# Create FastAPI app
app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("templates/index.html")


@app.post("/agent/chat/{session_id}")
async def agent_chat(session_id: str, audio: UploadFile = File(...)):
    logger.info(f"[{session_id}] Received audio: {audio.filename}")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
        tmp_path = tmp.name
        tmp.write(await audio.read())
    logger.info(f"[{session_id}] Saved to {tmp_path}")

    transcript_text = None
    ai_text = None
    audio_url = None

    try:
        if not os.getenv("ASSEMBLYAI_API_KEY"):
            raise RuntimeError("ASSEMBLYAI_API_KEY not set.")
        transcript_text = transcribe_audio(tmp_path)
    except Exception as e:
        logger.error(f"[{session_id}] STT failed: {e}")
        transcript_text = "(Error: could not get transcript)"

    try:
        ai_text = get_ai_response(transcript_text or "")
    except Exception as e:
        logger.error(f"[{session_id}] AI failed: {e}")
        ai_text = "(Error: could not get AI response)"

    try:
        if not os.getenv("MURF_API_KEY"):
            raise RuntimeError("MURF_API_KEY not set.")
        audio_url = text_to_speech(ai_text)
    except Exception as e:
        logger.error(f"[{session_id}] TTS failed: {e}")
        audio_url = None

    # ✅ Store in chat history
    if session_id not in chat_history:
        chat_history[session_id] = []
    chat_history[session_id].append({
        "transcript": transcript_text,
        "ai_response": ai_text
    })

    return JSONResponse({
        "transcript": transcript_text,
        "ai_response": ai_text,
        "audio_url": audio_url,
        "history": chat_history[session_id]
    })


@app.get("/audio/{filename}")
async def get_audio(filename: str):
    path = os.path.join(tempfile.gettempdir(), filename)
    return FileResponse(path, media_type="audio/mpeg")


# ✅ New clear history endpoint
@app.post("/agent/clear/{session_id}")
async def clear_history(session_id: str):
    if session_id in chat_history:
        del chat_history[session_id]
        logger.info(f"[{session_id}] Chat history cleared.")
        return {"ok": True}
    return {"ok": False, "error": "No history found"}
