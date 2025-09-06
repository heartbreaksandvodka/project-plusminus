"""
Authentication utilities for EA Service
Integrates with Django backend for user authentication
"""

import httpx
import logging
import jwt
from jwt.exceptions import InvalidTokenError
from typing import Dict, Optional
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

async def verify_jwt_token(token: str) -> Optional[Dict]:
    """
    Verify JWT token against Django backend
    """
    try:
        # First try to decode locally (faster)
        payload = jwt.decode(
            token, 
            settings.jwt_secret_key, 
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except InvalidTokenError as e:
        logger.warning(f"Local JWT verification failed: {e}")
        
        # Fallback: verify with Django backend
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.django_api_base}/auth/verify-token/",
                    json={"token": token},
                    timeout=5.0
                )
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Django token verification failed: {response.status_code}")
                    return None
        except Exception as e:
            logger.error(f"Error verifying token with Django: {e}")
            return None

async def get_user_from_token(token: str) -> Optional[Dict]:
    """
    Get user information from JWT token
    """
    payload = await verify_jwt_token(token)
    if not payload:
        return None
    
    user_id = payload.get('user_id')
    if not user_id:
        return None
    
    # Get user details from Django backend
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.django_api_base}/auth/user/{user_id}/",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5.0
            )
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get user details: {response.status_code}")
                return None
    except Exception as e:
        logger.error(f"Error getting user from Django: {e}")
        return None

async def get_mt5_account(user_id: int, account_id: int, token: str) -> Optional[Dict]:
    """
    Get MT5 account details from Django backend
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.django_api_base}/mt5/accounts/{account_id}/",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5.0
            )
            if response.status_code == 200:
                account_data = response.json()
                # Verify account belongs to user
                if account_data.get('user') == user_id:
                    return account_data
                else:
                    logger.warning(f"MT5 account {account_id} does not belong to user {user_id}")
                    return None
            else:
                logger.error(f"Failed to get MT5 account: {response.status_code}")
                return None
    except Exception as e:
        logger.error(f"Error getting MT5 account from Django: {e}")
        return None

async def update_algorithm_execution(execution_id: str, status_data: Dict, token: str) -> bool:
    """
    Update algorithm execution status in Django backend
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{settings.django_api_base}/mt5/executions/{execution_id}/",
                headers={"Authorization": f"Bearer {token}"},
                json=status_data,
                timeout=5.0
            )
            return response.status_code == 200
    except Exception as e:
        logger.error(f"Error updating execution status: {e}")
        return False
