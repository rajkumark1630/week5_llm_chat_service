
import uuid

from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse

from app.schemas import ChatRequest
from app.streaming import stream_openai
from app.conversation import (
    create_conversation,
    add_message,
    get_messages,
    get_conversation,
    delete_conversation
)
from app.usage import get_usage_summary
from app.reliability import get_reliability_summary
from app.dependencies import (
    get_authenticated_user,
    get_settings
)


app = FastAPI(
    title="OpenRouter LLM Chat Service",
    description="LLM Chat API with Streaming, Authentication and Monitoring",
    version="1.0.0"
)


@app.get("/")
async def home():
    return {
        "message": "LLM Chat Service is running",
        "provider": "OpenRouter",
        "status": "active"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }


@app.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    authenticated: bool = Depends(get_authenticated_user)
):
    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )

    conversation_id = (
        request.conversation_id or str(uuid.uuid4())
    )

    if not get_conversation(conversation_id):
        create_conversation(conversation_id)

    add_message(
        conversation_id,
        "user",
        request.message
    )

    messages = get_messages(conversation_id)

    def generate():
        answer_parts = []

        try:
            # Stream the current conversation context
            for chunk in stream_openai(
                request.message,
                messages=messages
            ):
                if chunk:
                    answer_parts.append(chunk)
                    yield f"data: {chunk}\n\n"

            answer = "".join(answer_parts)

            if answer:
                add_message(
                    conversation_id,
                    "assistant",
                    answer
                )

            yield f"event: conversation_id\ndata: {conversation_id}\n\n"
            yield "data: [DONE]\n\n"

        except Exception:
            yield "event: error\ndata: Streaming failed\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/conversation/{conversation_id}")
async def conversation_history(
    conversation_id: str,
    authenticated: bool = Depends(get_authenticated_user)
):
    conversation = get_conversation(conversation_id)

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    return conversation


@app.delete("/conversation/{conversation_id}")
async def remove_conversation(
    conversation_id: str,
    authenticated: bool = Depends(get_authenticated_user)
):
    deleted = delete_conversation(conversation_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    return {
        "message": "Conversation deleted successfully"
    }


@app.get("/usage")
async def usage(
    authenticated: bool = Depends(get_authenticated_user)
):
    return get_usage_summary()


@app.get("/reliability")
async def reliability(
    authenticated: bool = Depends(get_authenticated_user)
):
    return get_reliability_summary()


@app.get("/settings")
async def application_settings(
    authenticated: bool = Depends(get_authenticated_user),
    settings=Depends(get_settings)
):
    return {
        "model": settings.openrouter_model,
        "max_input_tokens": settings.max_input_tokens,
        "provider": "OpenRouter"
    }
