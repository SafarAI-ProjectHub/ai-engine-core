# backend.py
import os
import json
import aiohttp
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from dotenv import load_dotenv
import uvicorn

load_dotenv()

OPENAI_API_KEY = os.getenv("OPEN_AI_KEY")
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


@app.get("/new")
async def serve_newcall():
    """Serve the enhanced frontend with the talking orb."""
    here = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(here, "newcall.html")
    return FileResponse(filepath)

@app.post("/session")
async def create_session(request: Request):
    """Create a new real-time WebRTC session with OpenAI"""

    data = await request.json()
    level = data.get("level", "Intermediate")
    theme = data.get("theme", "Daily Life")
    topic = data.get("topic", "")
    personality = data.get("personality", "Friendly Mentor")
    avatar = data.get("avatar", "friendly")
    print(f"Creating session for level: {level}, theme: {theme}, topic: {topic}, personality: {personality}, avatar: {avatar}")

    level_instructions = {
        "Beginner": "Use very simple English, short sentences, and speak slowly. Avoid difficult vocabulary. Encourage the student gently.",
        "Intermediate": "Use everyday English, with some new vocabulary. Ask questions, correct mistakes, and explain grammar in simple terms.",
        "Advanced": "Use natural, fluent, and more complex English. Challenge the student with idioms, advanced grammar, and deeper discussions."
    }
    theme_prompts = {
        "Daily Life": "Talk about everyday routines, shopping, food, family, housing, and errands.",
        "Travel": "Discuss destinations, flights, hotels, itineraries, directions, and travel experiences.",
        "Work/Business": "Discuss workplaces, meetings, emails, presentations, negotiations, and career goals.",
        "Hobbies": "Talk about free-time activities, sports, arts, collections, and personal interests.",
        "School/University": "Discuss classes, assignments, majors, study tips, exams, and campus life.",
        "Culture & Society": "Discuss customs, festivals, news, values, traditions, and social issues with sensitivity."
    }

    personality_instructions = {
        "Friendly Mentor": "Be warm, encouraging, and supportive. Use a gentle, caring tone. Celebrate small victories and provide positive reinforcement. Use phrases like 'Great job!' and 'You're doing wonderfully!'",
        "Professional Coach": "Be structured, clear, and goal-oriented. Focus on practical improvement and measurable progress. Use business-like language and provide specific feedback. Be direct but respectful.",
        "Casual Friend": "Be relaxed, informal, and conversational. Use everyday language, slang when appropriate, and keep things light and fun. Make jokes and use casual expressions like 'Hey there!' and 'No worries!'",
        "Academic Expert": "Be precise, detailed, and scholarly. Use formal language and provide thorough explanations. Focus on grammar rules, vocabulary expansion, and linguistic accuracy. Be patient with complex explanations.",
        "Energetic Guide": "Be enthusiastic, dynamic, and motivating. Use exclamation points, energetic language, and motivational phrases. Keep the energy high and encourage active participation. Use phrases like 'Let's go!' and 'You've got this!'",
        "Patient Teacher": "Be calm, understanding, and methodical. Take time to explain things clearly and repeat when necessary. Use a soothing tone and be very patient with mistakes. Provide gentle guidance and reassurance."
    }

    print(f"Creating session for level: {level}, theme: {theme}")
    print(f"Level instructions: {level_instructions.get(level, '')}")
    print(f"Theme focus: {theme_prompts.get(theme, '')}")
    if topic:
        print(f"Specific topic: {topic}")

    instruction = f"""You are "Safar AI", an English speaking tutor with the personality of a {personality}. Your goal is to help students improve their spoken English through engaging, personality-driven conversations.

**Your Personality & Teaching Style:**
{personality_instructions.get(personality, personality_instructions["Friendly Mentor"])}

**Core Teaching Principles:**
- Start and maintain engaging, human-like discussions on everyday topics.
- If the student makes a grammatical or pronunciation mistake, correct them appropriately based on your personality style.
- Encourage students to express themselves and ask follow-up questions to keep the conversation flowing.
- Always provide constructive feedback and motivate students to keep practicing.

**Important Guidelines:**
- Always follow the user's selected English level when providing feedback and corrections.
- Use the appropriate level instructions to guide the conversation and support the user's learning.
- Be patient and encouraging, especially with beginners who may need more support.
- Adapt your language and explanations based on the user's proficiency and comfort level.
- Keep the conversation engaging and fun to motivate the user to practice more.

**Session Details:**
- Student's level: {level}
- Level instructions: {level_instructions.get(level, "")}
- Conversation theme: {theme}
- Theme focus: {theme_prompts.get(theme, "")}
- Specific topic: {topic if topic else "None - use general theme topics"}
- Your personality: {personality}
- Teaching approach: {personality_instructions.get(personality, "")}

Remember to embody your {personality} personality throughout the entire conversation while maintaining effective English teaching practices.
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
    uvicorn.run(app, host="0.0.0.0", port=8000)