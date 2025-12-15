from typing import Any, Dict, Generic, Optional, TypeVar

from pydantic import BaseModel


#
# Shared API response models
#


class Usage(BaseModel):
    """
    Generic usage information for a request.

    All fields are optional so endpoints can fill in what they know.
    """

    tokens: Optional[int] = None
    duration_seconds: Optional[float] = None
    session_seconds: Optional[float] = None


class Meta(BaseModel):
    """
    Metadata about the endpoint / request.
    """

    endpoint_key: Optional[str] = None
    # Allow arbitrary extra metadata without changing the schema
    extra: Optional[Dict[str, Any]] = None


T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """
    Standard envelope returned by all endpoints.
    """

    success: bool
    data: T
    usage: Optional[Usage] = None
    meta: Optional[Meta] = None


def build_response(
    data: Any,
    *,
    success: bool = True,
    endpoint_key: Optional[str] = None,
    usage: Optional[Usage] = None,
    meta_extra: Optional[Dict[str, Any]] = None,
) -> ApiResponse[Any]:
    """
    Helper to construct a standard ApiResponse object.
    """
    meta = Meta(endpoint_key=endpoint_key, extra=meta_extra)
    return ApiResponse[Any](success=success, data=data, usage=usage, meta=meta)


#
# Existing request/response models
# (kept for internal use; endpoints will now wrap these in ApiResponse)
#


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
    text: str
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
