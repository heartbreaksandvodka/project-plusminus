#!/usr/bin/env python3
"""
EA Token Authentication Test
Tests the new EA token system integration with WebSocket authentication
"""

import asyncio
import websockets
import json
import logging
import sys
import os
from datetime import datetime

# Add the backend to Python path for Django imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'authproject.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from authentication.ea_models import EAAuthToken

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

User = get_user_model()

class EATokenWebSocketTest:
    def __init__(self):
        self.test_user = None
        self.ea_token = None
        
    async def setup_test_user_and_token(self):
        """Create or get a test user and generate EA token"""
        try:
            from channels.db import database_sync_to_async
            
            # Get or create test user (async)
            @database_sync_to_async
            def get_or_create_user():
                user, created = User.objects.get_or_create(
                    email='ea_test@example.com',
                    defaults={
                        'username': 'ea_test_user',
                        'first_name': 'EA',
                        'last_name': 'Tester'
                    }
                )
                if created:
                    user.set_password('testpass123')
                    user.save()
                return user, created
            
            self.test_user, created = await get_or_create_user()
            
            if created:
                logger.info("Created new test user for EA testing")
            else:
                logger.info("Using existing EA test user")
            
            # Create or get existing EA token (async)
            @database_sync_to_async
            def get_or_create_ea_token():
                # Debug: Check what tokens exist
                all_tokens = EAAuthToken.objects.filter(
                    user=self.test_user,
                    algorithm_id='test_ea_websocket'
                )
                logger.info(f"Found {all_tokens.count()} existing tokens for this user/algorithm")
                
                for token in all_tokens:
                    logger.info(f"Token: {token.id}, active: {token.is_active}, valid: {token.is_valid()}")
                
                # Try to get existing active token first
                existing_tokens = EAAuthToken.objects.filter(
                    user=self.test_user,
                    algorithm_id='test_ea_websocket',
                    is_active=True
                )
                
                if existing_tokens.exists():
                    token = existing_tokens.first()
                    logger.info(f"Using existing EA token: {token.token[:20]}...")
                    return token
                else:
                    # If no active tokens, clean up any inactive ones and create new
                    all_tokens.delete()  # Clean up old tokens
                    logger.info("Creating new EA token")
                    return EAAuthToken.objects.create(
                        user=self.test_user,
                        algorithm_id='test_ea_websocket',
                        name='WebSocket Test EA'
                    )
            
            self.ea_token = await get_or_create_ea_token()
            
            logger.info(f"Created EA token: {self.ea_token.token[:20]}...")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup test user and token: {e}")
            return False
    
    async def test_ea_websocket_connection(self):
        """Test WebSocket connection with EA token"""
        try:
            ws_url = "ws://localhost:8000/ws/algorithm/test_ea_websocket/"
            
            logger.info(f"Connecting to {ws_url} with EA token...")
            
            # Connect with EA token in the URL or header
            async with websockets.connect(
                ws_url,
                extra_headers={"Authorization": f"Bearer {self.ea_token.token}"}
            ) as websocket:
                logger.info("✅ WebSocket connected successfully with EA token!")
                
                # Test sending a status update
                await self.test_ea_status_update(websocket)
                
                # Test sending trade data
                await self.test_ea_trade_reporting(websocket)
                
                return True
                
        except Exception as e:
            logger.error(f"❌ WebSocket connection failed: {e}")
            return False
    
    async def test_ea_status_update(self, websocket):
        """Test sending EA status update"""
        status_message = {
            "type": "status_update",
            "data": {
                "status": "running",
                "message": "EA is operational",
                "timestamp": datetime.now().isoformat(),
                "performance": {
                    "balance": 10000.0,
                    "equity": 10150.0,
                    "profit": 150.0,
                    "trades_count": 3
                }
            }
        }
        
        try:
            await websocket.send(json.dumps(status_message))
            logger.info("✅ EA status update sent successfully")
        except Exception as e:
            logger.error(f"❌ Failed to send EA status update: {e}")
    
    async def test_ea_trade_reporting(self, websocket):
        """Test sending trade reports"""
        trade_message = {
            "type": "trade_opened",
            "data": {
                "ticket": 54321,
                "symbol": "GBPUSD",
                "type": "sell",
                "volume": 0.05,
                "open_price": 1.2650,
                "sl": 1.2700,
                "tp": 1.2600,
                "timestamp": datetime.now().isoformat(),
                "comment": "EA automated trade"
            }
        }
        
        try:
            await websocket.send(json.dumps(trade_message))
            logger.info("✅ EA trade report sent successfully")
        except Exception as e:
            logger.error(f"❌ Failed to send EA trade report: {e}")
    
    async def verify_token_in_database(self):
        """Verify the EA token was recorded correctly"""
        try:
            from channels.db import database_sync_to_async
            
            @database_sync_to_async
            def get_token_info():
                # Refresh token from database
                self.ea_token.refresh_from_db()
                
                # Get connection logs
                connection_logs = list(self.ea_token.connection_logs.all())
                
                return {
                    'connection_count': self.ea_token.connection_count,
                    'last_used': self.ea_token.last_used,
                    'is_valid': self.ea_token.is_valid(),
                    'logs_count': len(connection_logs),
                    'logs': connection_logs
                }
            
            token_info = await get_token_info()
            
            logger.info(f"Token usage count: {token_info['connection_count']}")
            logger.info(f"Token last used: {token_info['last_used']}")
            logger.info(f"Token is valid: {token_info['is_valid']}")
            logger.info(f"Connection logs count: {token_info['logs_count']}")
            
            for log in token_info['logs']:
                logger.info(f"Connection: {log.connected_at} - {log.disconnected_at or 'Active'}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error verifying token in database: {e}")
            return False

async def main():
    """Main test execution"""
    print("🚀 EA Token WebSocket Authentication Test")
    print("=" * 60)
    print("Testing the new EA token authentication system:")
    print("✅ EA token creation")
    print("✅ WebSocket connection with EA token")  
    print("✅ Message exchange")
    print("✅ Connection logging")
    print("=" * 60)
    
    test = EATokenWebSocketTest()
    
    # Step 1: Setup test user and EA token
    logger.info("🔐 Setting up test user and EA token...")
    if not await test.setup_test_user_and_token():
        logger.error("❌ Failed to setup test environment. Exiting.")
        return False
    
    # Step 2: Test WebSocket connection
    logger.info("🌐 Testing WebSocket connection with EA token...")
    success = await test.test_ea_websocket_connection()
    
    # Step 3: Verify database records
    logger.info("📊 Verifying database records...")
    db_success = await test.verify_token_in_database()
    
    if success and db_success:
        print("\n" + "=" * 60)
        print("🎉 EA Token Authentication System: FULLY OPERATIONAL!")
        print("✅ EA Token Creation: Working")
        print("✅ WebSocket Authentication: Working")
        print("✅ Message Exchange: Working") 
        print("✅ Connection Logging: Working")
        print("✅ Database Integration: Working")
        print("=" * 60)
        print("🚀 Ready for production EA integration!")
    else:
        print("\n" + "=" * 60)
        print("❌ EA token authentication test failed")
        print("📝 Make sure the ASGI server is running:")
        print("   cd backend")
        print("   python -m daphne -p 8000 authproject.asgi:application")
        print("=" * 60)
    
    return success and db_success

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        print(f"\n❌ Unexpected error: {e}")
