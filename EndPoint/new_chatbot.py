from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from openai import OpenAI
from dotenv import load_dotenv
import os
import requests as req
import json

load_dotenv()
api_key = os.getenv("OPEN_AI_KEY")
new_chatbot_router = APIRouter(tags=["new_chatbot"])
client = OpenAI(api_key=api_key)

prompt = """You are a friendly, professional, helpful assistant that guides students in learning English.
You are an expert in English education. You only answer questions related to learning English.
If the User want to translate something, you will translate it to English or vice-versa to arabic and give a brief explanation.
if the sent a single word, you will give the meaning of that word in English and Arabic.
If the user asks something unrelated, reply with: "I can only answer questions about learning English."
Correct any typos the user makes.
You're talking to kids or teenagers."""

@new_chatbot_router.get("/new_conversation")
async def new_conversation():
    try:
        coversationID = client.conversations.create()
        return {"conversation_id": coversationID.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@new_chatbot_router.delete("/delete_conversation")
async def delete_conversation(conversation_id: str):
    try:
        url = f"https://api.openai.com/v1/conversations/{conversation_id}"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        response = req.delete(url, headers=headers)

        if response.status_code == 200:
            return {"message": "Conversation deleted successfully", "status": "success"}
        else:
            return {"message": "Failed to delete conversation", "status": "error", "details": response.json()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@new_chatbot_router.post("/chatbot")
async def chat(conversation_id: str, user_message: str):
    try:
        response = client.responses.create(
            model="gpt-4.1",
            conversation=conversation_id,
            input = user_message,
            instructions=prompt
        )

        return response.output_text
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))