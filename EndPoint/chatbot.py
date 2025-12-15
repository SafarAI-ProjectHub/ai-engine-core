from util.config import cls, HTTPException, APIRouter, stream_response, system_prompt, StreamingResponse
from langchain_core.messages import HumanMessage, AIMessage
import json
from util.token_utils import count_tokens
chatbot_router = APIRouter(tags=["chatbot"])

# #@chatbot_router.post("/chatbot", response_model=cls.ChatbotResponse)
# async def chatbot_chat(request: cls.ChatbotRequest):
#     """
#     Chat with the SafarAI learning assistant.
#     Returns a complete response with updated conversation history.
#     """
#     try:
#         # Build conversation history with system prompt
#         messages = [system_prompt]
        
#         # Add conversation history if provided
#         for msg in request.conversation_history:
#             if msg.get("role") == "user":
#                 messages.append(HumanMessage(content=msg.get("content", "")))
#             elif msg.get("role") == "assistant":
#                 messages.append(AIMessage(content=msg.get("content", "")))
        
#         # Add current user message
#         messages.append(HumanMessage(content=request.message))
        
#         # Get response from chatbot
#         full_response = ""
#         for chunk in stream_response(messages):
#             if chunk.content:
#                 full_response += chunk.content
        
#         # Update conversation history
#         updated_history = request.conversation_history.copy()
#         updated_history.append({"role": "user", "content": request.message})
#         updated_history.append({"role": "assistant", "content": full_response})
        
#         return cls.ChatbotResponse(
#             response=full_response,
#             conversation_history=updated_history
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# Chatbot streaming endpoint
@chatbot_router.post("/chatbot/stream")
async def chatbot_stream(request: cls.ChatbotRequest):
    """
    Stream chat responses from the SafarAI learning assistant.
    Returns a streaming response for real-time chat experience.
    """
    try:
        # Count tokens for the current message and conversation history
        token_count = count_tokens(request.message, "gpt-4.1")
        for msg in request.conversation_history:
            token_count += count_tokens(msg.get("content", ""), "gpt-4.1")

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
                # Collect all output chunks to measure output token usage
                output_chunks = []
                for chunk in stream_response(messages):
                    if chunk.content:
                        output_chunks.append(chunk.content)
                        # Format as Server-Sent Events
                        yield f"data: {json.dumps({'content': chunk.content, 'done': False})}\n\n"

                full_output = "".join(output_chunks)
                output_token_count = count_tokens(full_output, "gpt-4.1")
                total_token_count = token_count + output_token_count

                # Send completion signal with token information
                yield f"data: {json.dumps({'content': '', 'done': True, 'token_count': total_token_count})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"

        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )
    except Exception as e:
        return cls.ChatbotResponse(
            status="False",
            response=f"An error occurred while processing the request: {str(e)}",
            conversation_history=request.conversation_history,
            token_count=0
        )