# EA Service Architecture Guide
## FastAPI EA Management Service

### 🏗️ **Architecture Overview**
```
┌─────────────────────────────────────────────────┐
│               EA SERVICE                        │
│                (Port 8001)                     │
│  ┌─────────────────────────────────────────┐    │
│  │            FastAPI Layer               │    │
│  │     RESTful + WebSocket APIs          │    │
│  └─────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────┐    │
│  │         EA Manager Core                │    │
│  │    Process Control & Monitoring       │    │
│  └─────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────┐    │
│  │       Authentication Layer             │    │
│  │   Django Backend Integration          │    │
│  └─────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────┐    │
│  │        WebSocket Manager               │    │
│  │     Real-time Communication          │    │
│  └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

### 📁 **Service Structure**
```
ea-service/
├── main.py              # FastAPI application entry point
├── config.py           # Service configuration management
├── models.py           # Pydantic data models
├── auth.py             # Django authentication integration
├── ea_manager.py       # Core EA lifecycle management
├── websocket_handler.py # Real-time WebSocket communication
├── requirements.txt    # Python dependencies
├── .env.example        # Configuration template
├── .env               # Environment configuration
├── start_dev.bat      # Windows startup script
├── start_dev.sh       # Unix startup script
└── README.md          # Service documentation
```

### 🚀 **Core Components**

#### **1. FastAPI Application (main.py)**
```python
# Service initialization
app = FastAPI(title="EA Management Service", version="1.0.0")

# Global managers
ea_manager: EAManager = None
websocket_manager: WebSocketManager = None

# API endpoints
@app.get("/algorithms")           # List available EAs
@app.post("/algorithms/{id}/start")  # Start EA
@app.post("/algorithms/{id}/stop")   # Stop EA
@app.websocket("/ws/algorithms/{id}") # Real-time updates
```

#### **2. EA Manager (ea_manager.py)**
```python
class EAManager:
    def __init__(self):
        self.executions: Dict[str, EAExecution] = {}
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
    
    async def start_algorithm(self, request: StartAlgorithmRequest):
        # Launch EA subprocess with credentials
        
    async def stop_algorithm(self, execution_id: str):
        # Terminate EA process
        
    async def pause_algorithm(self, execution_id: str):
        # Create pause.flag file
        
    async def monitor_execution(self, execution_id: str):
        # Background monitoring task
```

#### **3. Authentication Integration (auth.py)**
```python
async def verify_jwt_token(token: str) -> Optional[Dict]:
    # Verify JWT with Django backend
    
async def get_user_from_token(token: str) -> Optional[Dict]:
    # Get user details from Django
    
async def get_mt5_account(user_id: int, account_id: int, token: str):
    # Fetch MT5 account from Django
```

### 🔌 **API Endpoints**

#### **Authentication**
```python
POST /auth/token        # Get JWT token (delegate to Django)
```

#### **Algorithm Management**
```python
GET  /algorithms                    # List available EAs
GET  /algorithms/status             # Get all EA statuses
POST /algorithms/{id}/start         # Start specific EA
POST /algorithms/{id}/stop          # Stop specific EA
POST /algorithms/{id}/pause         # Pause specific EA
POST /algorithms/{id}/resume        # Resume specific EA
GET  /algorithms/{id}/status        # Get EA status
WS   /ws/algorithms/{id}           # Real-time updates
```

#### **Service Health**
```python
GET  /health           # Service health check
GET  /service/status   # Detailed service status
```

### 📊 **Data Models**

#### **Request Models**
```python
class StartAlgorithmRequest(BaseModel):
    account_id: int
    symbol: str
    config: Optional[Dict[str, Any]] = {}

class AlgorithmConfig(BaseModel):
    symbol: str
    risk_percentage: float = 1.0
    max_positions: int = 5
    stop_loss_pips: float = 20.0
```

#### **Response Models**
```python
class AlgorithmStatus(BaseModel):
    execution_id: str
    algorithm_name: str
    status: str  # running/stopped/paused/error
    pid: Optional[int]
    started_at: Optional[datetime]
    symbol: str
    account_id: int

class EAServiceConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8001
    debug: bool = True
    cors_origins: List[str]
```

### 🔐 **Authentication Flow**

#### **JWT Integration**
```python
# Dependency injection for protected endpoints
async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = await verify_jwt_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user
```

#### **Django Backend Integration**
```python
# Verify tokens with Django backend
async def verify_jwt_token(token: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.django_api_base}/auth/verify-token/",
            json={"token": token}
        )
        return response.json() if response.status_code == 200 else None
```

### 🔄 **Process Management**

#### **EA Execution Lifecycle**
```python
class EAExecution:
    execution_id: str
    algorithm_name: str
    process: Optional[subprocess.Popen]
    status: str
    pid: Optional[int]
    config: Dict[str, Any]
    
    async def start(self):
        # Launch EA subprocess with environment variables
        
    async def stop(self):
        # Gracefully terminate process
        
    async def pause(self):
        # Create pause.flag file
        
    async def resume(self):
        # Remove pause.flag file
```

#### **Environment Variable Injection**
```python
# Dynamic credential passing
env_vars = os.environ.copy()
env_vars.update({
    'MT5_ACCOUNT_NUMBER': str(account['account_number']),
    'MT5_PASSWORD': account['password'],
    'MT5_SERVER': account['server'],
    'MT5_ACCOUNT_ID': str(account['id']),
    'MT5_BROKER_NAME': account['broker_name']
})
```

### 🌐 **WebSocket Communication**

#### **Real-time Updates**
```python
class WebSocketManager:
    def __init__(self):
        self.connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, execution_id: str):
        # Add connection to monitoring
        
    async def disconnect(self, websocket: WebSocket, execution_id: str):
        # Remove connection
        
    async def broadcast_status(self, execution_id: str, status: Dict):
        # Send updates to all connected clients
```

#### **Message Types**
```python
class WebSocketMessage(BaseModel):
    type: str  # status_update/error/notification
    execution_id: str
    data: Dict[str, Any]
    timestamp: datetime
```

### 🔧 **Configuration Management**

#### **Settings (config.py)**
```python
class Settings(BaseSettings):
    # Service configuration
    host: str = "0.0.0.0"
    port: int = 8001
    debug: bool = True
    
    # Django integration
    django_backend_url: str = "http://127.0.0.1:8000"
    django_api_base: str = "http://127.0.0.1:8000/api"
    
    # EA configuration
    algorithmsmt5ea_path: str = "../ALGORITHMSMT5EA"
    mt5_executable_path: str = "C:/Program Files/MetaTrader 5/terminal64.exe"
    
    # JWT settings
    jwt_secret_key: str = "your-secret-key"
    jwt_algorithm: str = "HS256"
```

#### **Environment Variables (.env)**
```env
EA_SERVICE_HOST=0.0.0.0
EA_SERVICE_PORT=8001
DEBUG=True

DJANGO_BACKEND_URL=http://127.0.0.1:8000
DJANGO_SECRET_KEY=your-django-secret-key

ALGORITHMSMT5EA_PATH=../ALGORITHMSMT5EA
MT5_EXECUTABLE_PATH=C:/Program Files/MetaTrader 5/terminal64.exe
```

### 🚀 **Service Startup**

#### **Development Startup**
```bash
# Windows
start_dev.bat

# Unix/Linux
chmod +x start_dev.sh
./start_dev.sh

# Manual
python main.py
```

#### **Production Deployment**
```bash
# Using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4

# Using Docker
docker build -t ea-service .
docker run -p 8001:8001 ea-service
```

### 🔗 **Integration Points**

#### **With Django Backend**
1. **Authentication**: JWT token validation
2. **User Data**: Fetch user and MT5 account info
3. **Execution Sync**: Update execution status
4. **Database**: Read MT5 accounts and user data

#### **With ALGORITHMSMT5EA**
1. **Process Launch**: Start EA subprocesses
2. **Credential Injection**: Environment variables
3. **Control Files**: pause.flag system
4. **Monitoring**: Process health checks

#### **With Frontend**
1. **API Calls**: Algorithm management
2. **WebSocket**: Real-time status updates
3. **Authentication**: JWT token handling

### 📊 **Monitoring & Logging**

#### **Process Monitoring**
```python
async def monitor_execution(self, execution_id: str):
    while execution.status == "running":
        # Check process health
        # Monitor resource usage
        # Send periodic status updates
        await asyncio.sleep(5)
```

#### **Logging Configuration**
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 🛡️ **Error Handling**

#### **Graceful Failures**
```python
try:
    process = await self.start_ea_process(config)
except Exception as e:
    logger.error(f"Failed to start EA: {e}")
    await self.websocket_manager.broadcast_error(execution_id, str(e))
    raise HTTPException(status_code=500, detail=str(e))
```

#### **Process Recovery**
```python
async def health_check(self):
    # Check if EA processes are still running
    # Restart failed processes if needed
    # Update execution statuses
```

### 🎯 **Current Status**

#### **✅ Implemented**
- Complete FastAPI service architecture
- JWT authentication integration
- EA process management
- WebSocket real-time communication
- Configuration management
- Error handling and logging

#### **🔄 In Development**
- Django backend integration
- Advanced monitoring
- Performance metrics
- Auto-recovery mechanisms

#### **📅 Future Enhancements**
- Horizontal scaling support
- Advanced analytics
- Resource optimization
- Container orchestration support

### 🚀 **Service Benefits**

#### **Separation of Concerns**
- Dedicated EA management
- Independent scaling
- Specialized monitoring
- Isolated failures

#### **Production Ready**
- Process management
- Real-time monitoring
- Comprehensive logging
- Error recovery

#### **Integration Friendly**
- RESTful APIs
- WebSocket support
- JWT authentication
- Docker compatible
