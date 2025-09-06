# System Integration & Communication Guide
## How All 4 Components Connect & Communicate

### 🌐 **System Overview**
```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           COMPLETE SYSTEM ARCHITECTURE                          │
│                                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │   FRONTEND   │    │   BACKEND    │    │  EA SERVICE  │    │ ALGORITHMSMT5│   │
│  │  (Port 3000) │    │ (Port 8000)  │    │ (Port 8001)  │    │   EA FOLDER  │   │
│  │              │    │              │    │              │    │              │   │
│  │  React +     │◄──►│  Django +    │◄──►│  FastAPI +   │◄──►│  10 Expert   │   │
│  │  TypeScript  │    │  PostgreSQL  │    │  Process Mgr │    │  Advisors    │   │
│  │              │    │              │    │              │    │              │   │
│  └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘   │
│        │                     │                     │                    │       │
│        │                     │                     │                    │       │
│        │                     │                     │                    │       │
│  ┌──────▼──────┐    ┌─────────▼─────────┐    ┌──────▼──────┐    ┌─────────▼──────┐
│  │   Browser   │    │    Database       │    │   Process   │    │   MetaTrader   │
│  │   Client    │    │    SQLite/        │    │  Management │    │   5 Terminal   │
│  │             │    │   PostgreSQL      │    │             │    │               │
│  └─────────────┘    └───────────────────┘    └─────────────┘    └───────────────┘
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 🔄 **Communication Flow Patterns**

#### **1. User Authentication Flow**
```
┌─────────────┐    HTTP POST     ┌─────────────┐    JWT Token     ┌─────────────┐
│  Frontend   │ ────────────────► │   Backend   │ ◄──────────────► │  Database   │
│  (Login UI) │ ◄──────────────── │ (Auth API)  │                  │ (User Data) │
└─────────────┘    JWT Response   └─────────────┘                  └─────────────┘
```

#### **2. EA Management Flow**
```
┌─────────────┐   Start EA API   ┌─────────────┐  Delegate to EA  ┌─────────────┐
│  Frontend   │ ────────────────► │   Backend   │ ────────────────► │ EA Service  │
│ (EA Control)│                  │ (EA API)    │                  │ (FastAPI)   │
└─────────────┘                  └─────────────┘                  └─────────────┘
                                        │                                 │
                                        │                                 │
                                        ▼                                 ▼
                                ┌─────────────┐   Environment Vars ┌─────────────┐
                                │  Database   │ ◄──────────────────│ALGORITHMSMT5│
                                │(Executions) │                    │ EA Process  │
                                └─────────────┘                    └─────────────┘
```

#### **3. Real-time Status Updates**
```
┌─────────────┐                  ┌─────────────┐                  ┌─────────────┐
│ALGORITHMSMT5│   WebSocket      │   Backend   │   WebSocket      │  Frontend   │
│ EA Process  │ ────────────────► │ (Consumer)  │ ────────────────► │ (Status UI) │
└─────────────┘   Status Data    └─────────────┘   UI Updates     └─────────────┘
```

### 🎯 **Detailed Integration Points**

## 1. 🖥️ **Frontend ↔ Backend Integration**

### **HTTP API Communication**
```typescript
// Frontend API client configuration
const API_BASE_URL = 'http://localhost:8000/api';

// Authentication endpoints
- POST /auth/login/          → Django authentication
- POST /auth/register/       → User registration
- GET  /auth/profile/        → User profile data

// MT5 management endpoints
- GET  /mt5/account/         → Get user's MT5 account
- POST /mt5/test-connection/ → Test MT5 credentials
- POST /mt5/start-algorithm/ → Start EA (delegates to EA Service)
```

### **JWT Token Management**
```typescript
// Automatic token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const newToken = await refreshToken();
      // Retry original request with new token
    }
  }
);
```

### **State Management**
```typescript
// React Context for global state
const AuthContext = createContext({
  user: null,
  isAuthenticated: false,
  login: () => {},
  logout: () => {}
});
```

## 2. 🗄️ **Backend ↔ Database Integration**

### **Django ORM Models**
```python
# User authentication
class User(AbstractUser):
    email = EmailField(unique=True)
    # Additional fields...

# MT5 account storage
class MT5Account(models.Model):
    user = ForeignKey(User)
    account_number = BigIntegerField()
    encrypted_password = TextField()
    server = CharField(max_length=100)

# EA execution tracking
class AlgorithmExecution(models.Model):
    user = ForeignKey(User)
    mt5_account = ForeignKey(MT5Account)
    algorithm_name = CharField(max_length=100)
    pid = IntegerField(null=True)
    execution_status = CharField(max_length=20)
```

### **Database Operations**
```python
# Create execution record
execution = AlgorithmExecution.objects.create(
    user=request.user,
    mt5_account=mt5_account,
    algorithm_name=algorithm_name,
    execution_status='starting'
)

# Query user's executions
user_executions = AlgorithmExecution.objects.filter(
    user=request.user,
    execution_status='running'
)
```

## 3. ⚡ **Backend ↔ EA Service Integration**

### **Service Communication**
```python
# Django backend delegates to EA Service
async def start_algorithm_via_service(mt5_account, algorithm_name, symbol):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://127.0.0.1:8001/algorithms/{algorithm_name}/start",
            json={
                "account_id": mt5_account.id,
                "symbol": symbol
            },
            headers={"Authorization": f"Bearer {jwt_token}"}
        )
        return response.json()
```

### **Authentication Delegation**
```python
# EA Service verifies tokens with Django
async def verify_jwt_token(token: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://127.0.0.1:8000/api/auth/verify-token/",
            json={"token": token}
        )
        return response.json() if response.status_code == 200 else None
```

### **Data Synchronization**
```python
# EA Service fetches MT5 account from Django
async def get_mt5_account(account_id: int, token: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://127.0.0.1:8000/api/mt5/accounts/{account_id}/",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()
```

## 4. 🤖 **EA Service ↔ ALGORITHMSMT5EA Integration**

### **Process Management**
```python
# EA Service launches EA subprocess
class EAManager:
    async def start_algorithm(self, request: StartAlgorithmRequest):
        # Get MT5 credentials from Django
        account = await self.get_mt5_account(request.account_id)
        
        # Setup environment variables
        env_vars = {
            'MT5_ACCOUNT_NUMBER': str(account['account_number']),
            'MT5_PASSWORD': account['password'],
            'MT5_SERVER': account['server'],
            'MT5_ACCOUNT_ID': str(account['id'])
        }
        
        # Launch EA subprocess
        script_path = f"../ALGORITHMSMT5EA/{algorithm_name}/mt5_{algorithm_name}.py"
        process = subprocess.Popen(
            [sys.executable, script_path],
            env=env_vars,
            cwd=os.path.dirname(script_path)
        )
        
        return process.pid
```

### **Control Mechanisms**
```python
# File-based control
async def pause_algorithm(self, execution_id: str):
    ea_dir = f"../ALGORITHMSMT5EA/{algorithm_name}"
    pause_flag_path = os.path.join(ea_dir, "pause.flag")
    with open(pause_flag_path, 'w') as f:
        f.write('paused')

# Process termination
async def stop_algorithm(self, execution_id: str):
    if execution.process:
        execution.process.terminate()
        execution.process.wait()
```

## 5. 📡 **Real-time Communication (WebSocket)**

### **Django WebSocket Consumer**
```python
class AlgorithmConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.algorithm_id = self.scope['url_route']['kwargs']['algorithm_id']
        await self.channel_layer.group_add(
            f"algorithm_{self.algorithm_id}",
            self.channel_name
        )
        await self.accept()

    async def algorithm_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'status_update',
            'data': event['data']
        }))
```

### **EA WebSocket Integration**
```python
# ALGORITHMSMT5EA WebSocket client
def setup_ea_websocket_integration(ea_instance, backend_url, algorithm_id, token):
    ws_url = f"{backend_url}/ws/algorithm/{algorithm_id}/"
    
    def on_message(message):
        data = json.loads(message)
        if data['type'] == 'pause':
            ea_instance.pause_trading()
        elif data['type'] == 'resume':
            ea_instance.resume_trading()
    
    ws_client = WebSocketClient(ws_url, token)
    ws_client.on_message = on_message
    return ws_client
```

### **Frontend WebSocket Client**
```typescript
// Real-time status updates in React
const useAlgorithmStatus = (algorithmId: string) => {
  const [status, setStatus] = useState(null);
  
  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/algorithm/${algorithmId}/`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setStatus(data);
    };
    
    return () => ws.close();
  }, [algorithmId]);
  
  return status;
};
```

### 🔐 **Security & Authentication Chain**

#### **Token Flow**
```
1. User logs in → Frontend
2. Frontend → Django Backend (login API)
3. Django → JWT Token → Frontend
4. Frontend → Django (authenticated requests)
5. Django → EA Service (with JWT token)
6. EA Service → Django (token verification)
7. EA Service → ALGORITHMSMT5EA (environment variables)
```

#### **Data Protection**
```python
# Encrypted MT5 passwords in database
class MT5Account(models.Model):
    encrypted_password = models.TextField()  # Encrypted storage
    
    def get_password(self):
        # Decrypt password when needed
        return decrypt_password(self.encrypted_password)
    
    def set_password(self, password):
        # Encrypt password before storage
        self.encrypted_password = encrypt_password(password)
```

### 📊 **Data Flow Examples**

#### **Example 1: Starting an EA**
```
1. User clicks "Start Grid EA" → Frontend
2. Frontend → POST /api/mt5/start-algorithm/ → Django Backend
3. Django → POST /algorithms/grid_trading_ea/start → EA Service
4. EA Service → Fetch MT5 account → Django Backend
5. EA Service → Launch subprocess → ALGORITHMSMT5EA/grid_trading_ea/
6. EA Process → Connect to MT5 → MetaTrader 5
7. EA Process → WebSocket status → Django Backend
8. Django → WebSocket → Frontend (status update)
```

#### **Example 2: Real-time Trading Updates**
```
1. EA executes trade → ALGORITHMSMT5EA
2. EA → WebSocket message → Django Backend
3. Django → Store trade data → Database
4. Django → WebSocket broadcast → Frontend
5. Frontend → Update UI → User sees trade
```

#### **Example 3: Pausing an EA**
```
1. User clicks "Pause" → Frontend
2. Frontend → POST /api/mt5/pause-algorithm/ → Django Backend
3. Django → POST /algorithms/{id}/pause → EA Service
4. EA Service → Create pause.flag → ALGORITHMSMT5EA folder
5. EA Process → Detect pause.flag → Pause execution
6. EA Process → WebSocket status "paused" → Django Backend
7. Django → WebSocket → Frontend (status update)
```

### 🌟 **Integration Benefits**

#### **1. Separation of Concerns**
- **Frontend**: Pure UI/UX, no business logic
- **Backend**: Authentication, data, API orchestration
- **EA Service**: Dedicated process management
- **ALGORITHMSMT5EA**: Pure trading logic

#### **2. Scalability**
- Independent scaling of each component
- Horizontal scaling of EA Service
- Database optimization separate from logic
- Frontend CDN deployment

#### **3. Maintainability**
- Clear boundaries between components
- Independent testing and deployment
- Technology-specific optimizations
- Easy debugging and monitoring

#### **4. Security**
- Layered authentication
- Encrypted credential storage
- Isolated EA processes
- JWT token management

#### **5. Real-time Capabilities**
- WebSocket communication
- Live status updates
- Immediate control responses
- Real-time performance monitoring

### 🚀 **Current Integration Status**

#### **✅ Fully Integrated**
- Frontend ↔ Backend authentication
- Backend ↔ Database ORM
- Backend ↔ ALGORITHMSMT5EA process management
- WebSocket real-time communication

#### **🔄 In Progress**
- Backend ↔ EA Service delegation
- EA Service ↔ ALGORITHMSMT5EA optimization
- Advanced monitoring and analytics

#### **📅 Future Enhancements**
- Load balancing between services
- Advanced caching layers
- Multi-tenant architecture
- Container orchestration
