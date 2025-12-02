from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict
import json

router = APIRouter()

# Connection manager for WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.dashboard_connections: List[WebSocket] = []
        self.match_connections: Dict[int, List[WebSocket]] = {}

    async def connect_dashboard(self, websocket: WebSocket):
        await websocket.accept()
        self.dashboard_connections.append(websocket)

    def disconnect_dashboard(self, websocket: WebSocket):
        self.dashboard_connections.remove(websocket)

    async def connect_match(self, match_id: int, websocket: WebSocket):
        await websocket.accept()
        if match_id not in self.match_connections:
            self.match_connections[match_id] = []
        self.match_connections[match_id].append(websocket)

    def disconnect_match(self, match_id: int, websocket: WebSocket):
        if match_id in self.match_connections:
            self.match_connections[match_id].remove(websocket)
            if not self.match_connections[match_id]:
                del self.match_connections[match_id]

    async def broadcast_to_dashboard(self, message: dict):
        """Broadcast message to all dashboard connections."""
        disconnected = []
        for connection in self.dashboard_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            self.dashboard_connections.remove(conn)

    async def broadcast_to_match(self, match_id: int, message: dict):
        """Broadcast message to all connections for a specific match."""
        if match_id not in self.match_connections:
            return

        disconnected = []
        for connection in self.match_connections[match_id]:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            self.match_connections[match_id].remove(conn)


manager = ConnectionManager()


@router.websocket("/ws/dashboard")
async def dashboard_websocket(websocket: WebSocket):
    """WebSocket endpoint for live dashboard updates."""
    await manager.connect_dashboard(websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Echo back to confirm connection
            await websocket.send_json({"type": "ping", "message": "pong"})
    except WebSocketDisconnect:
        manager.disconnect_dashboard(websocket)


@router.websocket("/ws/match/{match_id}")
async def match_websocket(websocket: WebSocket, match_id: int):
    """WebSocket endpoint for match-specific updates."""
    await manager.connect_match(match_id, websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Echo back to confirm connection
            await websocket.send_json({"type": "ping", "message": "pong"})
    except WebSocketDisconnect:
        manager.disconnect_match(match_id, websocket)


# Helper functions to broadcast events (called from services)
async def broadcast_health_update(match_id: int, player_id: int, new_health: int):
    """Broadcast health update to dashboard and match connections."""
    message = {
        "type": "health_update",
        "match_id": match_id,
        "player_id": player_id,
        "new_health": new_health
    }
    await manager.broadcast_to_dashboard(message)
    await manager.broadcast_to_match(match_id, {
        "type": "health_update",
        "your_health": new_health
    })


async def broadcast_match_complete(match_id: int, winner_id: int):
    """Broadcast match completion."""
    message = {
        "type": "match_complete",
        "match_id": match_id,
        "winner_id": winner_id
    }
    await manager.broadcast_to_dashboard(message)
    await manager.broadcast_to_match(match_id, {
        "type": "match_end",
        "winner_id": winner_id
    })


async def broadcast_round_complete(round_number: int):
    """Broadcast round completion."""
    message = {
        "type": "round_complete",
        "round_number": round_number
    }
    await manager.broadcast_to_dashboard(message)
