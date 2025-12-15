from pydantic import BaseModel

class AduioBookRequest(BaseModel):
    text: str
    id: int
    voice: str = "nova"
    accent: str
class AduioBookResponse(BaseModel):
    status: str
    message: str
    text: str
    file_path: str
    token_count: int
    duration: float



class TextToSpeechRequest(BaseModel):
    text: str
    id: int
    voice: str = "nova"
    accent: str
class TextToSpeechResponse(BaseModel):
    status: str
    message: str
    file_path: str
    token_count: int
    duration: float



class translationRequest(BaseModel):
    text : str
    target_language: str
class translationResponse(BaseModel):
    status: str
    translation: str
    info: str
    token_count: int



class CorrectionRequest(BaseModel):
    question: str
    text: str
class CorrectionResponse(BaseModel):
    status: str
    score: int
    feedback: str
    token_count: int




class ChatbotRequest(BaseModel):
    message: str
    conversation_history: list = []  # List of previous messages

class ChatbotResponse(BaseModel):
    status: str
    response: str
    conversation_history: list
    token_count: int


class NewChatbotRequest(BaseModel):
    message: str
    conversation_id: str
class NewChatbotResponse(BaseModel):
    status: str
    response: str
    token_count: int