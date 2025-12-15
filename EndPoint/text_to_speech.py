from util.config import client, cls, Path, HTTPException, APIRouter
from util.audio_model import audio_model
from util.token_utils import count_tokens
from util.audio_utils import get_audio_duration_seconds
text_to_speech_router = APIRouter(tags=["text-to-speech"])


@text_to_speech_router.post("/text-to-speech", response_model=cls.TextToSpeechResponse)
async def text_to_speech(request: cls.TextToSpeechRequest):
    try:
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
        return cls.TextToSpeechResponse(
            status="success",
            message="Speech synthesis complete", 
            file_path=str(speech_file_path),
            token_count=token_count,
            duration=get_audio_duration_seconds(str(speech_file_path))
            )
    except Exception as e:
        return cls.TextToSpeechResponse(
            status="False",
            message=f"An error occurred while processing the request: {str(e)}",
            file_path="",
            token_count=0,
            duration=0
        )