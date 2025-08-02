import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pathlib import Path
from openai import AsyncOpenAI
import dotenv 
import os 
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
import uvicorn
from util import parsingoutput as prs


# Load environment variables from .env file
dotenv.load_dotenv()
key = os.getenv("OPEN_AI_KEY")
client = AsyncOpenAI(api_key=key)

# Define a simple FastAPI app
app = FastAPI(root_path="/ai")

@app.get("/")
def read_root():
    return {"Hello": "World"}


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
            model = "gpt-4.1",
            instructions = f"""
            you are a translation assistant. your task is to
            Translate the text provided by the user to {request.target_language}. 
            return the translation with additional information of the translated text if needed.
            return the translation in a JSON format with the following keys: [ 'translation':'string', 'info' : 'string']
            ##important##
            do not return any other text or information.
            do not return the original text.
            do not return the translation in any other format.
            do not answer any question.
            only translate the text provided by the user.

            ##EXAMPLE##
            input: "How are you?"
            output: "translation": "مرحباً، كيف حالك؟", "info": "الجملة هي تحية شائعة تستخدم للاستفسار عن حال الشخص الآخر."
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
        with open(criteria_path, "r", encoding="utf-8") as file:
            # read the file content
            criteria = file.read()
        response = await client.responses.create(
            model = "gpt-4.1",
            temperature=0,
            instructions = f"""You are a professional writing correction assistant. Your task is to evaluate a user's written response based on a given question Here is the question: {request.question} and a set of criteria Here are the criteria: {criteria}. 
            You must score the response on five criteria: Task Achievement, Coherence and Cohesion, Lexical Resource, Grammatical Range and Accuracy, and Spelling/Punctuation/Mechanics.
            Each criterion must be scored using one of the following values: 0, 1, 3, or 5. You must sum the individual scores to return a total score out of 25. 
            Return your result in JSON format with the following keys: ["score": int, "feedback": str].
            The feedback should be concise, constructive, and supportive, highlighting strengths and offering suggestions for improvement. 
            If a criterion does not apply to the response, do not penalize the user. Be lenient and fair—always give the benefit of the doubt. 
            Do not include any additional commentary, explanation of the criteria, or restate the original question or answer. Only return the JSON response.

            ##EXAMPLE##
            input: "The dog brown run fastly in park."
            output: {{ "score": 9, "feedback": "The response shows some understanding of the task but needs improvement in grammar, vocabulary, and mechanics. Consider using 'brown dog' and 'runs quickly'. Sentence structure should be reviewed for better clarity." }}
            """,
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