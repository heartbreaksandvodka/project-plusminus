# Full Stack Django JWT React Authentication

A complete authentication system built with Django REST Framework, JWT tokens, React.js, TypeScript, and Axios.

## Features

- **Backend (Django)**:
  - Django REST Framework API
  - JWT Authentication with refresh tokens
  - Custom User model with email login
  - Token blacklisting on logout
  - CORS configuration
  - User registration, login, logout endpoints
  - Protected dashboard endpoint

- **Frontend (React)**:
  - React with TypeScript
  - Modern, responsive UI design
  - React Router for navigation
  - Axios for HTTP requests
  - JWT token management with auto-refresh
  - Authentication context and protected routes
  - Beautiful gradient design

## Project Structure

```
project-plusminus/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env
│   ├── authproject/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── ...
│   └── authentication/
│       ├── models.py
│       ├── views.py
│       ├── serializers.py
│       ├── urls.py
│       └── ...
└── frontend/
    ├── package.json
    ├── src/
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
