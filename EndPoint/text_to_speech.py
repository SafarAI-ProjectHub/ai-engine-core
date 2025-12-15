from util.config import client, cls, Path, HTTPException, APIRouter
from util.audio_model import audio_model
from util.token_utils import count_tokens
from util.audio_utils import get_audio_duration_seconds
from util.logging_config import get_logger, get_correlation_id

text_to_speech_router = APIRouter(tags=["text-to-speech"])
logger = get_logger(__name__)


@text_to_speech_router.post("/text-to-speech", response_model=cls.ApiResponse)
async def text_to_speech(request: cls.TextToSpeechRequest):
    try:
        logger.info(
            "Text-to-speech request | id=%s voice=%s accent=%s cid=%s",
            request.id,
            request.voice,
            request.accent,
            get_correlation_id(),
        )
        speech_file_path = Path(__file__).parent.parent/ "speechfiles" / f"speech_{request.id}.mp3"
        instructions = f"""
            Please read the text in a clear and engaging manner. Use a friendly tone and emphasize key points.
            Use the accent of the text to read the text.
            you should talk in this accent: {request.accent}.
        """

        await audio_model(
            model="gpt-4o-mini-tts",
            voice=request.voice,
            instructions=instructions,
            input=request.text,
            speech_file_path=speech_file_path
        )

        token_count = count_tokens(request.text, "gpt-4o-mini")
        data = cls.TextToSpeechResponse(
            status="success",
            message="Speech synthesis complete", 
            file_path=str(speech_file_path),
            token_count=token_count,
            duration=get_audio_duration_seconds(str(speech_file_path))
        )
        usage = cls.Usage(tokens=token_count, duration_seconds=data.duration)

        logger.info(
            "Text-to-speech complete | id=%s tokens=%s duration=%.2fs path=%s",
            request.id,
            token_count,
            data.duration,
            str(speech_file_path),
        )

        return cls.build_response(
            data=data,
            usage=usage,
            endpoint_key="tts",
        )
    except Exception as e:
        logger.exception("Error in text_to_speech endpoint: %s", e)
        data = cls.TextToSpeechResponse(
            status="False",
            message=f"An error occurred while processing the request: {str(e)}",
            file_path="",
            token_count=0,
            duration=0,
        )
        usage = cls.Usage(tokens=0, duration_seconds=0)
        return cls.build_response(
            data=data,
            usage=usage,
            endpoint_key="tts",
            success=False,
        )
