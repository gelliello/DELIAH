from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import json

from backend.core.ai_engine import AIEngine
from backend.core.model_router import TaskType
from backend.core.task_manager import TaskManager
from backend.personality.traits import PersonalityEngine
from backend.memory.memory_manager import MemoryManager

app = FastAPI(title="DELIAH Core", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ai_engine = AIEngine()
task_manager = TaskManager()
personality = PersonalityEngine()
memory = MemoryManager()


class ChatRequest(BaseModel):
    message: str
    task_type: Optional[str] = None
    mode: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    task_type: str
    model: str


class MemoryRequest(BaseModel):
    key: str
    value: str
    category: str = "general"


class MemorySearchRequest(BaseModel):
    query: str
    category: Optional[str] = None


@app.get("/")
async def root():
    return {"name": "DELIAH", "version": "0.1.0", "status": "active"}


@app.get("/health")
async def health():
    ollama_ok = await ai_engine.check_connection()
    return {
        "status": "healthy" if ollama_ok else "degraded",
        "ollama": "connected" if ollama_ok else "disconnected",
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    task_type = None
    if request.task_type:
        try:
            task_type = TaskType(request.task_type)
        except ValueError:
            pass

    if request.mode:
        mode_map = {
            "coding": TaskType.CODING,
            "planning": TaskType.PLANNING,
            "general": TaskType.GENERAL,
        }
        task_type = mode_map.get(request.mode, TaskType.GENERAL)

    personality_prompt = personality.get_prompt()
    reply = await ai_engine.process_message(
        request.message, task_type=task_type, personality_prompt=personality_prompt
    )

    detected_type = task_type or ai_engine.router.classify_task(request.message)
    model = ai_engine.router.get_model(detected_type)

    await memory.store(
        key=f"chat_{len(memory.get_all())}",
        value=f"User: {request.message}\nDELIAH: {reply}",
        category="conversations",
    )

    return ChatResponse(
        reply=reply,
        task_type=detected_type.value,
        model=model,
    )


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            message = message_data.get("message", "")

            personality_prompt = personality.get_prompt()

            async for chunk in ai_engine.stream_message(
                message, personality_prompt=personality_prompt
            ):
                await websocket.send_text(
                    json.dumps({"type": "chunk", "content": chunk})
                )

            await websocket.send_text(json.dumps({"type": "done"}))
    except WebSocketDisconnect:
        pass


@app.get("/memory")
async def get_memory(category: Optional[str] = None):
    if category:
        return memory.get_by_category(category)
    return memory.get_all()


@app.post("/memory")
async def store_memory(request: MemoryRequest):
    memory.store(key=request.key, value=request.value, category=request.category)
    return {"status": "stored"}


@app.post("/memory/search")
async def search_memory(request: MemorySearchRequest):
    results = memory.search(request.query, category=request.category)
    return {"results": results}


@app.get("/personality")
async def get_personality():
    return personality.get_info()


@app.get("/models")
async def get_models():
    models = await ai_engine.list_models()
    configured = ai_engine.router.get_all_models()
    return {"available": models, "configured": configured}


@app.get("/tasks")
async def get_tasks():
    return {"tasks": task_manager.get_all_tasks()}


@app.post("/chat/clear")
async def clear_chat():
    ai_engine.clear_history()
    return {"status": "cleared"}
