"""
WebSocket client for real-time communication with Django backend
Replaces file-based pause/resume with instant WebSocket messaging
"""

import asyncio
import websockets
import json
import logging
import threading
from datetime import datetime
from typing import Dict, Any, Callable, Optional
import queue

class AlgorithmWebSocketClient:
    """WebSocket client for algorithm communication with backend"""
    
    def __init__(self, backend_url: str, algorithm_id: str, auth_token: str):
        self.backend_url = backend_url.replace('http://', 'ws://').replace('https://', 'wss://')
        self.algorithm_id = algorithm_id
        self.auth_token = auth_token
        self.websocket = None
        self.is_connected = False
        self.is_running = True
        self.message_handlers = {}
        self.outbound_queue = queue.Queue()
        self.logger = logging.getLogger(f'WebSocket-{algorithm_id}')
        
        # Event callbacks
        self.on_connect_callback = None
        self.on_disconnect_callback = None
        self.on_error_callback = None
        
        # Start background thread for message handling
        self.thread = threading.Thread(target=self._run_client, daemon=True)
        
    def start(self):
        """Start the WebSocket client"""
        self.logger.info(f"Starting WebSocket client for algorithm {self.algorithm_id}")
        self.thread.start()
        
    def stop(self):
        """Stop the WebSocket client"""
        self.logger.info(f"Stopping WebSocket client for algorithm {self.algorithm_id}")
        self.is_running = False
        if self.websocket:
            asyncio.create_task(self.websocket.close())
    
    def send_message(self, message_type: str, data: Dict[str, Any]):
        """Queue a message to be sent to the backend"""
        message = {
            'type': message_type,
            'algorithm_id': self.algorithm_id,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        self.outbound_queue.put(message)
        
    def register_handler(self, message_type: str, handler: Callable):
        """Register a handler for incoming messages"""
        self.message_handlers[message_type] = handler
        
    def set_callbacks(self, on_connect=None, on_disconnect=None, on_error=None):
        """Set event callbacks"""
        self.on_connect_callback = on_connect
        self.on_disconnect_callback = on_disconnect
        self.on_error_callback = on_error
    
    def _run_client(self):
        """Run the WebSocket client in background thread"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self._connect_and_listen())
        except Exception as e:
            self.logger.error(f"WebSocket client error: {e}")
            if self.on_error_callback:
                self.on_error_callback(e)
        finally:
            loop.close()
    
    async def _connect_and_listen(self):
        """Connect to WebSocket and listen for messages"""
        uri = f"{self.backend_url}/ws/algorithm/{self.algorithm_id}/"
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        while self.is_running:
            try:
                self.logger.info(f"Connecting to {uri}")
                async with websockets.connect(uri, extra_headers=headers) as websocket:
                    self.websocket = websocket
                    self.is_connected = True
                    self.logger.info("WebSocket connected successfully")
                    
                    if self.on_connect_callback:
                        self.on_connect_callback()
                    
                    # Start message sender task
                    sender_task = asyncio.create_task(self._message_sender())
                    
                    try:
                        # Listen for incoming messages
                        async for message in websocket:
                            await self._handle_incoming_message(message)
                    except websockets.exceptions.ConnectionClosed:
                        self.logger.warning("WebSocket connection closed")
                    finally:
                        sender_task.cancel()
                        self.is_connected = False
                        if self.on_disconnect_callback:
                            self.on_disconnect_callback()
                        
            except Exception as e:
                self.logger.error(f"WebSocket connection error: {e}")
                self.is_connected = False
                
                if self.on_error_callback:
                    self.on_error_callback(e)
                
                # Wait before reconnecting
                if self.is_running:
                    await asyncio.sleep(5)
    
    async def _message_sender(self):
        """Send queued messages to backend"""
        while self.is_connected and self.is_running:
            try:
                # Get message from queue (non-blocking)
                message = self.outbound_queue.get_nowait()
                await self.websocket.send(json.dumps(message))
                self.logger.debug(f"Sent message: {message['type']}")
            except queue.Empty:
                await asyncio.sleep(0.1)  # Brief pause if no messages
            except Exception as e:
                self.logger.error(f"Error sending message: {e}")
                break
    
    async def _handle_incoming_message(self, message_data: str):
        """Handle incoming WebSocket messages"""
        try:
            message = json.loads(message_data)
            message_type = message.get('type')
            
            self.logger.debug(f"Received message: {message_type}")
            
            # Call registered handler if available
            if message_type in self.message_handlers:
                handler = self.message_handlers[message_type]
                if asyncio.iscoroutinefunction(handler):
                    await handler(message)
                else:
                    handler(message)
            else:
                self.logger.warning(f"No handler for message type: {message_type}")
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON received: {e}")
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")


class AlgorithmStatusReporter:
    """Helper class for reporting algorithm status to backend"""
    
    def __init__(self, websocket_client: AlgorithmWebSocketClient):
        self.client = websocket_client
        self.logger = logging.getLogger(f'StatusReporter-{websocket_client.algorithm_id}')
        
    def report_status_update(self, status: str, message: str = "", data: Dict[str, Any] = None):
        """Report algorithm status change"""
        status_data = {
            'status': status,
            'message': message,
            'data': data or {}
        }
        self.client.send_message('status_update', status_data)
        self.logger.info(f"Status update: {status} - {message}")
    
    def report_trade_opened(self, trade_data: Dict[str, Any]):
        """Report new trade opened"""
        self.client.send_message('trade_opened', trade_data)
        self.logger.info(f"Trade opened: {trade_data.get('symbol')} {trade_data.get('type')}")
    
    def report_trade_closed(self, trade_data: Dict[str, Any]):
        """Report trade closed"""
        self.client.send_message('trade_closed', trade_data)
        self.logger.info(f"Trade closed: {trade_data.get('symbol')} P&L: {trade_data.get('profit')}")
    
    def report_signal_generated(self, signal_data: Dict[str, Any]):
        """Report trading signal generated"""
        self.client.send_message('signal_generated', signal_data)
        self.logger.info(f"Signal: {signal_data.get('action')} {signal_data.get('symbol')}")
    
    def report_error(self, error_message: str, error_data: Dict[str, Any] = None):
        """Report algorithm error"""
        error_data = {
            'error_message': error_message,
            'data': error_data or {}
        }
        self.client.send_message('error_occurred', error_data)
        self.logger.error(f"Error reported: {error_message}")
    
    def report_heartbeat(self, performance_data: Dict[str, Any] = None):
        """Send heartbeat with current performance data"""
        heartbeat_data = {
            'timestamp': datetime.now().isoformat(),
            'performance': performance_data or {}
        }
        self.client.send_message('heartbeat', heartbeat_data)


class AlgorithmCommandHandler:
    """Handle commands received from backend"""
    
    def __init__(self):
        self.command_handlers = {}
        self.logger = logging.getLogger('CommandHandler')
        
    def register_command_handler(self, command: str, handler: Callable):
        """Register a handler for specific command"""
        self.command_handlers[command] = handler
        
    async def handle_command(self, message: Dict[str, Any]):
        """Handle incoming command message"""
        command = message.get('data', {}).get('command')
        if command in self.command_handlers:
            try:
                handler = self.command_handlers[command]
                if asyncio.iscoroutinefunction(handler):
                    await handler(message['data'])
                else:
                    handler(message['data'])
                self.logger.info(f"Executed command: {command}")
            except Exception as e:
                self.logger.error(f"Error executing command {command}: {e}")
        else:
            self.logger.warning(f"Unknown command: {command}")


def create_algorithm_websocket_client(backend_url: str, algorithm_id: str, 
                                    auth_token: str) -> tuple[AlgorithmWebSocketClient, 
                                                              AlgorithmStatusReporter, 
                                                              AlgorithmCommandHandler]:
    """Factory function to create complete WebSocket setup"""
    
    # Create WebSocket client
    client = AlgorithmWebSocketClient(backend_url, algorithm_id, auth_token)
    
    # Create status reporter
    status_reporter = AlgorithmStatusReporter(client)
    
    # Create command handler
    command_handler = AlgorithmCommandHandler()
    
    # Register command handler with client
    client.register_handler('command', command_handler.handle_command)
    
    # Set up basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    return client, status_reporter, command_handler


# Example usage for EA integration
def setup_ea_websocket_integration(ea_instance, backend_url: str, algorithm_id: str, auth_token: str):
    """
    Example integration setup for EA instances
    This would be called from each EA's launcher
    """
    
    # Create WebSocket components
    ws_client, status_reporter, command_handler = create_algorithm_websocket_client(
        backend_url, algorithm_id, auth_token
    )
    
    # Set up EA-specific command handlers
    def pause_algorithm(data):
        ea_instance.pause_trading()
        status_reporter.report_status_update('paused', 'Algorithm paused by user command')
    
    def resume_algorithm(data):
        ea_instance.resume_trading()
        status_reporter.report_status_update('running', 'Algorithm resumed by user command')
    
    def stop_algorithm(data):
        ea_instance.stop_trading()
        status_reporter.report_status_update('stopped', 'Algorithm stopped by user command')
    
    def update_config(data):
        config_updates = data.get('config_updates', {})
        ea_instance.update_configuration(config_updates)
        status_reporter.report_status_update('running', 'Configuration updated')
    
    # Register command handlers
    command_handler.register_command_handler('pause', pause_algorithm)
    command_handler.register_command_handler('resume', resume_algorithm)
    command_handler.register_command_handler('stop', stop_algorithm)
    command_handler.register_command_handler('update_config', update_config)
    
    # Set up connection callbacks
    def on_connect():
        status_reporter.report_status_update('running', 'WebSocket connected')
    
    def on_disconnect():
        print(f"WebSocket disconnected for algorithm {algorithm_id}")
    
    def on_error(error):
        print(f"WebSocket error for algorithm {algorithm_id}: {error}")
    
    ws_client.set_callbacks(on_connect=on_connect, on_disconnect=on_disconnect, on_error=on_error)
    
    # Start WebSocket client
    ws_client.start()
    
    return ws_client, status_reporter, command_handler
