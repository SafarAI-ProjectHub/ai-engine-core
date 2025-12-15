from fastapi import APIRouter, HTTPException
from openai import OpenAI
from dotenv import load_dotenv
import os
import requests as req
from util.config import cls
from util.token_utils import count_tokens
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
async def chat(request: cls.NewChatbotRequest):
    try:
        response = client.responses.create(
            model="gpt-4.1",
            conversation=request.conversation_id,
            input = request.message,
            instructions=prompt
        )

        token_count = count_tokens(request.message, "gpt-4.1") + count_tokens(response.output_text, "gpt-4.1")
        return cls.NewChatbotResponse(
            status="success",
            response=response.output_text,
            token_count=token_count
        )
    except Exception as e:
        return cls.NewChatbotResponse(
            status="False",
            response=f"An error occurred while processing the request: {str(e)}",
            token_count=0
        )