from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx
import logging
import asyncio
import json

# 🔁 Import saving logic (adjust import path if needed)
from backend.app.routes.project_chat_routes import save_chat_message

router = APIRouter()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    chat_id: int
    stream: bool = False

@router.post("/chat")
async def chat_with_deepseek(request: Request):
    try:
        body = await request.json()
        messages = body.get("messages", [])
        chat_id = body.get("chat_id")
        stream = body.get("stream", False)

        if not chat_id:
            raise HTTPException(status_code=400, detail="Missing chat_id in request body.")

        logging.warning("[CHAT] Request payload: %s", body)

        if stream:
            async def stream_gen():
                collected_chunks = []

                async with httpx.AsyncClient(timeout=None) as client:
                    async with client.stream(
                        "POST",
                        "http://localhost:11434/api/chat",
                        json={
                            "model": "deepseek-coder:latest",
                            "messages": messages,
                            "stream": True,
                        },
                    ) as resp:
                        if resp.status_code != 200:
                            text = await resp.aread()
                            raise HTTPException(status_code=resp.status_code, detail=text.decode())

                        async for chunk in resp.aiter_text():
                            if chunk.strip():
                                yield f"data: {chunk}\n\n"
                                try:
                                    parsed = json.loads(chunk)
                                    if parsed.get("message", {}).get("role") == "assistant":
                                        collected_chunks.append(parsed["message"]["content"])
                                except Exception:
                                    continue  # silently ignore malformed chunks
                            await asyncio.sleep(0.01)

                # ✅ Save final assistant message
                assistant_text = "".join(collected_chunks).strip()
                if assistant_text:
                    await save_chat_message(chat_id=chat_id, content=assistant_text, role="assistant")

            return StreamingResponse(stream_gen(), media_type="text/event-stream")

        # 🧱 Fallback: non-streaming request
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": "deepseek-coder:latest",
                    "messages": messages,
                    "stream": False,
                },
                timeout=60,
            )

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Ollama error: {response.status_code} - {response.text}")

        data = response.json()

        if "message" not in data or "content" not in data["message"]:
            raise HTTPException(status_code=500, detail=f"Unexpected DeepSeek format: {data}")

        assistant_message = data["message"]["content"]
        await save_chat_message(chat_id=chat_id, content=assistant_message, role="assistant")

        return {
            "choices": [
                {
                    "message": {
                        "role": data["message"]["role"],
                        "content": assistant_message,
                    }
                }
            ]
        }

    except Exception as e:
        logging.exception("[CHAT ERROR] Failed during chat_with_deepseek:")
        raise HTTPException(status_code=500, detail=str(e))

async def query_deepseek(messages: list[dict]) -> str:
    """
    Sends messages to DeepSeek and returns assistant's content.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": "deepseek-coder:latest",
                    "messages": messages,
                    "stream": False,
                },
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "")
    except Exception as e:
        raise RuntimeError(f"Failed to reach DeepSeek: {e}")
