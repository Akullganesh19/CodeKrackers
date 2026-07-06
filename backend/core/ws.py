"""
Production-grade WebSocket connection manager with heartbeat and cleanup.
"""
import asyncio
import logging
import json
from datetime import datetime, timezone
from typing import List
from fastapi import WebSocket

logger = logging.getLogger("vas.ws")


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)
        logger.info("WS client connected. Total: %d", len(self.active_connections))

    async def disconnect(self, websocket: WebSocket):
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
        logger.info("WS client disconnected. Total: %d", len(self.active_connections))

    async def broadcast(self, message: dict):
        """Broadcast to all clients, cleaning up dead connections."""
        dead: List[WebSocket] = []
        payload = json.dumps(message, default=str)

        for connection in self.active_connections:
            try:
                await connection.send_text(payload)
            except Exception:
                dead.append(connection)

        # Cleanup dead connections
        if dead:
            async with self._lock:
                for ws in dead:
                    if ws in self.active_connections:
                        self.active_connections.remove(ws)
            logger.warning("Cleaned up %d dead WS connections", len(dead))

    @property
    def client_count(self) -> int:
        return len(self.active_connections)


manager = ConnectionManager()
