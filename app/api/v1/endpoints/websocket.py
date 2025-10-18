"""
WebSocket endpoint for real-time spreadsheet collaboration
"""
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from fastapi.websockets import WebSocketState
import json
from datetime import datetime

from app.api.v1.endpoints.auth import get_current_active_user
from app.services.auth_service import AuthService
from app.services.spreadsheet_service import SpreadsheetService
from app.spreadsheet_schemas import WSCellUpdate, WSUserJoined, WSUserLeft, WSError
from app.models import User


router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections for spreadsheets"""
    
    def __init__(self):
        # spreadsheet_id -> set of websockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # websocket -> user_email
        self.user_mapping: Dict[WebSocket, str] = {}
    
    async def connect(self, websocket: WebSocket, spreadsheet_id: str, user_email: str):
        """Connect a user to a spreadsheet room"""
        await websocket.accept()
        
        if spreadsheet_id not in self.active_connections:
            self.active_connections[spreadsheet_id] = set()
        
        self.active_connections[spreadsheet_id].add(websocket)
        self.user_mapping[websocket] = user_email
    
    def disconnect(self, websocket: WebSocket, spreadsheet_id: str):
        """Disconnect a user from a spreadsheet room"""
        if spreadsheet_id in self.active_connections:
            self.active_connections[spreadsheet_id].discard(websocket)
            if not self.active_connections[spreadsheet_id]:
                del self.active_connections[spreadsheet_id]
        
        if websocket in self.user_mapping:
            del self.user_mapping[websocket]
    
    async def broadcast(self, spreadsheet_id: str, message: dict, exclude: WebSocket = None):
        """Broadcast message to all users in a spreadsheet room"""
        if spreadsheet_id not in self.active_connections:
            return
        
        # Create list of connections to avoid modification during iteration
        connections = list(self.active_connections[spreadsheet_id])
        
        for connection in connections:
            if connection != exclude and connection.client_state == WebSocketState.CONNECTED:
                try:
                    await connection.send_json(message)
                except Exception:
                    # Remove dead connections
                    self.disconnect(connection, spreadsheet_id)
    
    def get_users_in_room(self, spreadsheet_id: str) -> Set[str]:
        """Get all users currently in a spreadsheet room"""
        if spreadsheet_id not in self.active_connections:
            return set()
        
        return {
            self.user_mapping[ws]
            for ws in self.active_connections[spreadsheet_id]
            if ws in self.user_mapping
        }


manager = ConnectionManager()


@router.websocket("/ws/spreadsheets/{spreadsheet_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    spreadsheet_id: str,
    token: str = Query(...)
):
    """
    WebSocket endpoint for real-time collaboration
    
    Connect with: ws://localhost:7878/api/v1/ws/spreadsheets/{spreadsheet_id}?token={jwt_token}
    """
    try:
        # Verify token and get user
        user = await AuthService.get_current_user_from_token(token)
        
        # Verify user has access to this spreadsheet
        try:
            await SpreadsheetService.get_spreadsheet(spreadsheet_id, user)
        except Exception as e:
            await websocket.close(code=1008, reason="Access denied")
            return
        
        # Connect user
        await manager.connect(websocket, spreadsheet_id, user.email)
        
        # Notify others that user joined
        join_message = WSUserJoined(
            spreadsheet_id=spreadsheet_id,
            user_email=user.email
        )
        await manager.broadcast(
            spreadsheet_id,
            join_message.model_dump(),
            exclude=websocket
        )
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                msg_type = message.get("type")
                
                if msg_type == "cell_update":
                    # Broadcast cell update to all other users
                    cell_update = WSCellUpdate(
                        spreadsheet_id=spreadsheet_id,
                        cell=message.get("cell"),
                        user_email=user.email,
                        version=message.get("version", 0)
                    )
                    await manager.broadcast(
                        spreadsheet_id,
                        cell_update.model_dump(),
                        exclude=websocket
                    )
                
                elif msg_type == "ping":
                    # Keep-alive
                    await websocket.send_json({"type": "pong"})
        
        except WebSocketDisconnect:
            # User disconnected
            manager.disconnect(websocket, spreadsheet_id)
            
            # Notify others that user left
            left_message = WSUserLeft(
                spreadsheet_id=spreadsheet_id,
                user_email=user.email
            )
            await manager.broadcast(
                spreadsheet_id,
                left_message.model_dump()
            )
    
    except Exception as e:
        # Handle errors
        try:
            error_message = WSError(
                spreadsheet_id=spreadsheet_id,
                message=str(e)
            )
            await websocket.send_json(error_message.model_dump())
            await websocket.close(code=1011, reason=str(e))
        except:
            pass


@router.get("/ws/spreadsheets/{spreadsheet_id}/users")
async def get_active_users(
    spreadsheet_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get list of users currently connected to a spreadsheet"""
    # Verify access
    await SpreadsheetService.get_spreadsheet(spreadsheet_id, current_user)
    
    users = manager.get_users_in_room(spreadsheet_id)
    return {"users": list(users)}
