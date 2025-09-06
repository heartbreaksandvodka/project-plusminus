"""
WebSocket Manager for real-time EA communication
Handles WebSocket connections and real-time messaging
"""

import asyncio
import json
import logging
from typing import Dict, Set, Optional
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect

from models import WebSocketMessage, ExecutionStatus

logger = logging.getLogger(__name__)

class WebSocketConnection:
    """Represents a WebSocket connection"""
    
    def __init__(self, websocket: WebSocket, execution_id: str):
        self.websocket = websocket
        self.execution_id = execution_id
        self.connected_at = datetime.now()
        self.last_ping = datetime.now()

class WebSocketManager:
    """Manages WebSocket connections for EA real-time communication"""
    
    def __init__(self):
        # execution_id -> set of WebSocketConnection
        self.connections: Dict[str, Set[WebSocketConnection]] = {}
        self._ping_task: Optional[asyncio.Task] = None
        
    async def initialize(self):
        """Initialize WebSocket manager"""
        self._ping_task = asyncio.create_task(self._ping_connections())
        logger.info("WebSocket manager initialized")
    
    async def cleanup(self):
        """Cleanup WebSocket manager"""
        if self._ping_task:
            self._ping_task.cancel()
        
        # Close all connections
        for connections in self.connections.values():
            for conn in connections.copy():
                try:
                    await conn.websocket.close()
                except:
                    pass
        
        self.connections.clear()
        logger.info("WebSocket manager cleaned up")
    
    async def handle_connection(self, websocket: WebSocket, execution_id: str):
        """Handle a new WebSocket connection"""
        connection = WebSocketConnection(websocket, execution_id)
        
        # Add to connections
        if execution_id not in self.connections:
            self.connections[execution_id] = set()
        self.connections[execution_id].add(connection)
        
        logger.info(f"WebSocket connected for execution {execution_id}")
        
        try:
            # Send initial status
            await self._send_message(connection, WebSocketMessage(
                type="connected",
                execution_id=execution_id,
                data={"message": "WebSocket connected successfully"}
            ))
            
            # Handle incoming messages
            async for message in websocket.iter_text():
                await self._handle_incoming_message(connection, message)
        
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for execution {execution_id}")
        except Exception as e:
            logger.error(f"WebSocket error for execution {execution_id}: {e}")
        finally:
            # Remove connection
            if execution_id in self.connections:
                self.connections[execution_id].discard(connection)
                if not self.connections[execution_id]:
                    del self.connections[execution_id]
    
    async def broadcast_to_execution(self, execution_id: str, message: WebSocketMessage):
        """Broadcast message to all connections for an execution"""
        if execution_id not in self.connections:
            return
        
        connections = self.connections[execution_id].copy()
        for connection in connections:
            try:
                await self._send_message(connection, message)
            except Exception as e:
                logger.error(f"Error sending message to connection: {e}")
                # Remove failed connection
                self.connections[execution_id].discard(connection)
    
    async def send_status_update(self, execution_id: str, status: ExecutionStatus, 
                               data: Optional[Dict] = None):
        """Send status update to connections"""
        message = WebSocketMessage(
            type="status_update",
            execution_id=execution_id,
            data={
                "status": status.value,
                "timestamp": datetime.now().isoformat(),
                **(data or {})
            }
        )
        await self.broadcast_to_execution(execution_id, message)
    
    async def send_trade_update(self, execution_id: str, trade_data: Dict):
        """Send trade update to connections"""
        message = WebSocketMessage(
            type="trade_update",
            execution_id=execution_id,
            data=trade_data
        )
        await self.broadcast_to_execution(execution_id, message)
    
    async def send_performance_update(self, execution_id: str, performance_data: Dict):
        """Send performance update to connections"""
        message = WebSocketMessage(
            type="performance_update",
            execution_id=execution_id,
            data=performance_data
        )
        await self.broadcast_to_execution(execution_id, message)
    
    async def send_error_message(self, execution_id: str, error_message: str):
        """Send error message to connections"""
        message = WebSocketMessage(
            type="error",
            execution_id=execution_id,
            data={
                "error": error_message,
                "timestamp": datetime.now().isoformat()
            }
        )
        await self.broadcast_to_execution(execution_id, message)
    
    async def setup_ea_monitoring(self, execution_id: str, pid: int):
        """Set up monitoring for a new EA execution"""
        # This could be extended to set up specific monitoring
        # for the EA process, like log tailing, performance metrics, etc.
        logger.info(f"Setting up monitoring for execution {execution_id} (PID: {pid})")
        
        # Send initial monitoring setup message
        message = WebSocketMessage(
            type="monitoring_started",
            execution_id=execution_id,
            data={
                "pid": pid,
                "message": "Real-time monitoring started"
            }
        )
        await self.broadcast_to_execution(execution_id, message)
    
    async def _send_message(self, connection: WebSocketConnection, message: WebSocketMessage):
        """Send message to a specific connection"""
        try:
            await connection.websocket.send_text(message.model_dump_json())
            connection.last_ping = datetime.now()
        except Exception as e:
            logger.error(f"Failed to send WebSocket message: {e}")
            raise
    
    async def _handle_incoming_message(self, connection: WebSocketConnection, message_str: str):
        """Handle incoming message from WebSocket client"""
        try:
            message_data = json.loads(message_str)
            message_type = message_data.get('type')
            
            if message_type == 'ping':
                # Respond to ping
                pong_message = WebSocketMessage(
                    type="pong",
                    execution_id=connection.execution_id,
                    data={"timestamp": datetime.now().isoformat()}
                )
                await self._send_message(connection, pong_message)
            
            elif message_type == 'get_status':
                # Client requesting current status
                # This could be extended to fetch current EA status
                status_message = WebSocketMessage(
                    type="status_response",
                    execution_id=connection.execution_id,
                    data={"requested_at": datetime.now().isoformat()}
                )
                await self._send_message(connection, status_message)
            
            else:
                logger.warning(f"Unknown message type: {message_type}")
        
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON message received: {message_str}")
        except Exception as e:
            logger.error(f"Error handling incoming message: {e}")
    
    async def _ping_connections(self):
        """Periodically ping connections to keep them alive"""
        while True:
            try:
                await asyncio.sleep(30)  # Ping every 30 seconds
                
                for execution_id, connections in self.connections.items():
                    for connection in connections.copy():
                        try:
                            ping_message = WebSocketMessage(
                                type="ping",
                                execution_id=execution_id,
                                data={"timestamp": datetime.now().isoformat()}
                            )
                            await self._send_message(connection, ping_message)
                        except Exception as e:
                            logger.error(f"Error pinging connection: {e}")
                            # Remove failed connection
                            connections.discard(connection)
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in ping task: {e}")
