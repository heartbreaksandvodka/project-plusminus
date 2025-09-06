# Frontend Architecture Guide
## React + TypeScript Frontend

### 🏗️ **Architecture Overview**
```
┌─────────────────────────────────────────────────┐
│                 FRONTEND                        │
│                (Port 3000)                     │
│  ┌─────────────────────────────────────────┐    │
│  │           React Router                  │    │
│  │  /login  /dashboard  /algorithms       │    │
│  └─────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────┐    │
│  │        Authentication Context          │    │
│  │     JWT Token Management              │    │
│  └─────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────┐    │
│  │          API Services                   │    │
│  │  - Django Backend (Port 8000)         │    │
│  │  - EA Service (Port 8001)             │    │
│  └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

### 📁 **Folder Structure**
```
frontend/
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── auth/         # Login, Register, ProtectedRoute
│   │   ├── dashboard/    # Dashboard components
│   │   ├── algorithms/   # EA management components
│   │   └── layout/       # Layout, Sidebar, Header
│   ├── services/         # API integration
│   │   └── api/
│   │       ├── client.ts      # Axios configuration
│   │       ├── auth.ts        # Authentication API
│   │       ├── mt5.ts         # MT5 & EA management API
│   │       └── index.ts       # API exports
│   ├── contexts/         # React contexts
│   │   ├── AuthContext.tsx    # Authentication state
│   │   └── SettingsContext.tsx # App settings
│   ├── types/           # TypeScript definitions
│   │   ├── auth.ts      # Auth types
│   │   └── mt5.ts       # MT5 types
│   ├── pages/           # Route components
│   │   ├── Home.tsx
│   │   ├── Login.tsx
│   │   ├── Dashboard.tsx
│   │   └── Algorithms.tsx
│   └── App.tsx          # Main app component
├── public/              # Static assets
└── package.json         # Dependencies
```

### 🔌 **API Integration**

#### **1. Django Backend Communication (Port 8000)**
```typescript
// Base API configuration
const API_BASE_URL = 'http://localhost:8000/api';

// Authentication endpoints
- POST /login/           # User login
- POST /register/        # User registration
- POST /logout/          # User logout
- GET /profile/          # User profile
- PUT /update-profile/   # Update profile

// MT5 Account Management
- GET /mt5/account/      # Get user's MT5 account
- POST /mt5/account/     # Create MT5 account
- POST /mt5/test-connection/  # Test MT5 connection
```

#### **2. EA Service Communication (Future Integration)**
```typescript
// EA Service endpoints (Port 8001)
const EA_SERVICE_URL = 'http://localhost:8001';

// Algorithm management
- GET /algorithms        # List available EAs
- POST /algorithms/{id}/start   # Start EA
- POST /algorithms/{id}/stop    # Stop EA
- GET /algorithms/status        # Get all EA statuses
- WS /ws/algorithms/{id}        # Real-time EA updates
```

### 🔐 **Authentication Flow**

#### **JWT Token Management**
```typescript
// Automatic token refresh on API calls
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Auto-refresh token
      const newToken = await refreshToken();
      // Retry original request
    }
  }
);
```

#### **Protected Routes**
```typescript
<ProtectedRoute>
  <Layout>
    <Dashboard />
  </Layout>
</ProtectedRoute>
```

### 🎨 **UI Components**

#### **Key Components**
- **AuthProvider**: Global authentication state
- **ProtectedRoute**: Route protection wrapper
- **Layout**: Sidebar navigation layout
- **MT5AccountCard**: MT5 account display/management
- **AlgorithmCard**: Individual EA control panel

#### **State Management**
- **React Context**: Authentication and settings
- **Local State**: Component-specific state
- **localStorage**: Token persistence

### 🚀 **Development Setup**

#### **Start Development Server**
```bash
cd frontend
npm install
npm start
# Frontend runs on http://localhost:3000
```

#### **Environment Configuration**
```env
# Create .env.local
REACT_APP_API_BASE_URL=http://localhost:8000/api
REACT_APP_EA_SERVICE_URL=http://localhost:8001
```

### 🔗 **Integration Points**

#### **With Django Backend**
1. **Authentication**: JWT token-based auth
2. **User Management**: Profile, settings, subscriptions
3. **MT5 Accounts**: Account setup and verification
4. **Payment Processing**: Subscription management

#### **With EA Service** (Future)
1. **Algorithm Control**: Start/stop/pause EAs
2. **Real-time Status**: WebSocket updates
3. **Performance Metrics**: EA analytics
4. **Configuration**: EA parameter management

#### **With ALGORITHMSMT5EA**
1. **Indirect**: Through backend API calls
2. **No Direct**: No direct frontend-to-EA communication
3. **Status Updates**: Via backend WebSocket consumers

### 📊 **Data Flow**

#### **User Login Flow**
```
User Input → Frontend → Django Backend → JWT Token → Local Storage
```

#### **EA Management Flow**
```
Frontend → Django Backend → EA Service → ALGORITHMSMT5EA
```

#### **Real-time Updates**
```
ALGORITHMSMT5EA → WebSocket → Django Backend → Frontend
```

### 🛡️ **Security Considerations**

#### **Token Security**
- JWT tokens stored in localStorage
- Automatic token refresh
- Logout on token expiration
- HTTPS required in production

#### **API Security**
- CORS configured for localhost during development
- Bearer token authorization headers
- Request/response validation

### 🎯 **Current Status**

#### **✅ Implemented**
- Complete authentication system
- MT5 account management UI
- Protected routing
- Responsive design
- Error handling

#### **🔄 In Progress**
- EA Service integration
- Real-time algorithm status
- Advanced algorithm management

#### **📅 Future Enhancements**
- WebSocket real-time updates
- Advanced charting
- Performance analytics dashboard
- Mobile responsiveness optimization
