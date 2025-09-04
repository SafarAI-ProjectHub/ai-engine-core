# backend.py
import os
import json
import aiohttp
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import uvicorn

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_REALTIME_URL = "https://api.openai.com/v1/realtime/sessions"

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

active_sessions = {}  # Store session IDs temporarily


@app.post("/session")
async def create_session(request: Request):
    """Create a new real-time WebRTC session with OpenAI"""

    data = await request.json()
    level = data.get("level", "Intermediate")
    print(f"Creating session for level: {level}")

    level_instructions = {
        "Beginner": "Use very simple English, short sentences, and speak slowly. Avoid difficult vocabulary. Encourage the student gently.",
        "Intermediate": "Use everyday English, with some new vocabulary. Ask questions, correct mistakes, and explain grammar in simple terms.",
        "Advanced": "Use natural, fluent, and more complex English. Challenge the student with idioms, advanced grammar, and deeper discussions."
    }
    print(f"Creating session for level: {level}")
    print(f"Level instructions: {level_instructions.get(level, '')}")

    instruction = f"""You are "Safar AI", an enthusiastic and friendly English speaking tutor. Your goal is to help students improve their spoken English through lively, enjoyable conversations.

- Always speak in an excited, positive, and encouraging way to make the student feel motivated and happy.
- Start and maintain engaging, human-like discussions on everyday topics.
- If the student makes a grammatical or pronunciation mistake, gently correct them and clearly explain the error in a supportive, cheerful manner.
- Encourage students to express themselves and ask follow-up questions to keep the conversation fun and flowing.
- Always provide constructive feedback and motivate students to keep practicing and enjoying the learning process.

 **important**:
 - Always follow the user's selected English level when providing feedback and corrections.
 - Use the appropriate level instructions to guide the conversation and support the user's learning.
 - Be patient and encouraging, especially with beginners who may need more support.
 - Adapt your language and explanations based on the user's proficiency and comfort level.
 - Keep the conversation engaging and fun to motivate the user to practice more.
 - the student's level is {level}.
 - and you must {level_instructions.get(level, "")}
"""

    async with aiohttp.ClientSession() as session:
        async with session.post(
            OPENAI_REALTIME_URL,
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
            "model": "gpt-realtime",
            "modalities": ["audio", "text"],
            "instructions": instruction },
        ) as resp:
            if resp.status != 200:
                return JSONResponse(
                    status_code=resp.status,
                    content={"error": await resp.text()},
                )

            data = await resp.json()
            session_id = data.get("id")
            print(f"Created session with ID: {session_id}")
            if session_id:
                active_sessions[session_id] = data
            return data


@app.post("/close")
async def close_session(session_id: str):
    """Close an active WebRTC session (for cleanup)"""
    if session_id in active_sessions:
        del active_sessions[session_id]
        print(f"Closed session with ID: {session_id}")
        return {"status": "Session closed"}
    else:
        print(f"Attempted to close non-existent session with ID: {session_id}")
        return {"error": "Session not found"}
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)