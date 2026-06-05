from __future__ import annotations

import asyncio
import json
from typing import Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.utils.logger import logger

router = APIRouter()

# Global set of active WebSocket connections
active_connections: Set[WebSocket] = set()

@router.websocket("/ws/attendance")
async def attendance_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time attendance event streaming.
    Frontend connects here to receive instant attendance notifications.
    """
    await websocket.accept()
    active_connections.add(websocket)
    logger.info("event=websocket_connected total_connections=%s", len(active_connections))
    
    try:
        while True:
            # Keep connection alive — wait for client pings
            data = await websocket.receive_text()
            # Client can send "ping" to keep alive
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        active_connections.discard(websocket)
        logger.info("event=websocket_disconnected total_connections=%s", len(active_connections))


async def broadcast_attendance_event(event: dict):
    """
    Broadcast an attendance event to all connected WebSocket clients.
    Called from the /verify endpoint after successful attendance marking.
    """
    if not active_connections:
        return
    
    message = json.dumps(event)
    disconnected = set()
    
    for connection in active_connections:
        try:
            await connection.send_text(message)
        except Exception:
            disconnected.add(connection)
    
    active_connections.difference_update(disconnected)
