import os
import logging
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger("ai-voice-agent")

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY not set in .env file.")
genai.configure(api_key=api_key)

# Use latest Gemini model
MODEL_NAME = "gemini-1.5-pro-latest"


def get_ai_response(prompt: str) -> str:
    """
    Send prompt to Gemini API and get the AI-generated text response.
    """
    if not prompt.strip():
        logger.warning("Empty prompt passed to AI service.")
        return "(No input provided.)"

    logger.info("Sending prompt to Gemini API...")
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)

        if hasattr(response, "text") and response.text:
            return response.text.strip()
        else:
            logger.error("No text returned from Gemini API.")
            return "(Error: No AI response text.)"
    except Exception as e:
        logger.error(f"Error getting AI response: {e}")
        return f"(Error: {e})"
