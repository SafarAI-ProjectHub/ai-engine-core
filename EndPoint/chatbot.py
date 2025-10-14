from util.config import cls, HTTPException, APIRouter, stream_response, system_prompt, HumanMessage, AIMessage, json, StreamingResponse

chatbot_router = APIRouter(tags=["chatbot"])

@chatbot_router.post("/chatbot", response_model=cls.ChatbotResponse)
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
@chatbot_router.post("/chatbot/stream")
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