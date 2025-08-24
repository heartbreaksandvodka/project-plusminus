import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
from .models import AlgorithmExecution, TradeResult, AlgorithmSignal, MT5Account
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class AlgorithmWebSocketConsumer(AsyncWebsocketConsumer):
    """Handle WebSocket connections from running algorithms"""

    async def connect(self):
        """Handle WebSocket connection"""
        self.user = None
        self.algorithm_name = self.scope['url_route']['kwargs'].get('algorithm_name')
        self.execution_id = self.scope['url_route']['kwargs'].get('execution_id')
        
        # Get authentication token from multiple sources
        token = self.get_auth_token()
        
        if token:
            self.user = await self.get_user_from_token(token)
        
        if not self.user:
            await self.close()
            return
        
        # Join user-specific group for broadcasting
        self.group_name = f'user_{self.user.id}_algorithms'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        
        # Join algorithm-specific group if execution_id provided
        if self.execution_id:
            self.algorithm_group = f'algorithm_{self.execution_id}'
            await self.channel_layer.group_add(self.algorithm_group, self.channel_name)
        
        await self.accept()
        logger.info(f"WebSocket connected for user {self.user.id}, algorithm: {self.algorithm_name}")

    def get_auth_token(self):
        """
        Extract authentication token from various sources:
        1. Authorization header (Bearer token)
        2. Query string parameter (token=...)
        3. Subprotocol (for some WebSocket clients)
        """
        # Check Authorization header first
        headers = dict(self.scope.get('headers', []))
        auth_header = headers.get(b'authorization', b'').decode()
        
        if auth_header.startswith('Bearer '):
            return auth_header[7:]  # Remove 'Bearer ' prefix
        
        # Check query string
        query_string = self.scope['query_string'].decode()
        for param in query_string.split('&'):
            if param.startswith('token='):
                return param.split('=')[1]
        
        # Check subprotocols (some WebSocket clients use this)
        subprotocols = self.scope.get('subprotocols', [])
        for protocol in subprotocols:
            if protocol.startswith('token.'):
                return protocol[6:]  # Remove 'token.' prefix
        
        return None

    def get_client_ip(self):
        """
        Extract client IP address from WebSocket scope
        Returns a valid IP address or defaults to localhost
        """
        # Try different sources for IP address
        # 1. X-Forwarded-For header (for proxied connections)
        headers = dict(self.scope.get('headers', []))
        forwarded_for = headers.get(b'x-forwarded-for', b'').decode()
        if forwarded_for:
            # Take the first IP if multiple are present
            return forwarded_for.split(',')[0].strip()
        
        # 2. X-Real-IP header
        real_ip = headers.get(b'x-real-ip', b'').decode()
        if real_ip:
            return real_ip
        
        # 3. Client info from scope
        client = self.scope.get('client')
        if client and len(client) >= 1:
            client_host = client[0]
            if client_host and client_host != 'unknown':
                return client_host
        
        # 4. Server info as fallback (for localhost connections)
        server = self.scope.get('server')
        if server and len(server) >= 1:
            server_host = server[0]
            if server_host:
                return server_host
        
        # Default fallback
        return '127.0.0.1'

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        
        if hasattr(self, 'algorithm_group'):
            await self.channel_layer.group_discard(self.algorithm_group, self.channel_name)
        
        # Handle EA connection log cleanup
        if hasattr(self, 'connection_log') and self.connection_log:
            await self.cleanup_connection_log(close_code)
        
        logger.info(f"WebSocket disconnected for user {getattr(self.user, 'id', 'unknown')}")

    @database_sync_to_async
    def cleanup_connection_log(self, close_code):
        """Mark EA connection as disconnected"""
        try:
            if hasattr(self, 'connection_log') and self.connection_log:
                reason = f"WebSocket closed with code {close_code}"
                self.connection_log.mark_disconnected(reason)
        except Exception as e:
            logger.error(f"Error cleaning up connection log: {e}")

    async def receive(self, text_data):
        """Process messages from algorithms or frontend"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            logger.info(f"Received WebSocket message: {message_type}")
            
            if message_type == 'status_update':
                await self.handle_status_update(data)
            elif message_type == 'trade_update':
                await self.handle_trade_update(data)
            elif message_type == 'signal_generated':
                await self.handle_signal_generated(data)
            elif message_type == 'error':
                await self.handle_error(data)
            elif message_type == 'heartbeat':
                await self.handle_heartbeat(data)
            elif message_type == 'performance_update':
                await self.handle_performance_update(data)
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {str(e)}")

    async def handle_status_update(self, data):
        """Handle algorithm status updates"""
        try:
            execution_id = data.get('execution_id')
            status = data.get('status')
            
            if execution_id:
                await self.update_execution_status(execution_id, data)
            
            # Broadcast to all clients of this user
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'algorithm_status',
                    'message': {
                        'type': 'status_update',
                        'execution_id': execution_id,
                        'algorithm_name': data.get('algorithm_name'),
                        'status': status,
                        'timestamp': datetime.now().isoformat(),
                        'data': data.get('data', {})
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"Error handling status update: {str(e)}")

    async def handle_trade_update(self, data):
        """Handle new trade results"""
        try:
            execution_id = data.get('execution_id')
            trade_data = data.get('trade_data', {})
            
            if execution_id and trade_data:
                # Save trade result to database
                await self.save_trade_result(execution_id, trade_data)
            
            # Broadcast to frontend
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'trade_notification',
                    'message': {
                        'type': 'trade_update',
                        'execution_id': execution_id,
                        'trade_data': trade_data,
                        'timestamp': datetime.now().isoformat()
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"Error handling trade update: {str(e)}")

    async def handle_signal_generated(self, data):
        """Handle trading signal generation"""
        try:
            execution_id = data.get('execution_id')
            signal_data = data.get('signal_data', {})
            
            if execution_id and signal_data:
                # Save signal to database
                await self.save_algorithm_signal(execution_id, signal_data)
            
            # Broadcast to frontend
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'signal_notification',
                    'message': {
                        'type': 'signal_generated',
                        'execution_id': execution_id,
                        'signal_data': signal_data,
                        'timestamp': datetime.now().isoformat()
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"Error handling signal: {str(e)}")

    async def handle_performance_update(self, data):
        """Handle performance metrics updates"""
        try:
            execution_id = data.get('execution_id')
            performance_data = data.get('performance_data', {})
            
            if execution_id:
                await self.update_performance_metrics(execution_id, performance_data)
            
            # Broadcast to frontend
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'performance_update',
                    'message': {
                        'type': 'performance_update',
                        'execution_id': execution_id,
                        'performance_data': performance_data,
                        'timestamp': datetime.now().isoformat()
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"Error handling performance update: {str(e)}")

    async def handle_error(self, data):
        """Handle error messages from algorithms"""
        try:
            execution_id = data.get('execution_id')
            error_message = data.get('error_message', '')
            
            if execution_id:
                await self.update_execution_error(execution_id, error_message)
            
            # Broadcast error to frontend
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'error_notification',
                    'message': {
                        'type': 'error',
                        'execution_id': execution_id,
                        'error_message': error_message,
                        'timestamp': datetime.now().isoformat()
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"Error handling error message: {str(e)}")

    async def handle_heartbeat(self, data):
        """Handle heartbeat messages from algorithms"""
        try:
            execution_id = data.get('execution_id')
            
            if execution_id:
                await self.update_heartbeat(execution_id)
            
        except Exception as e:
            logger.error(f"Error handling heartbeat: {str(e)}")

    # Message handlers for broadcasting to WebSocket clients
    async def algorithm_status(self, event):
        """Send algorithm status to WebSocket"""
        await self.send(text_data=json.dumps(event['message']))

    async def trade_notification(self, event):
        """Send trade notification to WebSocket"""
        await self.send(text_data=json.dumps(event['message']))

    async def signal_notification(self, event):
        """Send signal notification to WebSocket"""
        await self.send(text_data=json.dumps(event['message']))

    async def performance_update(self, event):
        """Send performance update to WebSocket"""
        await self.send(text_data=json.dumps(event['message']))

    async def error_notification(self, event):
        """Send error notification to WebSocket"""
        await self.send(text_data=json.dumps(event['message']))

    # Database operations
    @database_sync_to_async
    def get_user_from_token(self, token):
        """
        Get user from JWT token or EA token
        Returns (user, token_type, token_object) tuple
        """
        try:
            # First try EA token authentication
            from authentication.ea_models import EAAuthToken
            ea_token = EAAuthToken.validate_token(token)
            if ea_token:
                # Mark token as used and get client IP
                client_ip = self.get_client_ip()
                ea_token.mark_used(client_ip)
                
                # Create connection log
                from authentication.ea_models import EAConnectionLog
                connection_log = EAConnectionLog.objects.create(
                    ea_token=ea_token,
                    ip_address=client_ip,
                    user_agent=''  # Will be set later if available
                )
                
                # Store for cleanup on disconnect
                self.connection_log = connection_log
                self.ea_token = ea_token
                self.token_type = 'ea_token'
                
                return ea_token.user
            
            # Fallback to JWT token authentication
            UntypedToken(token)
            from rest_framework_simplejwt.authentication import JWTAuthentication
            jwt_auth = JWTAuthentication()
            validated_token = jwt_auth.get_validated_token(token)
            user = jwt_auth.get_user(validated_token)
            
            if user and not isinstance(user, AnonymousUser):
                self.token_type = 'jwt_token'
                return user
            
            return None
            
        except (InvalidToken, TokenError):
            return None

    @database_sync_to_async
    def update_execution_status(self, execution_id, data):
        """Update algorithm execution status"""
        try:
            execution = AlgorithmExecution.objects.get(id=execution_id)
            execution.execution_status = data.get('status', execution.execution_status)
            execution.last_heartbeat = datetime.now()
            execution.positions_count = data.get('positions_count', execution.positions_count)
            execution.daily_pnl = data.get('daily_pnl', execution.daily_pnl)
            execution.current_positions = data.get('current_positions', execution.current_positions)
            execution.save()
        except AlgorithmExecution.DoesNotExist:
            logger.error(f"Execution {execution_id} not found")

    @database_sync_to_async
    def save_trade_result(self, execution_id, trade_data):
        """Save trade result to database"""
        try:
            execution = AlgorithmExecution.objects.get(id=execution_id)
            
            trade_result = TradeResult.objects.create(
                execution=execution,
                mt5_position_id=trade_data.get('position_id'),
                trade_type=trade_data.get('trade_type'),
                symbol=trade_data.get('symbol'),
                volume=trade_data.get('volume', 0),
                open_price=trade_data.get('open_price', 0),
                close_price=trade_data.get('close_price'),
                stop_loss=trade_data.get('stop_loss'),
                take_profit=trade_data.get('take_profit'),
                profit_loss=trade_data.get('profit_loss', 0),
                commission=trade_data.get('commission', 0),
                swap=trade_data.get('swap', 0),
                opened_at=datetime.fromisoformat(trade_data.get('opened_at', datetime.now().isoformat())),
                closed_at=datetime.fromisoformat(trade_data['closed_at']) if trade_data.get('closed_at') else None,
                trade_status=trade_data.get('trade_status', 'open'),
                signal_data=trade_data.get('signal_data', {}),
                exit_reason=trade_data.get('exit_reason')
            )
            
            # Update execution metrics
            execution.update_performance_metrics()
            
        except AlgorithmExecution.DoesNotExist:
            logger.error(f"Execution {execution_id} not found")
        except Exception as e:
            logger.error(f"Error saving trade result: {str(e)}")

    @database_sync_to_async
    def save_algorithm_signal(self, execution_id, signal_data):
        """Save algorithm signal to database"""
        try:
            execution = AlgorithmExecution.objects.get(id=execution_id)
            
            signal = AlgorithmSignal.objects.create(
                execution=execution,
                signal_type=signal_data.get('signal_type'),
                symbol=signal_data.get('symbol'),
                signal_strength=signal_data.get('signal_strength', 0),
                recommended_volume=signal_data.get('recommended_volume'),
                recommended_price=signal_data.get('recommended_price'),
                recommended_sl=signal_data.get('recommended_sl'),
                recommended_tp=signal_data.get('recommended_tp'),
                signal_data=signal_data.get('technical_data', {}),
                market_conditions=signal_data.get('market_conditions', {}),
                signal_status=signal_data.get('signal_status', 'generated')
            )
            
        except AlgorithmExecution.DoesNotExist:
            logger.error(f"Execution {execution_id} not found")
        except Exception as e:
            logger.error(f"Error saving signal: {str(e)}")

    @database_sync_to_async
    def update_performance_metrics(self, execution_id, performance_data):
        """Update performance metrics"""
        try:
            execution = AlgorithmExecution.objects.get(id=execution_id)
            execution.performance_metrics.update(performance_data)
            execution.profit_loss = performance_data.get('total_pnl', execution.profit_loss)
            execution.win_rate = performance_data.get('win_rate', execution.win_rate)
            execution.current_drawdown = performance_data.get('current_drawdown', execution.current_drawdown)
            execution.max_drawdown = max(execution.max_drawdown, execution.current_drawdown)
            execution.save()
        except AlgorithmExecution.DoesNotExist:
            logger.error(f"Execution {execution_id} not found")

    @database_sync_to_async
    def update_execution_error(self, execution_id, error_message):
        """Update execution error"""
        try:
            execution = AlgorithmExecution.objects.get(id=execution_id)
            execution.execution_status = 'error'
            execution.error_message = error_message
            execution.save()
        except AlgorithmExecution.DoesNotExist:
            logger.error(f"Execution {execution_id} not found")

    @database_sync_to_async
    def update_heartbeat(self, execution_id):
        """Update last heartbeat"""
        try:
            execution = AlgorithmExecution.objects.get(id=execution_id)
            execution.last_heartbeat = datetime.now()
            execution.save()
        except AlgorithmExecution.DoesNotExist:
            logger.error(f"Execution {execution_id} not found")
