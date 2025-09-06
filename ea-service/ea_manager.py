"""
EA Management Core
Handles Expert Advisor lifecycle, process management, and communication
"""

import asyncio
import subprocess
import signal
import os
import sys
import psutil
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pathlib import Path

from config import get_settings
from models import ExecutionStatus, AlgorithmStatus, ProcessInfo
from auth import get_mt5_account, update_algorithm_execution

logger = logging.getLogger(__name__)

class EAExecution:
    """Represents a single EA execution"""
    
    def __init__(self, execution_id: str, algorithm_name: str, symbol: str, 
                 user_id: int, mt5_account_id: int, parameters: Dict[str, Any]):
        self.execution_id = execution_id
        self.algorithm_name = algorithm_name
        self.symbol = symbol
        self.user_id = user_id
        self.mt5_account_id = mt5_account_id
        self.parameters = parameters
        
        self.pid: Optional[int] = None
        self.process: Optional[subprocess.Popen] = None
        self.status = ExecutionStatus.STARTING
        self.started_at: Optional[datetime] = None
        self.stopped_at: Optional[datetime] = None
        self.error_message: Optional[str] = None
    
    def to_status(self) -> AlgorithmStatus:
        """Convert to AlgorithmStatus model"""
        return AlgorithmStatus(
            execution_id=self.execution_id,
            algorithm_name=self.algorithm_name,
            symbol=self.symbol,
            status=self.status,
            pid=self.pid,
            started_at=self.started_at,
            stopped_at=self.stopped_at,
            user_id=self.user_id,
            mt5_account_id=self.mt5_account_id,
            parameters=self.parameters,
            error_message=self.error_message
        )

class EAManager:
    """Manages Expert Advisor executions"""
    
    def __init__(self, settings):
        self.settings = settings
        self.active_executions: Dict[str, EAExecution] = {}
        self.algorithms_dir = Path(settings.algorithms_dir).resolve()
        self._monitoring_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
    
    async def initialize(self):
        """Initialize the EA Manager"""
        logger.info("Initializing EA Manager...")
        
        # Verify algorithms directory exists
        if not self.algorithms_dir.exists():
            logger.error(f"Algorithms directory not found: {self.algorithms_dir}")
            raise FileNotFoundError(f"Algorithms directory not found: {self.algorithms_dir}")
        
        # Start monitoring tasks
        self._monitoring_task = asyncio.create_task(self._monitor_processes())
        self._cleanup_task = asyncio.create_task(self._cleanup_finished())
        
        logger.info(f"EA Manager initialized. Algorithms dir: {self.algorithms_dir}")
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up EA Manager...")
        
        # Cancel monitoring tasks
        if self._monitoring_task:
            self._monitoring_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        # Stop all running EAs
        for execution_id in list(self.active_executions.keys()):
            try:
                await self._stop_execution(execution_id, force=True)
            except Exception as e:
                logger.error(f"Error stopping execution {execution_id}: {e}")
        
        logger.info("EA Manager cleanup completed")
    
    async def start_algorithm(self, user_id: int, algorithm_name: str, symbol: str, 
                            mt5_account_id: int, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Start an Expert Advisor"""
        try:
            # Check if we're at max capacity
            if len(self.active_executions) >= self.settings.max_concurrent_eas:
                return {
                    'status': 'error',
                    'message': f'Maximum concurrent EAs limit reached ({self.settings.max_concurrent_eas})'
                }
            
            # Stop any existing executions for the same algorithm and user
            await self._stop_user_algorithm(user_id, algorithm_name)
            
            # Generate execution ID
            execution_id = str(uuid.uuid4())
            
            # Create execution object
            execution = EAExecution(
                execution_id=execution_id,
                algorithm_name=algorithm_name,
                symbol=symbol,
                user_id=user_id,
                mt5_account_id=mt5_account_id,
                parameters=parameters
            )
            
            # Get EA script path
            ea_script_path = self._get_ea_script_path(algorithm_name)
            if not ea_script_path.exists():
                return {
                    'status': 'error',
                    'message': f'EA script not found for {algorithm_name}: {ea_script_path}'
                }
            
            # Start the EA process
            success = await self._launch_ea_process(execution, ea_script_path)
            if not success:
                return {
                    'status': 'error',
                    'message': f'Failed to launch EA process for {algorithm_name}'
                }
            
            # Store execution
            self.active_executions[execution_id] = execution
            
            logger.info(f"Started EA {algorithm_name} with execution ID {execution_id}")
            
            return {
                'status': 'success',
                'message': f'Algorithm {algorithm_name} started successfully',
                'execution_id': execution_id,
                'pid': execution.pid
            }
            
        except Exception as e:
            logger.error(f"Error starting algorithm {algorithm_name}: {e}")
            return {
                'status': 'error',
                'message': f'Failed to start algorithm: {str(e)}'
            }
    
    async def stop_algorithm(self, execution_id: str, user_id: int) -> Dict[str, Any]:
        """Stop a running Expert Advisor"""
        try:
            execution = self.active_executions.get(execution_id)
            if not execution:
                return {
                    'status': 'error',
                    'message': f'Execution {execution_id} not found'
                }
            
            # Verify ownership
            if execution.user_id != user_id:
                return {
                    'status': 'error',
                    'message': 'Access denied: execution belongs to different user'
                }
            
            success = await self._stop_execution(execution_id)
            if success:
                return {
                    'status': 'success',
                    'message': f'Algorithm stopped successfully'
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Failed to stop algorithm'
                }
                
        except Exception as e:
            logger.error(f"Error stopping algorithm {execution_id}: {e}")
            return {
                'status': 'error',
                'message': f'Failed to stop algorithm: {str(e)}'
            }
    
    async def pause_algorithm(self, execution_id: str, user_id: int) -> Dict[str, Any]:
        """Pause a running Expert Advisor"""
        try:
            execution = self.active_executions.get(execution_id)
            if not execution:
                return {
                    'status': 'error',
                    'message': f'Execution {execution_id} not found'
                }
            
            # Verify ownership
            if execution.user_id != user_id:
                return {
                    'status': 'error',
                    'message': 'Access denied: execution belongs to different user'
                }
            
            if execution.status != ExecutionStatus.RUNNING:
                return {
                    'status': 'error',
                    'message': f'Algorithm is not running (current status: {execution.status})'
                }
            
            # Create pause flag
            success = await self._create_pause_flag(execution.algorithm_name)
            if success:
                execution.status = ExecutionStatus.PAUSED
                return {
                    'status': 'success',
                    'message': 'Algorithm paused successfully'
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Failed to pause algorithm'
                }
                
        except Exception as e:
            logger.error(f"Error pausing algorithm {execution_id}: {e}")
            return {
                'status': 'error',
                'message': f'Failed to pause algorithm: {str(e)}'
            }
    
    async def resume_algorithm(self, execution_id: str, user_id: int) -> Dict[str, Any]:
        """Resume a paused Expert Advisor"""
        try:
            execution = self.active_executions.get(execution_id)
            if not execution:
                return {
                    'status': 'error',
                    'message': f'Execution {execution_id} not found'
                }
            
            # Verify ownership
            if execution.user_id != user_id:
                return {
                    'status': 'error',
                    'message': 'Access denied: execution belongs to different user'
                }
            
            if execution.status != ExecutionStatus.PAUSED:
                return {
                    'status': 'error',
                    'message': f'Algorithm is not paused (current status: {execution.status})'
                }
            
            # Remove pause flag
            success = await self._remove_pause_flag(execution.algorithm_name)
            if success:
                execution.status = ExecutionStatus.RUNNING
                return {
                    'status': 'success',
                    'message': 'Algorithm resumed successfully'
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Failed to resume algorithm'
                }
                
        except Exception as e:
            logger.error(f"Error resuming algorithm {execution_id}: {e}")
            return {
                'status': 'error',
                'message': f'Failed to resume algorithm: {str(e)}'
            }
    
    async def get_algorithm_status(self, execution_id: str, user_id: int) -> AlgorithmStatus:
        """Get status of a specific algorithm execution"""
        execution = self.active_executions.get(execution_id)
        if not execution:
            raise ValueError(f'Execution {execution_id} not found')
        
        # Verify ownership
        if execution.user_id != user_id:
            raise PermissionError('Access denied: execution belongs to different user')
        
        return execution.to_status()
    
    async def list_user_algorithms(self, user_id: int) -> List[AlgorithmStatus]:
        """List all algorithm executions for a user"""
        user_executions = [
            execution.to_status() 
            for execution in self.active_executions.values() 
            if execution.user_id == user_id
        ]
        return user_executions
    
    async def get_available_algorithms(self) -> List[str]:
        """Get list of available EA algorithms"""
        algorithms = []
        try:
            for item in self.algorithms_dir.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    # Check if EA script exists
                    ea_script = item / f"mt5_{item.name}.py"
                    if ea_script.exists():
                        algorithms.append(item.name)
        except Exception as e:
            logger.error(f"Error listing algorithms: {e}")
        
        return sorted(algorithms)
    
    def _get_ea_script_path(self, algorithm_name: str) -> Path:
        """Get path to EA script"""
        ea_dir = self.algorithms_dir / algorithm_name
        return ea_dir / f"mt5_{algorithm_name}.py"
    
    async def _launch_ea_process(self, execution: EAExecution, script_path: Path) -> bool:
        """Launch EA subprocess"""
        try:
            # Prepare environment with credentials
            env = os.environ.copy()
            
            # Add Python path for imports
            project_root = self.algorithms_dir.parent
            existing_pp = env.get('PYTHONPATH', '')
            env['PYTHONPATH'] = str(project_root) + (os.pathsep + existing_pp if existing_pp else '')
            
            # TODO: Get MT5 credentials from Django backend and set environment variables
            # env['MT5_ACCOUNT_NUMBER'] = str(account_data['account_number'])
            # env['MT5_PASSWORD'] = account_data['password']
            # env['MT5_SERVER'] = account_data['server']
            # env['MT5_ACCOUNT_ID'] = str(execution.mt5_account_id)
            # env['MT5_BROKER_NAME'] = account_data.get('broker_name', 'Unknown')
            
            # Launch process
            cmd = [sys.executable, str(script_path)]
            if execution.symbol:
                cmd.append(execution.symbol)
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(project_root),
                env=env,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            execution.process = process
            execution.pid = process.pid
            execution.status = ExecutionStatus.RUNNING
            execution.started_at = datetime.now(timezone.utc)
            
            logger.info(f"Launched EA process: PID {process.pid}, Script: {script_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to launch EA process: {e}")
            execution.status = ExecutionStatus.ERROR
            execution.error_message = str(e)
            return False
    
    async def _stop_execution(self, execution_id: str, force: bool = False) -> bool:
        """Stop an EA execution"""
        try:
            execution = self.active_executions.get(execution_id)
            if not execution:
                return False
            
            if execution.process and execution.pid:
                try:
                    if os.name == 'nt':  # Windows
                        if force:
                            subprocess.run(['taskkill', '/PID', str(execution.pid), '/F', '/T'], 
                                         check=False, capture_output=True)
                        else:
                            os.kill(execution.pid, signal.SIGTERM)
                    else:  # Unix-like
                        signal_type = signal.SIGKILL if force else signal.SIGTERM
                        os.kill(execution.pid, signal_type)
                    
                    # Wait for process to terminate
                    try:
                        execution.process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        if not force:
                            # Force kill if graceful termination failed
                            return await self._stop_execution(execution_id, force=True)
                    
                except ProcessLookupError:
                    # Process already terminated
                    pass
            
            execution.status = ExecutionStatus.STOPPED
            execution.stopped_at = datetime.now(timezone.utc)
            
            # Remove pause flag if exists
            await self._remove_pause_flag(execution.algorithm_name)
            
            logger.info(f"Stopped execution {execution_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping execution {execution_id}: {e}")
            return False
    
    async def _stop_user_algorithm(self, user_id: int, algorithm_name: str):
        """Stop existing executions of the same algorithm for a user"""
        to_stop = [
            exec_id for exec_id, execution in self.active_executions.items()
            if execution.user_id == user_id and execution.algorithm_name == algorithm_name
            and execution.status in [ExecutionStatus.RUNNING, ExecutionStatus.PAUSED]
        ]
        
        for exec_id in to_stop:
            await self._stop_execution(exec_id)
    
    async def _create_pause_flag(self, algorithm_name: str) -> bool:
        """Create pause flag file"""
        try:
            ea_dir = self.algorithms_dir / algorithm_name
            pause_flag_path = ea_dir / "pause.flag"
            
            with open(pause_flag_path, 'w') as f:
                f.write('paused')
            
            return True
        except Exception as e:
            logger.error(f"Failed to create pause flag: {e}")
            return False
    
    async def _remove_pause_flag(self, algorithm_name: str) -> bool:
        """Remove pause flag file"""
        try:
            ea_dir = self.algorithms_dir / algorithm_name
            pause_flag_path = ea_dir / "pause.flag"
            
            if pause_flag_path.exists():
                pause_flag_path.unlink()
            
            return True
        except Exception as e:
            logger.error(f"Failed to remove pause flag: {e}")
            return False
    
    async def _monitor_processes(self):
        """Monitor EA processes and update status"""
        while True:
            try:
                await asyncio.sleep(self.settings.process_check_interval)
                
                for execution in list(self.active_executions.values()):
                    if execution.pid and execution.status == ExecutionStatus.RUNNING:
                        try:
                            # Check if process is still running
                            process = psutil.Process(execution.pid)
                            if not process.is_running():
                                execution.status = ExecutionStatus.STOPPED
                                execution.stopped_at = datetime.now(timezone.utc)
                                logger.info(f"Process {execution.pid} stopped naturally")
                        except psutil.NoSuchProcess:
                            execution.status = ExecutionStatus.STOPPED
                            execution.stopped_at = datetime.now(timezone.utc)
                            logger.info(f"Process {execution.pid} no longer exists")
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in process monitoring: {e}")
    
    async def _cleanup_finished(self):
        """Cleanup finished executions"""
        while True:
            try:
                await asyncio.sleep(self.settings.cleanup_interval)
                
                # Remove stopped executions older than 1 hour
                cutoff_time = datetime.now(timezone.utc).timestamp() - 3600
                
                to_remove = []
                for exec_id, execution in self.active_executions.items():
                    if (execution.status in [ExecutionStatus.STOPPED, ExecutionStatus.ERROR] 
                        and execution.stopped_at 
                        and execution.stopped_at.timestamp() < cutoff_time):
                        to_remove.append(exec_id)
                
                for exec_id in to_remove:
                    del self.active_executions[exec_id]
                    logger.info(f"Cleaned up old execution {exec_id}")
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
