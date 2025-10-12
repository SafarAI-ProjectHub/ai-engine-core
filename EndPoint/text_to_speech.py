from util.config import client, cls, Path, HTTPException, APIRouter
from util.audio_model import audio_model

text_to_speech_router = APIRouter(tags=["text-to-speech"])


@text_to_speech_router.post("/text-to-speech", response_model=cls.TextToSpeechResponse)
async def text_to_speech(request: cls.TextToSpeechRequest):
    try:
        speech_file_path = Path(__file__).parent.parent/ "speechfiles" / f"speech_{request.id}.mp3"
        instructions = "Please read the text in a clear and engaging manner. Use a friendly tone and emphasize key points."

        await audio_model(
            model="gpt-4o-mini-tts",
            voice="nova",
            instructions=instructions,
            input=request.text,
            speech_file_path=speech_file_path
        )

        return cls.TextToSpeechResponse(message="Speech synthesis complete", file_path=str(speech_file_path))
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))