# app/core/broadcast.py
from typing import List
from fastapi import WebSocket

active_connections: List[WebSocket] = []

async def connect(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)

async def disconnect(websocket: WebSocket):
    if websocket in active_connections:
        active_connections.remove(websocket)

async def broadcast_resolution(incident_id: str):
    for connection in active_connections:
        await connection.send_json({"type": "resolution", "incident_id": incident_id})
