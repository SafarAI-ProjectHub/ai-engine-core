from pydantic import BaseModel

class AduioBookRequest(BaseModel):
    text: str
    id: int
class AduioBookResponse(BaseModel):
    message: str
    text: str
    file_path: str



class TextToSpeechRequest(BaseModel):
    text: str
    id: int
    voice: str = "nova"
    accent: str
class TextToSpeechResponse(BaseModel):
    message: str
    file_path: str



class translationRequest(BaseModel):
    text : str
    target_language: str
class translationResponse(BaseModel):
    translation: str
    info: str



class CorrectionRequest(BaseModel):
    question: str
    text: str
class CorrectionResponse(BaseModel):
    score: int
    feedback: str




class ChatbotRequest(BaseModel):
    message: str
    conversation_history: list = []  # List of previous messages

class ChatbotResponse(BaseModel):
    response: str
    conversation_history: list