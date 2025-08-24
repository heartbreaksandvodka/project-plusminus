# Project Plus-Minus 🚀

A full-stack authentication system built with Django REST Framework and React TypeScript, featuring comprehensive user management, password reset functionality, modern UI design, and **real-time WebSocket infrastructure for MetaTrader 5 Expert Advisors**.

## 🌟 Latest Updates

### ✅ EA Authentication System - PRODUCTION READY (August 24, 2025)
- **Two-Tier Authentication**: User JWT tokens + EA-specific tokens
- **WebSocket Integration**: Real-time communication with trading algorithms
- **Connection Monitoring**: Full logging and usage tracking for EA connections
- **Secure Token Management**: SHA256 hashing, 30-day expiration, IP validation
- **Production Testing**: Complete authentication flow validated and operational

📖 **[Complete EA Implementation Guide](EA_AUTHENTICATION_IMPLEMENTATION_COMPLETE.md)**

## 🌟 Core Features

### Backend (Django)
- **JWT Authentication** with refresh tokens
- **EA Token Authentication** for trading algorithms
- **WebSocket Infrastructure** with Django Channels and ASGI
- **Custom User Model** with extended profile fields
- **Password Reset System** with secure token-based reset
- **Enhanced Dashboard API** with user statistics
- **CORS Configuration** for frontend integration
- **Token Blacklisting** on logout for security
- **RESTful API** endpoints for all authentication operations
- **Real-time Communication** for MetaTrader 5 Expert Advisors

### Frontend (React + TypeScript)
- **Modern UI Design** with responsive layout
- **Organized Component Structure** with dedicated folders
- **Authentication Context** for global state management
- **Protected Routes** with authentication checks
- **Password Reset Flow** with email-based reset
- **Profile Management** with update capabilities
- **Sidebar Navigation** with user information
- **Common Components** for reusability (Button, LoadingSpinner)
- **Centralized API Services** with Axios interceptors
  - JWT token management with auto-refresh
  - Authentication context and protected routes
  - Beautiful gradient design

### Expert Advisors (MetaTrader 5)
- **Professional EA Collection** with 7+ trading strategies
- **WebSocket Connectivity** for real-time backend communication
- **EA Token Authentication** for secure algorithm connections
- **Centralized Python Environment** for development
- **AWS VPS Deployment** ready for 24/7 trading
- **Comprehensive Testing** and validation tools

## 📁 Project Structure

```
project-plusminus/
├── .venv/                          # Python virtual environment
├── backend/                        # Django REST API + WebSocket Server
│   ├── manage.py
│   ├── requirements.txt
│   ├── db.sqlite3
│   ├── authproject/               # Django project settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py               # ASGI configuration for WebSocket
│   │   └── ...
│   ├── authentication/            # Authentication app
│   │   ├── models.py             # User model & password reset
│   │   ├── ea_models.py          # EA authentication models
│   │   ├── ea_views.py           # EA token management API
│   │   ├── views.py              # API endpoints
│   │   ├── serializers.py        # Data serialization
│   │   ├── urls.py               # URL routing
│   │   └── migrations/           # Database migrations
│   └── mt5_integration/           # WebSocket consumer for EAs
│       ├── consumers.py          # WebSocket consumer with EA auth
│       ├── models.py             # Trading data models
│       ├── routing.py            # WebSocket URL routing
│       └── ...
├── frontend/                      # React TypeScript app
│   ├── package.json
│   ├── src/
│   │   ├── components/           # Organized components
│   │   │   ├── Layout/          # Main layout wrapper
│   │   │   ├── Sidebar/         # Navigation sidebar
│   │   │   ├── ProtectedRoute/  # Route protection
│   │   │   └── common/          # Reusable components
│   │   ├── pages/               # Page components
│   │   ├── services/            # API services
│   │   │   ├── api/            # Authentication API
│   │   │   └── utils/          # Helper utilities
│   │   ├── contexts/            # React contexts
│   │   └── types/               # TypeScript types
│   └── public/                   # Static assets
└── ALGORITHMSMT5EA/              # Expert Advisors Collection
    ├── websocket_client.py       # WebSocket client for EAs
    ├── test_ea_token_auth.py     # EA authentication test
    ├── common_ea.py              # Shared EA utilities
    ├── global_config.py          # Global configuration
    ├── trailing_stop_ea/         # Risk-based trailing stop
    ├── grid_trading_ea/          # Grid trading strategy
    ├── trend_following_ea/       # Fast trend following
    ├── hf_scalping_ea/           # High-frequency scalping
    ├── liquidity_ea/             # Liquidity provider
    ├── news_ea/                  # News-based trading
    └── smart_hedging_ea/         # Smart hedging system
```

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 16+
- npm or yarn

### Backend Setup
1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

5. **Start the Django development server**
   ```bash
   python manage.py runserver
   ```
   Backend will be available at `http://localhost:8000`

### Frontend Setup
1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the React development server**
   ```bash
   npm start
   ```
   Frontend will be available at `http://localhost:3000`

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the backend directory:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

## 🎯 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/token/refresh/` - Refresh JWT token
- `GET /api/auth/user/` - Get current user info
- `PUT /api/auth/user/` - Update user profile

### Password Reset
- `POST /api/auth/password/forgot/` - Request password reset
- `POST /api/auth/password/reset/` - Reset password with token

### Dashboard
- `GET /api/auth/dashboard/` - Get dashboard data (protected)
    │   ├── components/
    │   ├── contexts/
    │   ├── pages/
    │   ├── services/
    │   ├── types/
    │   └── App.tsx
    └── public/
```

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows
   # source venv/bin/activate    # On macOS/Linux
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Start the Django server:
   ```bash
   python manage.py runserver
   ```

   The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the React development server:
   ```bash
   npm start
   ```

   The frontend will be available at `http://localhost:3000`

## API Endpoints

### Authentication Endpoints

- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/token/refresh/` - Refresh JWT token
- `GET /api/auth/profile/` - Get user profile (protected)
- `PUT /api/auth/update-profile/` - Update user profile (protected)
- `GET /api/auth/dashboard/` - Dashboard data (protected)

### Request/Response Examples

#### Register
```json
// POST /api/auth/register/
{
  "email": "user@example.com",
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe",
  "password": "securepassword123",
  "password_confirm": "securepassword123"
}
```

#### Login
```json
// POST /api/auth/login/
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

#### Response
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "date_joined": "2024-01-01T00:00:00.000Z"
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

## Frontend Routes

- `/` - Home page
- `/login` - Login page
- `/register` - Registration page
- `/dashboard` - Dashboard (protected route)

## Technologies Used

### Backend
- Django 4.2.7
- Django REST Framework
- Django REST Framework SimpleJWT
- Django CORS Headers
- Python Decouple
- SQLite (default database)

### Frontend
- React 18 with TypeScript
- React Router DOM
- Axios
- Modern CSS with gradients and animations

## Key Features

### JWT Token Management
- Automatic token refresh on API calls
- Token storage in localStorage
- Automatic logout on token expiration

### Authentication Context
- React Context for global auth state
- Protected routes component
- Persistent authentication across page refreshes

### Modern UI Design
- Gradient backgrounds
- Smooth animations and transitions
- Responsive design
- Form validation and error handling

## Environment Variables

Create a `.env` file in the backend directory:

```env
SECRET_KEY=your-secret-key-here-change-this-in-production
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## Usage

1. Start both backend and frontend servers
2. Visit `http://localhost:3000` in your browser
3. Register a new account or login with existing credentials
4. Upon successful authentication, you'll be redirected to the dashboard
5. The dashboard shows user information and provides logout functionality

## Security Features

- Email-based authentication
- Password validation
- JWT token expiration and refresh
- Token blacklisting on logout
- CORS configuration
- Protected API endpoints

## Future Enhancements

- Password reset functionality
- Email verification
- User profile picture upload
- Two-factor authentication
- Admin panel integration
- Database migration to PostgreSQL
- Docker containerization
- Deployment configuration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source and available under the MIT License.

## 📘 Additional Documentation

- [MT5 Backend Integration](MT5_BACKEND_README.md): Detailed overview of the MT5 integration backend, including server-side logic and database structure.
