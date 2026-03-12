"""NEXUS Backend — FastAPI Entry Point.

Event Logistics Swarm backend with AI agent system.
Run with: python -m uvicorn app.main:app --reload --port 8000
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import json

from .config import settings
from .database import init_db
from .api.websocket import manager
from .api.routes.dashboard import router as dashboard_router
from .api.routes.schedule import router as schedule_router
from .api.routes.mail import router as mail_router
from .api.routes.content import router as content_router
from .api.routes.agents import router as agents_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    # Startup: initialize database + seed demo data
    print("🚀 NEXUS Backend starting...")
    await init_db()
    print(f"📦 Database initialized")
    print(f"🤖 LLM Available: {settings.LLM_AVAILABLE}")
    if not settings.LLM_AVAILABLE:
        print("⚠️  GEMINI_API_KEY not set — agents will use fallback responses")
    print("✅ NEXUS Backend ready!")
    yield
    # Shutdown
    print("👋 NEXUS Backend shutting down...")


app = FastAPI(
    title="NEXUS — Event Logistics Swarm",
    description="AI-powered multi-agent event management system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount REST routers
app.include_router(dashboard_router)
app.include_router(schedule_router)
app.include_router(mail_router)
app.include_router(content_router)
app.include_router(agents_router)


# ── WebSocket Endpoints ───────────────────────────────────

@app.websocket("/ws/activity")
async def websocket_activity(websocket: WebSocket):
    """Real-time activity feed stream."""
    await manager.connect(websocket, "activity")
    try:
        while True:
            try:
                data = await websocket.receive_text()
                # Client can send "ping" to keep alive
                if data == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except Exception:
                break
    except Exception:
        pass
    finally:
        manager.disconnect(websocket, "activity")


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """Meta-Agent (Nexus Core) chat interface."""
    from .agents.meta_agent import handle_chat_message
    from datetime import datetime

    await manager.connect(websocket, "chat")
    try:
        while True:
            try:
                data = await websocket.receive_text()
                msg = json.loads(data)
                user_message = msg.get("message", "")

                if user_message:
                    result = await handle_chat_message(user_message)
                    response = {
                        "type": "chat_response",
                        "data": {
                            "reply": result.reply,
                            "plan": result.plan,
                            "agents_involved": result.agents_involved,
                        },
                        "timestamp": datetime.now().strftime("%I:%M %p")
                    }
                    await websocket.send_text(json.dumps(response))

                    await manager.broadcast("agent_activity", {
                        "agent": "Nexus Core",
                        "action": "Chat Response",
                        "text": "Processed organizer request via command bar.",
                        "status": "done"
                    })
            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"[WS CHAT] Error: {e}")
                break
    except Exception:
        pass
    finally:
        manager.disconnect(websocket, "chat")


# ── Health Check ──────────────────────────────────────────

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "llm_available": settings.LLM_AVAILABLE,
        "agents": ["chronos", "hermes", "apollo", "athena", "nexus_core", "fortuna"]
    }
