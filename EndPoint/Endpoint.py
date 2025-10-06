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
from fastapi.responses import StreamingResponse
import uvicorn
from util import parsingoutput as prs
from util import classes as cls
from safarai_realtime.backend import realtime
from safarai_chatbot.chatbot.chatbot import stream_response, system_prompt
from langchain.schema import HumanMessage, AIMessage
import json

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

@app.post("/audio-book", response_model=cls.AduioBookResponse)
async def audio_book(request: cls.AduioBookRequest):
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
            
        return cls.AduioBookResponse(
            message="Audio book created successfully",
            text=text_response.output_text,
            file_path=str(speech_file_path)
        )
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))

# Text-to-Speech endpoint

# Get user input for the text to be converted to speech
@app.post("/text-to-speech", response_model=cls.TextToSpeechResponse)
async def text_to_speech(request: cls.TextToSpeechRequest):
    try:
        speech_file_path = Path(__file__).parent.parent/ "speechfiles" / f"speech{request.id}.mp3"

        async with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="nova",
            instructions="Please read the text in a clear and engaging manner. Use a friendly tone and emphasize key points.",
            input=request.text
        ) as response:
            await response.stream_to_file(speech_file_path)

        return cls.TextToSpeechResponse(message="Speech synthesis complete", file_path=str(speech_file_path))
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))
    
# translation endpoint


@app.post("/translate", response_model=cls.translationResponse)
async def translate_text(request: cls.translationRequest):
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
        return cls.translationResponse(
            translation=response_data.get("translation", "error:translation not found"),
            info=response_data.get("info", "error:info not found")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    



#Writing correction endpoint
@app.post("/correction")
async def get_correction(request: cls.CorrectionRequest):
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
        return cls.CorrectionResponse(
            score=response_data.get("score", "error:score not found"),
            feedback=response_data.get("feedback", "error:feedback not found")
        )
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))

# Chatbot endpoint - regular response
@app.post("/chatbot", response_model=cls.ChatbotResponse)
async def chatbot_chat(request: cls.ChatbotRequest):
    """
    Chat with the SafarAI learning assistant.
    Returns a complete response with updated conversation history.
    """
    try:
        # Build conversation history with system prompt
        messages = [system_prompt]
        
        # Add conversation history if provided
        for msg in request.conversation_history:
            if msg.get("role") == "user":
                messages.append(HumanMessage(content=msg.get("content", "")))
            elif msg.get("role") == "assistant":
                messages.append(AIMessage(content=msg.get("content", "")))
        
        # Add current user message
        messages.append(HumanMessage(content=request.message))
        
        # Get response from chatbot
        full_response = ""
        for chunk in stream_response(messages):
            if chunk.content:
                full_response += chunk.content
        
        # Update conversation history
        updated_history = request.conversation_history.copy()
        updated_history.append({"role": "user", "content": request.message})
        updated_history.append({"role": "assistant", "content": full_response})
        
        return cls.ChatbotResponse(
            response=full_response,
            conversation_history=updated_history
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Chatbot streaming endpoint
@app.post("/chatbot/stream")
async def chatbot_stream(request: cls.ChatbotRequest):
    """
    Stream chat responses from the SafarAI learning assistant.
    Returns a streaming response for real-time chat experience.
    """
    try:
        # Build conversation history with system prompt
        messages = [system_prompt]
        
        # Add conversation history if provided
        for msg in request.conversation_history:
            if msg.get("role") == "user":
                messages.append(HumanMessage(content=msg.get("content", "")))
            elif msg.get("role") == "assistant":
                messages.append(AIMessage(content=msg.get("content", "")))
        
        # Add current user message
        messages.append(HumanMessage(content=request.message))
        
        def generate_stream():
            try:
                for chunk in stream_response(messages):
                    if chunk.content:
                        # Format as Server-Sent Events
                        yield f"data: {json.dumps({'content': chunk.content, 'done': False})}\n\n"
                # Send completion signal
                yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

uvicorn.run(app, host = "0.0.0.0", port = 9999)


