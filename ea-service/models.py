"""
Pydantic models for EA Service
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

class ExecutionStatus(str, Enum):
    """Algorithm execution status"""
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"

class StartAlgorithmRequest(BaseModel):
    """Request model for starting an algorithm"""
    algorithm_name: str = Field(..., description="Name of the EA algorithm")
    symbol: str = Field(default="EURUSD", description="Trading symbol")
    mt5_account_id: int = Field(..., description="MT5 account ID from database")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="EA parameters")

class StopAlgorithmRequest(BaseModel):
    """Request model for stopping an algorithm"""
    force: bool = Field(default=False, description="Force stop if graceful stop fails")

class PauseAlgorithmRequest(BaseModel):
    """Request model for pausing an algorithm"""
    timeout: int = Field(default=30, description="Timeout in seconds")

class ResumeAlgorithmRequest(BaseModel):
    """Request model for resuming an algorithm"""
    pass

class AlgorithmStatus(BaseModel):
    """Algorithm execution status response"""
    execution_id: str
    algorithm_name: str
    symbol: str
    status: ExecutionStatus
    pid: Optional[int] = None
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    user_id: int
    mt5_account_id: int
    parameters: Dict[str, Any] = Field(default_factory=dict)
    performance: Optional[Dict[str, Any]] = Field(default_factory=dict)
    error_message: Optional[str] = None

class EAServiceConfig(BaseModel):
    """EA Service configuration"""
    max_concurrent_eas: int
    algorithms_dir: str
    process_check_interval: int
    websocket_enabled: bool = True

class ProcessInfo(BaseModel):
    """Process information"""
    pid: int
    status: str
    cpu_percent: float
    memory_percent: float
    create_time: datetime

class AlgorithmMetrics(BaseModel):
    """Algorithm performance metrics"""
    execution_id: str
    trades_count: int = 0
    profit_loss: float = 0.0
    win_rate: float = 0.0
    max_drawdown: float = 0.0
    current_positions: int = 0
    last_trade_time: Optional[datetime] = None
    uptime_seconds: int = 0

class WebSocketMessage(BaseModel):
    """WebSocket message structure"""
    type: str
    execution_id: str
    data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)

class CommandMessage(BaseModel):
    """Command message for EA control"""
    command: str  # pause, resume, stop, update_config
    parameters: Dict[str, Any] = Field(default_factory=dict)

class StatusMessage(BaseModel):
    """Status update message from EA"""
    status: ExecutionStatus
    metrics: Optional[AlgorithmMetrics] = None
    message: Optional[str] = None
