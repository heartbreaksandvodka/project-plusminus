"""
EA Management Service - FastAPI
Dedicated service for Expert Advisor lifecycle management
Port: 8001
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import logging
from contextlib import asynccontextmanager
from typing import Dict, List, Optional
import asyncio

from ea_manager import EAManager
from models import (
    StartAlgorithmRequest, StopAlgorithmRequest, PauseAlgorithmRequest, 
    ResumeAlgorithmRequest, AlgorithmStatus, EAServiceConfig
)
from auth import verify_jwt_token, get_user_from_token
from websocket_handler import WebSocketManager
from config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
ea_manager = None
websocket_manager = None
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global ea_manager, websocket_manager
    
    # Startup
    logger.info("🚀 Starting EA Management Service...")
    ea_manager = EAManager(settings)
    websocket_manager = WebSocketManager()
    
    # Initialize EA manager
    await ea_manager.initialize()
    
    logger.info(f"✅ EA Service running on port {settings.port}")
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down EA Management Service...")
    if ea_manager:
        await ea_manager.cleanup()

# FastAPI app with lifespan management
app = FastAPI(
    title="EA Management Service",
    description="Dedicated service for Expert Advisor lifecycle management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and get user information"""
    try:
        user = await get_user_from_token(credentials.credentials)
        return user
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "EA Management Service",
        "status": "running",
        "version": "1.0.0",
        "port": settings.port
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "ea_manager": "ready" if ea_manager else "not_ready",
        "websocket_manager": "ready" if websocket_manager else "not_ready",
        "active_eas": len(ea_manager.active_executions) if ea_manager else 0
    }

@app.post("/algorithms/start")
async def start_algorithm(
    request: StartAlgorithmRequest,
    background_tasks: BackgroundTasks,
    user = Depends(get_current_user)
):
    """Start an Expert Advisor"""
    try:
        logger.info(f"Starting algorithm {request.algorithm_name} for user {user['id']}")
        
        result = await ea_manager.start_algorithm(
            user_id=user['id'],
            algorithm_name=request.algorithm_name,
            symbol=request.symbol,
            mt5_account_id=request.mt5_account_id,
            parameters=request.parameters
        )
        
        if result['status'] == 'success':
            # Set up WebSocket monitoring in background
            if websocket_manager:
                background_tasks.add_task(
                    websocket_manager.setup_ea_monitoring,
                    result['execution_id'],
                    result['pid']
                )
            
            return {
                "status": "success",
                "message": result['message'],
                "execution_id": result['execution_id'],
                "pid": result['pid'],
                "algorithm_name": request.algorithm_name
            }
        else:
            raise HTTPException(status_code=400, detail=result['message'])
            
    except Exception as e:
        logger.error(f"Error starting algorithm: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/algorithms/{execution_id}/stop")
async def stop_algorithm(
    execution_id: str,
    user = Depends(get_current_user)
):
    """Stop a running Expert Advisor"""
    try:
        logger.info(f"Stopping algorithm execution {execution_id}")
        
        result = await ea_manager.stop_algorithm(execution_id, user['id'])
        
        if result['status'] == 'success':
            return {
                "status": "success",
                "message": result['message'],
                "execution_id": execution_id
            }
        else:
            raise HTTPException(status_code=400, detail=result['message'])
            
    except Exception as e:
        logger.error(f"Error stopping algorithm: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/algorithms/{execution_id}/pause")
async def pause_algorithm(
    execution_id: str,
    user = Depends(get_current_user)
):
    """Pause a running Expert Advisor"""
    try:
        logger.info(f"Pausing algorithm execution {execution_id}")
        
        result = await ea_manager.pause_algorithm(execution_id, user['id'])
        
        if result['status'] == 'success':
            return {
                "status": "success",
                "message": result['message'],
                "execution_id": execution_id
            }
        else:
            raise HTTPException(status_code=400, detail=result['message'])
            
    except Exception as e:
        logger.error(f"Error pausing algorithm: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/algorithms/{execution_id}/resume")
async def resume_algorithm(
    execution_id: str,
    user = Depends(get_current_user)
):
    """Resume a paused Expert Advisor"""
    try:
        logger.info(f"Resuming algorithm execution {execution_id}")
        
        result = await ea_manager.resume_algorithm(execution_id, user['id'])
        
        if result['status'] == 'success':
            return {
                "status": "success",
                "message": result['message'],
                "execution_id": execution_id
            }
        else:
            raise HTTPException(status_code=400, detail=result['message'])
            
    except Exception as e:
        logger.error(f"Error resuming algorithm: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/algorithms/{execution_id}/status")
async def get_algorithm_status(
    execution_id: str,
    user = Depends(get_current_user)
) -> AlgorithmStatus:
    """Get status of a specific algorithm execution"""
    try:
        status = await ea_manager.get_algorithm_status(execution_id, user['id'])
        return status
    except Exception as e:
        logger.error(f"Error getting algorithm status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/algorithms")
async def list_algorithms(user = Depends(get_current_user)) -> List[AlgorithmStatus]:
    """List all algorithm executions for the user"""
    try:
        algorithms = await ea_manager.list_user_algorithms(user['id'])
        return algorithms
    except Exception as e:
        logger.error(f"Error listing algorithms: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/algorithms/available")
async def get_available_algorithms() -> List[str]:
    """Get list of available EA algorithms"""
    try:
        algorithms = await ea_manager.get_available_algorithms()
        return algorithms
    except Exception as e:
        logger.error(f"Error getting available algorithms: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time communication
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws/algorithms/{execution_id}")
async def websocket_endpoint(websocket: WebSocket, execution_id: str):
    """WebSocket endpoint for real-time EA communication"""
    try:
        await websocket.accept()
        logger.info(f"WebSocket connected for execution {execution_id}")
        
        if websocket_manager:
            await websocket_manager.handle_connection(websocket, execution_id)
        else:
            await websocket.close(code=1011, reason="WebSocket manager not available")
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for execution {execution_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close(code=1011, reason=f"Internal error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
