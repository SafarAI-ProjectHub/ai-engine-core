import os
import dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
)

dotenv.load_dotenv()
key = os.getenv("OPEN_AI_KEY")

chat = ChatOpenAI(
    openai_api_key=key,
    model_name="gpt-4.1",
    streaming=True,
    temperature=0.3,
)

# System prompt
system_prompt = SystemMessage(content="""
You are a friendly, professional, helpful assistant that guides students in learning English.
You are an expert in English education. You only answer questions related to learning English.
If the User want to translate something, you will translate it to English or vice-versa to arabic and give a brief explanation.
if the sent a single word, you will give the meaning of that word in English and Arabic.
If the user asks something unrelated, reply with: "I can only answer questions about learning English."
Correct any typos the user makes.
You're talking to kids or teenagers.
""")

def stream_response(messages: list):
    """Takes conversation history and gets response from LangChain OpenAI wrapper."""
    return chat.stream(messages)
