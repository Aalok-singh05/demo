"""WebSocket connection manager for real-time updates."""
from fastapi import WebSocket
from datetime import datetime
import json
from typing import Any


class ConnectionManager:
    """Manages active WebSocket connections and broadcasts events."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.chat_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket, channel: str = "activity"):
        await websocket.accept()
        if channel == "chat":
            self.chat_connections.append(websocket)
        else:
            self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket, channel: str = "activity"):
        if channel == "chat":
            if websocket in self.chat_connections:
                self.chat_connections.remove(websocket)
        else:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)

    async def broadcast(self, event_type: str, data: Any):
        """Broadcast an event to all connected activity clients."""
        message = json.dumps({
            "type": event_type,
            "data": data if isinstance(data, dict) else data,
            "timestamp": datetime.now().strftime("%I:%M %p")
        })
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            self.active_connections.remove(conn)

    async def send_chat(self, message: str):
        """Send a chat response to all connected chat clients."""
        disconnected = []
        for connection in self.chat_connections:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            self.chat_connections.remove(conn)


# Global manager instance
manager = ConnectionManager()
