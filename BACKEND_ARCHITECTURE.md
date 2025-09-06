# Django Backend Architecture Guide
## REST API Backend + Database Server

### 🏗️ **Architecture Overview**
```
┌─────────────────────────────────────────────────┐
│              DJANGO BACKEND                     │
│                (Port 8000)                     │
│  ┌─────────────────────────────────────────┐    │
│  │           REST API Layer               │    │
│  │     Django REST Framework             │    │
│  └─────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────┐    │
│  │          Business Logic                │    │
│  │   Authentication | MT5 | Payments    │    │
│  └─────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────┐    │
│  │           Database Layer               │    │
│  │     SQLite/PostgreSQL (ORM)          │    │
│  └─────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────┐    │
│  │         WebSocket Layer                │    │
│  │    Django Channels + Redis           │    │
│  └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

### 📁 **Project Structure**
```
backend/
├── authproject/           # Main Django project
│   ├── settings.py       # Django configuration
│   ├── urls.py          # Main URL routing
│   ├── asgi.py          # ASGI configuration
│   └── wsgi.py          # WSGI configuration
├── authentication/       # User management app
│   ├── models.py        # User, PasswordReset models
│   ├── views.py         # Auth API endpoints
│   ├── serializers.py   # Data serialization
│   ├── urls.py          # Auth URL routing
│   └── ea_views.py      # EA token management
├── mt5_integration/      # MT5 & EA management app
│   ├── models.py        # MT5Account, AlgorithmExecution
│   ├── mt5_service.py   # Core MT5 logic
│   ├── consumers.py     # WebSocket consumers
│   ├── urls.py          # MT5 URL routing
│   └── api_views/       # Organized API views
├── payments/             # Payment processing app
│   ├── models.py        # Subscription models
│   ├── views.py         # Payment endpoints
│   └── urls.py          # Payment routing
├── projectplusdatabase/  # EA templates app
│   ├── models.py        # EA metadata models
│   └── views.py         # EA template API
├── manage.py            # Django management
└── requirements.txt     # Python dependencies
```

### 🗄️ **Database Schema**

#### **Authentication Models**
```python
# User model (Custom user)
class User(AbstractUser):
    email = EmailField(unique=True)  # Primary identifier
    first_name = CharField(max_length=30)
    last_name = CharField(max_length=30)
    phone_number = CharField(max_length=15, blank=True)
    is_active = BooleanField(default=True)
    date_joined = DateTimeField(auto_now_add=True)

# Password reset tokens
class PasswordResetToken:
    user = ForeignKey(User)
    token = CharField(max_length=100, unique=True)
    created_at = DateTimeField(auto_now_add=True)
    expires_at = DateTimeField()
```

#### **MT5 Integration Models**
```python
# MT5 trading accounts
class MT5Account(models.Model):
    user = ForeignKey(User)
    account_number = BigIntegerField()
    encrypted_password = TextField()  # Encrypted credentials
    server = CharField(max_length=100)
    broker_name = CharField(max_length=100)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)

# Algorithm execution tracking
class AlgorithmExecution(models.Model):
    user = ForeignKey(User)
    mt5_account = ForeignKey(MT5Account)
    algorithm_name = CharField(max_length=100)
    symbol = CharField(max_length=20)
    execution_status = CharField(max_length=20)  # running/stopped/paused
    pid = IntegerField(null=True)  # Process ID
    started_at = DateTimeField(auto_now_add=True)
    stopped_at = DateTimeField(null=True)
    
# Trading session logs
class MT5TradingSession(models.Model):
    execution = ForeignKey(AlgorithmExecution)
    session_start = DateTimeField()
    session_end = DateTimeField(null=True)
    total_trades = IntegerField(default=0)
    profit_loss = DecimalField(max_digits=10, decimal_places=2)
```

#### **Payment Models**
```python
# Subscription plans
class SubscriptionPlan(models.Model):
    name = CharField(max_length=100)
    price = DecimalField(max_digits=10, decimal_places=2)
    currency = CharField(max_length=3, default='ZAR')
    duration_days = IntegerField()
    
# User subscriptions
class UserSubscription(models.Model):
    user = ForeignKey(User)
    plan = ForeignKey(SubscriptionPlan)
    is_active = BooleanField(default=True)
    start_date = DateTimeField()
    end_date = DateTimeField()
```

### 🔌 **API Endpoints**

#### **Authentication API (`/api/auth/`)**
```python
POST /register/           # User registration
POST /login/             # User login
POST /logout/            # User logout
POST /token/refresh/     # JWT token refresh
GET  /profile/           # User profile
PUT  /update-profile/    # Update profile
POST /change-password/   # Change password
POST /forgot-password/   # Request password reset
POST /reset-password/    # Reset password
GET  /dashboard/         # Dashboard data
GET  /subscriptions/     # User subscriptions
```

#### **MT5 Integration API (`/api/mt5/`)**
```python
# Account Management
GET  /account/           # Get user's MT5 account
POST /account/           # Create MT5 account
PUT  /account/           # Update MT5 account
DELETE /account/         # Delete MT5 account
POST /test-connection/   # Test MT5 connection
POST /refresh-status/    # Refresh account status

# Algorithm Management
GET  /algorithms/        # List algorithm executions
POST /start-algorithm/   # Start algorithm
POST /stop-algorithm/    # Stop algorithm
POST /pause-algorithm/   # Pause algorithm
POST /resume-algorithm/  # Resume algorithm
GET  /algorithm/{id}/status/     # Get algorithm status
GET  /algorithm/{id}/analytics/  # Get analytics
GET  /algorithm/{id}/trades/     # Get trade history
```

#### **Payment API (`/api/payments/`)**
```python
GET  /plans/             # List subscription plans
POST /subscribe/         # Create subscription
POST /webhook/           # Payment webhook
GET  /subscription/status/  # Check subscription status
```

### 🔐 **Authentication System**

#### **JWT Token Configuration**
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
}
```

#### **Security Features**
- Email-based authentication
- JWT token management with refresh
- Token blacklisting on logout
- Password reset with secure tokens
- CORS configuration for frontend
- Permission-based access control

### 🌐 **WebSocket Integration**

#### **Django Channels Configuration**
```python
# Real-time communication with EAs
class AlgorithmConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Handle EA WebSocket connections
        
    async def receive(self, text_data):
        # Process messages from EAs
        
    async def algorithm_update(self, event):
        # Send updates to connected clients
```

#### **WebSocket Endpoints**
```
WS /ws/algorithm/{algorithm_id}/  # Real-time EA communication
```

### 🚀 **Business Logic**

#### **MT5 Service Layer**
```python
class MT5AlgorithmManager:
    @staticmethod
    def start_algorithm(mt5_account, algorithm_name, symbol):
        # Delegate to EA Service (Port 8001)
        
    @staticmethod
    def stop_algorithm(pid):
        # Stop algorithm process
        
    @staticmethod
    def pause_algorithm(pid, algorithm_name):
        # Create pause.flag file
```

#### **Dynamic Credential System**
```python
# Environment variables passed to EA processes
env_vars = {
    'MT5_ACCOUNT_NUMBER': str(mt5_account.account_number),
    'MT5_PASSWORD': mt5_account.get_password(),
    'MT5_SERVER': mt5_account.server,
    'MT5_ACCOUNT_ID': str(mt5_account.id),
    'MT5_BROKER_NAME': mt5_account.broker_name
}
```

### 🔧 **Development Setup**

#### **Start Development Server**
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
# Backend runs on http://localhost:8000
```

#### **Environment Configuration**
```env
# .env file
SECRET_KEY=your-django-secret-key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### 🔗 **Integration Points**

#### **With Frontend**
1. **REST API**: JSON-based communication
2. **JWT Authentication**: Secure token-based auth
3. **CORS**: Cross-origin request handling
4. **WebSocket**: Real-time updates

#### **With EA Service**
1. **API Delegation**: Forward EA requests to port 8001
2. **Authentication**: Provide JWT tokens for EA service
3. **Database Sync**: Share user and execution data

#### **With ALGORITHMSMT5EA**
1. **Process Management**: Launch EA subprocesses
2. **Credential Injection**: Environment variables
3. **WebSocket**: Real-time communication
4. **File-based Control**: pause.flag system

### 📊 **Data Flow**

#### **User Registration Flow**
```
Frontend → Django → User Creation → JWT Token → Response
```

#### **EA Start Flow**
```
Frontend → Django → EA Service → ALGORITHMSMT5EA Process
```

#### **Real-time Updates**
```
ALGORITHMSMT5EA → WebSocket → Django → Frontend
```

### 🛡️ **Security Implementation**

#### **Data Protection**
- Encrypted MT5 passwords in database
- JWT secret key protection
- HTTPS enforcement in production
- SQL injection prevention (ORM)

#### **Access Control**
- User-based permissions
- MT5 account ownership validation
- API rate limiting
- CORS security

### 🎯 **Current Status**

#### **✅ Implemented**
- Complete authentication system
- MT5 account management
- Algorithm execution tracking
- WebSocket communication
- Payment processing integration

#### **🔄 Needs Refactoring**
- EA management delegation to EA Service
- Reduce duplicate EA control logic
- Optimize WebSocket connections

#### **📅 Future Enhancements**
- Database connection pooling
- Redis caching layer
- Advanced logging and monitoring
- Multi-tenant architecture
