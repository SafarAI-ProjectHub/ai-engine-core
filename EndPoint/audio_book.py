from util.config import client, cls, Path, HTTPException, APIRouter
from util.audio_model import audio_model

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
            instructions = audio_book_prompt,
            input=request.text,
            max_output_tokens=2000,
            temperature=0.5,
        )

        speech_file_path = Path(__file__).parent.parent/ "speechfiles" / f"audio-book_{request.id}.mp3"
        await audio_model(
            model="gpt-4o-mini-tts",
            voice="nova",
            instructions = audio_book_tts_prompt,
            input=text_response.output_text,
            speech_file_path=speech_file_path
        )
            
        return cls.AduioBookResponse(
            message="Audio book created successfully",
            text=text_response.output_text,
            file_path=str(speech_file_path)
        )
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))