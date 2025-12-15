from util.config import client, cls, Path, APIRouter
from util.audio_model import audio_model
from util.token_utils import count_tokens
from util.audio_utils import get_audio_duration_seconds
audio_book_router = APIRouter(tags=["audio-book"])

@audio_book_router.post("/audio-book", response_model=cls.AduioBookResponse)
async def audio_book(request: cls.AduioBookRequest):
    try:
        audio_book_path = Path(__file__).parent.parent/ "config" / "audiobook_prompt.txt"
        with open(audio_book_path, "r", encoding="utf-8") as file:
            audio_book_prompt = file.read()

        audio_book_tts_path = Path(__file__).parent.parent/ "config" / "audiobook_TTS_prompt.txt"
        with open(audio_book_tts_path, "r", encoding="utf-8") as file:
            audio_book_tts_prompt = file.read()

        text_response = await client.responses.create(
            model="gpt-4.1",
            instructions=audio_book_prompt,
            input=request.text,
            max_output_tokens=2000,
            temperature=0.5,
        )
        # Ensure the speechfiles directory exists before writing the file
        speech_dir = Path(__file__).parent.parent / "speechfiles"
        speech_dir.mkdir(parents=True, exist_ok=True)
        speech_file_path = speech_dir / f"audio-book_{request.id}.mp3"
        await audio_model(
            model="gpt-4o-mini-tts",
            voice=request.voice,
            instructions = audio_book_tts_prompt,
            input=text_response.output_text,
            speech_file_path=speech_file_path
        )
        token_count = count_tokens(request.text, "gpt-4.1") + count_tokens(text_response.output_text, "gpt-4.1")
        duration = get_audio_duration_seconds(str(speech_file_path))
        return cls.AduioBookResponse(
            status="success",
            message="Audio book created successfully",
            text=text_response.output_text,
            file_path=str(speech_file_path),
            token_count=token_count,
            duration=duration
        )
    except Exception as e:
        return cls.AduioBookResponse(
            status="False",
            message=f"An error occurred while processing the request: {str(e)}",
            text="",
            file_path="",
            token_count=0,
            duration=0
        )