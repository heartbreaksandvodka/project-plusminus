"""
EA Token Management Views
Provides endpoints for managing EA authentication tokens
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .ea_models import EAAuthToken, EAConnectionLog
from .serializers import EAAuthTokenSerializer
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_ea_tokens(request):
    """
    List all EA tokens for the authenticated user
    """
    try:
        tokens = EAAuthToken.objects.filter(user=request.user, is_active=True)
        token_data = []
        
        for token in tokens:
            # Get recent connection info
            recent_connection = token.connection_logs.order_by('-connected_at').first()
            
            token_info = {
                'id': token.id,
                'algorithm_id': token.algorithm_id,
                'name': token.name,
                'created_at': token.created_at,
                'last_used': token.last_used,
                'expires_at': token.expires_at,
                'connection_count': token.connection_count,
                'permissions': token.permissions,
                'is_valid': token.is_valid(),
                'last_connection': {
                    'connected_at': recent_connection.connected_at if recent_connection else None,
                    'ip_address': recent_connection.ip_address if recent_connection else None,
                    'is_active': recent_connection.disconnected_at is None if recent_connection else False
                } if recent_connection else None
            }
            token_data.append(token_info)
        
        return Response({
            'message': 'EA tokens retrieved successfully',
            'tokens': token_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error listing EA tokens for user {request.user.id}: {e}")
        return Response({
            'error': 'Failed to retrieve EA tokens'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_ea_token(request):
    """
    Create a new EA authentication token
    Expected data: {
        "algorithm_id": "string",
        "name": "string",
        "permissions": {optional dict},
        "expires_days": optional integer (default 30)
    }
    """
    try:
        algorithm_id = request.data.get('algorithm_id')
        name = request.data.get('name')
        permissions = request.data.get('permissions', {})
        expires_days = request.data.get('expires_days', 30)
        
        if not algorithm_id or not name:
            return Response({
                'error': 'algorithm_id and name are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate algorithm_id format (alphanumeric, underscore, hyphen only)
        if not algorithm_id.replace('_', '').replace('-', '').isalnum():
            return Response({
                'error': 'algorithm_id must contain only letters, numbers, underscores, and hyphens'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            # Create the EA token
            ea_token = EAAuthToken.create_for_user(
                user=request.user,
                algorithm_id=algorithm_id,
                name=name,
                permissions=permissions
            )
            
            # Set custom expiration if provided
            if expires_days != 30:
                ea_token.extend_expiration(days=expires_days)
        
        logger.info(f"Created EA token {ea_token.algorithm_id} for user {request.user.email}")
        
        return Response({
            'message': 'EA token created successfully',
            'token_data': {
                'id': ea_token.id,
                'algorithm_id': ea_token.algorithm_id,
                'name': ea_token.name,
                'token': ea_token.token,  # Only returned on creation
                'expires_at': ea_token.expires_at,
                'permissions': ea_token.permissions
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error creating EA token for user {request.user.id}: {e}")
        return Response({
            'error': 'Failed to create EA token'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_ea_token(request, token_id):
    """
    Update an existing EA token (permissions, name, expiration)
    """
    try:
        ea_token = EAAuthToken.objects.get(
            id=token_id, 
            user=request.user,
            is_active=True
        )
        
        # Update name if provided
        if 'name' in request.data:
            ea_token.name = request.data['name']
        
        # Update permissions if provided
        if 'permissions' in request.data:
            ea_token.update_permissions(request.data['permissions'])
        
        # Extend expiration if requested
        if 'extend_days' in request.data:
            extend_days = int(request.data['extend_days'])
            ea_token.extend_expiration(days=extend_days)
        
        ea_token.save()
        
        logger.info(f"Updated EA token {ea_token.algorithm_id} for user {request.user.email}")
        
        return Response({
            'message': 'EA token updated successfully',
            'token_data': {
                'id': ea_token.id,
                'algorithm_id': ea_token.algorithm_id,
                'name': ea_token.name,
                'expires_at': ea_token.expires_at,
                'permissions': ea_token.permissions
            }
        }, status=status.HTTP_200_OK)
        
    except EAAuthToken.DoesNotExist:
        return Response({
            'error': 'EA token not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error updating EA token {token_id} for user {request.user.id}: {e}")
        return Response({
            'error': 'Failed to update EA token'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def revoke_ea_token(request, token_id):
    """
    Revoke (deactivate) an EA token
    """
    try:
        ea_token = EAAuthToken.objects.get(
            id=token_id, 
            user=request.user,
            is_active=True
        )
        
        ea_token.revoke()
        
        logger.info(f"Revoked EA token {ea_token.algorithm_id} for user {request.user.email}")
        
        return Response({
            'message': 'EA token revoked successfully'
        }, status=status.HTTP_200_OK)
        
    except EAAuthToken.DoesNotExist:
        return Response({
            'error': 'EA token not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error revoking EA token {token_id} for user {request.user.id}: {e}")
        return Response({
            'error': 'Failed to revoke EA token'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def regenerate_ea_token(request, token_id):
    """
    Regenerate a new token string for an existing EA token
    This invalidates the old token and creates a new one
    """
    try:
        old_token = EAAuthToken.objects.get(
            id=token_id, 
            user=request.user,
            is_active=True
        )
        
        with transaction.atomic():
            # Create new token with same settings
            new_token = EAAuthToken.create_for_user(
                user=request.user,
                algorithm_id=old_token.algorithm_id,
                name=old_token.name,
                permissions=old_token.permissions
            )
            
            # Copy expiration time if it was custom
            if old_token.expires_at > new_token.expires_at:
                new_token.expires_at = old_token.expires_at
                new_token.save()
        
        logger.info(f"Regenerated EA token {new_token.algorithm_id} for user {request.user.email}")
        
        return Response({
            'message': 'EA token regenerated successfully',
            'token_data': {
                'id': new_token.id,
                'algorithm_id': new_token.algorithm_id,
                'name': new_token.name,
                'token': new_token.token,  # Only returned on regeneration
                'expires_at': new_token.expires_at,
                'permissions': new_token.permissions
            }
        }, status=status.HTTP_200_OK)
        
    except EAAuthToken.DoesNotExist:
        return Response({
            'error': 'EA token not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error regenerating EA token {token_id} for user {request.user.id}: {e}")
        return Response({
            'error': 'Failed to regenerate EA token'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ea_connection_logs(request, token_id):
    """
    Get connection logs for a specific EA token
    """
    try:
        ea_token = EAAuthToken.objects.get(
            id=token_id, 
            user=request.user,
            is_active=True
        )
        
        logs = EAConnectionLog.objects.filter(
            ea_token=ea_token
        ).order_by('-connected_at')[:50]  # Last 50 connections
        
        log_data = []
        for log in logs:
            log_info = {
                'connected_at': log.connected_at,
                'disconnected_at': log.disconnected_at,
                'ip_address': log.ip_address,
                'connection_duration': log.connection_duration,
                'disconnect_reason': log.disconnect_reason,
                'messages_sent': log.messages_sent,
                'messages_received': log.messages_received,
                'trades_reported': log.trades_reported,
                'errors_encountered': log.errors_encountered
            }
            log_data.append(log_info)
        
        return Response({
            'message': 'Connection logs retrieved successfully',
            'logs': log_data
        }, status=status.HTTP_200_OK)
        
    except EAAuthToken.DoesNotExist:
        return Response({
            'error': 'EA token not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error retrieving connection logs for token {token_id}: {e}")
        return Response({
            'error': 'Failed to retrieve connection logs'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
