import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pathlib import Path
from openai import AsyncOpenAI, audio
import dotenv 
import os 
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from util import parsingoutput as prs
from safarai_realtime.backend import realtime

# Load environment variables from .env file
dotenv.load_dotenv()
key = os.getenv("OPEN_AI_KEY")
client = AsyncOpenAI(api_key=key)

# Define a simple FastAPI app
app = FastAPI(root_path="/ai")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(realtime)


@app.get("/")
def read_root():
    return {"Hello": "World"}

class AduioBookRequest(BaseModel):
    text: str
    id: int


class AduioBookResponse(BaseModel):
    message: str
    text: str
    file_path: str

@app.post("/audio-book", response_model=AduioBookResponse)
async def audio_book(request: AduioBookRequest):
    try:
        audio_book_path = Path(__file__).parent.parent/ "config" / "audiobookprompts.txt"
        with open(audio_book_path, "r", encoding="utf-8") as file:
            audio_book_prompt = file.read()

        audio_book_tts_path = Path(__file__).parent.parent/ "config" / "audiobookttsprompts.txt"
        with open(audio_book_tts_path, "r", encoding="utf-8") as file:
            audio_book_tts_prompt = file.read()

        text_response = await client.responses.create(
            model="gpt-5",
            instructions = audio_book_prompt,
            input=request.text,
        )

        speech_file_path = Path(__file__).parent.parent/ "speechfiles" / f"audio-book{request.id}.mp3"
        async with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="nova",
            instructions = audio_book_tts_prompt,
            input=text_response.output_text,
        ) as audio_response:
            await audio_response.stream_to_file(speech_file_path)
            
        return AduioBookResponse(
            message="Audio book created successfully",
            text=text_response.output_text,
            file_path=str(speech_file_path)
        )
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))

# Text-to-Speech endpoint
class TextToSpeechRequest(BaseModel):
    text: str
    id: int
class TextToSpeechResponse(BaseModel):
    message: str
    file_path: str
# Get user input for the text to be converted to speech
@app.post("/text-to-speech", response_model=TextToSpeechResponse)
async def text_to_speech(request: TextToSpeechRequest):
    try:
        speech_file_path = Path(__file__).parent.parent/ "speechfiles" / f"speech{request.id}.mp3"

        async with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="nova",
            instructions="Please read the text in a clear and engaging manner. Use a friendly tone and emphasize key points.",
            input=request.text
        ) as response:
            await response.stream_to_file(speech_file_path)

        return TextToSpeechResponse(message="Speech synthesis complete", file_path=str(speech_file_path))
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))
    
# translation endpoint
class translationRequest(BaseModel):
    text : str
    target_language: str
class translationResponse(BaseModel):
    translation: str
    info: str

@app.post("/translate", response_model=translationResponse)
async def translate_text(request: translationRequest):
    try:
        response = await client.responses.create(
            model = "gpt-5-nano",
            instructions = f"""
            You are a translation assistant. Your ONLY task is to translate the user's text to {request.target_language}.
            Do NOT answer, explain, or comment on the text. Do NOT provide any information except the translation and a brief description of the translated text.
            If the input is a question, ONLY translate the question—do NOT answer it.
            Return the translation in JSON format with these keys: {{ "translation": "string", "info": "string" }}.
            Do NOT return the original text, any answers, or any extra information.

            ##EXAMPLES##
            input: "How are you?"
            output: {{ "translation": "مرحباً، كيف حالك؟", "info": "سؤال شائع للتحية." }}

            input: "What is the capital of France?"
            output: {{ "translation": "ما هي عاصمة فرنسا؟", "info": "سؤال عن عاصمة دولة." }}

            input: "Translate: I love programming."
            output: {{ "translation": "أحب البرمجة.", "info": "جملة تعبر عن الحب للبرمجة." }}
            """,
            input = request.text,
        )
        # Parse the response to extract JSON
        response_data = prs.extract_json_from_response(response)
        # Return the translation response model
        return translationResponse(
            translation=response_data.get("translation", "error:translation not found"),
            info=response_data.get("info", "error:info not found")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
class CorrectionRequest(BaseModel):
    question: str
    text: str
class CorrectionResponse(BaseModel):
    score: int
    feedback: str
#Writing correction endpoint
@app.post("/correction")
async def get_correction(request: CorrectionRequest):
    try:
        criteria_path = Path(__file__).parent.parent / "config" / "activitywritingcriteria.txt"
        example_path = Path(__file__).parent.parent / "config" / "writingexamples.txt"
        # read the criteria from the file
        with open(criteria_path, "r", encoding="utf-8") as file:
            # read the file content
            criteria = file.read()
        with open(example_path, "r", encoding="utf-8") as file:
            # read the file content
            examples = file.read()
            
        response = await client.responses.create(
            model = "gpt-5",
            temperature=0,
            instructions = f"""
                You are a professional writing correction assistant.
                Your task is to evaluate a user's written response based on:

                The given question: 
                {request.question}

                The evaluation criteria: 
                {criteria}

                ##Scoring##

                ##Evaluate the response across five criteria:##

                -Task Achievement
                -Coherence and Cohesion
                -Lexical Resource
                -Grammatical Range and Accuracy
                -Spelling, Punctuation, and Mechanics
                -Each criterion must be scored with 0, 1, 3, or 5.
                -Sum the scores to produce a total out of 25.

                ##Output Format##

                Return the result in JSON with exactly these keys:
                {
                "score": int,
                "feedback": str
                }

                ##Feedback Instructions##

                -Feedback must be concise, constructive, and supportive.
                -Address each criterion specifically with strengths and suggestions for improvement.
                -Point out specific mistakes and show how to correct them.
                -If a criterion does not apply, do not penalize the user.
                -Be fair and lenient, always giving the benefit of the doubt.
                -Do not restate the question or answer, explain the criteria, or add extra commentary.

                ##Example##
                {examples}""",
                
            input = request.text
        )
        # Parse the response to extract JSON
        response_data = prs.extract_json_from_response(response, header="score:")
        return CorrectionResponse(
            score=response_data.get("score", "error:score not found"),
            feedback=response_data.get("feedback", "error:feedback not found")
        )
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))



uvicorn.run(app, host = "0.0.0.0", port = 9999)


