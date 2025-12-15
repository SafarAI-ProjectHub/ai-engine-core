# backend.py
import os
import time
import aiohttp
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, FileResponse
from dotenv import load_dotenv
import uvicorn
from util.logging_config import get_logger, get_correlation_id

load_dotenv()

OPENAI_API_KEY = os.getenv("OPEN_AI_KEY")
OPENAI_REALTIME_URL = "https://api.openai.com/v1/realtime/sessions"


realtime = APIRouter(tags=["realtime"], prefix="/realtime")


active_sessions = {}  # Store session IDs temporarily
logger = get_logger(__name__)


@realtime.get("/new")
async def serve_newcall():
    """Serve the enhanced frontend with the talking orb."""
    here = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(here, "newcall.html")
    return FileResponse(filepath)

@realtime.post("/session")
async def create_session(request: Request):
    """Create a new real-time WebRTC session with OpenAI"""

    data = await request.json()
    level = data.get("level", "Intermediate")
    theme = data.get("theme", "Daily Life")
    topic = data.get("topic", "")
    personality = data.get("personality", "Friendly Mentor")
    avatar = data.get("avatar", "friendly")
    logger.info(
        "Creating realtime session | level=%s theme=%s topic=%s personality=%s avatar=%s cid=%s",
        level,
        theme,
        topic,
        personality,
        avatar,
        get_correlation_id(),
    )

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

    logger.debug("Level instructions: %s", level_instructions.get(level, ""))
    logger.debug("Theme focus: %s", theme_prompts.get(theme, ""))
    if topic:
        logger.debug("Specific topic: %s", topic)

    instruction = f"""You are "Safar AI", an English speaking tutor with the personality of a {personality}. Your goal is to help students improve their spoken English through engaging, personality-driven conversations.

**Your Personality & Teaching Style:**
{personality_instructions.get(personality, personality_instructions["Friendly Mentor"])}

**Core Teaching Principles:**
- Start and maintain engaging, human-like discussions on everyday topics.
- If the student makes a grammatical or pronunciation mistake, correct them appropriately based on your personality style.
- Encourage students to express themselves and ask follow-up questions to keep the conversation flowing.
- Always provide constructive feedback and motivate students to keep practicing.

**Correction Guidelines - IMPORTANT:**
- **Limit corrections per word**: If a student struggles with a word, correct it maximum 2-3 times, then move on.
- **Focus on communication**: Prioritize understanding and communication over perfect pronunciation.
- **Don't obsess over perfection**: If the student's pronunciation is understandable, don't keep correcting the same word.
- **Mix corrections with encouragement**: After 2-3 attempts, praise their effort and continue the conversation.
- **Choose your battles**: Only correct the most important mistakes, not every small error.

**Important Guidelines:**
- Always follow the user's selected English level when providing feedback and corrections.
- Use the appropriate level instructions to guide the conversation and support the user's learning.
- Be patient and encouraging, especially with beginners who may need more support.
- Adapt your language and explanations based on the user's proficiency and comfort level.
- Keep the conversation engaging and fun to motivate the user to practice more.
- **Remember**: The goal is fluent communication, not perfect pronunciation. Don't let corrections interrupt the flow of conversation.

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

    import ssl
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    async with aiohttp.ClientSession(connector=connector) as session:
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
            logger.info("Created realtime session with ID: %s", session_id)
            if session_id:
                data["last_activity"] = time.time()
                active_sessions[session_id] = data
                logger.info(
                    "Stored session in active_sessions | total_sessions=%s ids=%s",
                    len(active_sessions),
                    list(active_sessions.keys()),
                )
            return data


@realtime.post("/keep-alive")
async def keep_alive(request: Request):
    """Keep the session alive by updating the session timestamp"""
    data = await request.json()
    session_id = data.get("session_id")
    
    logger.info(
        "Keep-alive request | session_id=%s active_ids=%s",
        session_id,
        list(active_sessions.keys()),
    )
    
    if not session_id or session_id not in active_sessions:
        return JSONResponse(
            status_code=404,
            content={"error": "Session not found"}
        )
    
    # Update the session timestamp to keep it "active"
    active_sessions[session_id]["last_activity"] = time.time()
    logger.debug("Updated last activity for session | session_id=%s", session_id)
    return {"status": "Session kept alive", "timestamp": active_sessions[session_id]["last_activity"]}

@realtime.post("/close")
async def close_session(request: Request):
    """Close an active WebRTC session (for cleanup)"""
    try:
        data = await request.json()
        session_id = data.get("session_id")
        
        if not session_id:
            return JSONResponse(
                status_code=400,
                content={"error": "session_id is required"}
            )
        
        if session_id in active_sessions:
            del active_sessions[session_id]
            logger.info("Closed session | session_id=%s", session_id)
            return {"status": "Session closed"}
        else:
            logger.warning(
                "Attempted to close non-existent session | session_id=%s",
                session_id,
            )
            return JSONResponse(
                status_code=404,
                content={"error": "Session not found"}
            )
    except Exception as e:
        logger.exception("Error closing session | error=%s", str(e))
        return JSONResponse(
            status_code=500,
            content={"error": f"Error closing session: {str(e)}"}
        )

@realtime.get("/debug/sessions")
async def debug_sessions():
    """Debug endpoint to check active sessions"""
    return {
        "active_sessions_count": len(active_sessions),
        "session_ids": list(active_sessions.keys()),
        "sessions": active_sessions
    }
    