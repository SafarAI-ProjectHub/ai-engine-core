from fastapi import APIRouter, HTTPException
from openai import OpenAI
from dotenv import load_dotenv
import os
import requests as req
from util.config import cls
from util.token_utils import count_tokens
from util.logging_config import get_logger, get_correlation_id
load_dotenv()

api_key = os.getenv("OPEN_AI_KEY")
new_chatbot_router = APIRouter(tags=["new_chatbot"])
client = OpenAI(api_key=api_key)
logger = get_logger(__name__)

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
        data = {"conversation_id": coversationID.id}
        logger.info(
            "New conversation created | conversation_id=%s cid=%s",
            coversationID.id,
            get_correlation_id(),
        )
        return cls.build_response(
            data=data,
            endpoint_key="new_chatbot_new_conversation",
        )
    except Exception as e:
        logger.exception("Error creating new conversation: %s", e)
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
            data = {"message": "Conversation deleted successfully", "status": "success"}
            success = True
        else:
            data = {
                "message": "Failed to delete conversation",
                "status": "error",
                "details": response.json(),
            }
            success = False
        logger.info(
            "Delete conversation | conversation_id=%s status_code=%s success=%s",
            conversation_id,
            response.status_code,
            success,
        )
        return cls.build_response(
            data=data,
            endpoint_key="new_chatbot_delete_conversation",
            success=success,
        )
    except Exception as e:
        logger.exception("Error deleting conversation | conversation_id=%s error=%s", conversation_id, e)
        raise HTTPException(status_code=500, detail=str(e))
    

@new_chatbot_router.post("/chatbot", response_model=cls.ApiResponse)
async def chat(request: cls.NewChatbotRequest):
    try:
        response = client.responses.create(
            model="gpt-4.1",
            conversation=request.conversation_id,
            input = request.message,
            instructions=prompt
        )

        token_count = count_tokens(request.message, "gpt-4.1") + count_tokens(
            response.output_text, "gpt-4.1"
        )
        data = cls.NewChatbotResponse(
            status="success",
            response=response.output_text,
            token_count=token_count,
        )
        usage = cls.Usage(tokens=token_count)

        logger.info(
            "New chatbot message | conversation_id=%s tokens=%s cid=%s",
            request.conversation_id,
            token_count,
            get_correlation_id(),
        )

        return cls.build_response(
            data=data,
            usage=usage,
            endpoint_key="new_chatbot_chat",
        )
    except Exception as e:
        logger.exception("Error in new_chatbot chat endpoint: %s", e)
        data = cls.NewChatbotResponse(
            status="False",
            response=f"An error occurred while processing the request: {str(e)}",
            token_count=0,
        )
        usage = cls.Usage(tokens=0)
        return cls.build_response(
            data=data,
            usage=usage,
            endpoint_key="new_chatbot_chat",
            success=False,
        )
