from pydantic import BaseModel
from typing import Optional

class ChatResponse(BaseModel):
    transcript: Optional[str] = None
    ai_text: Optional[str] = None
    audio_url: Optional[str] = None
    history: Optional[str] = None
    error: Optional[str] = None
