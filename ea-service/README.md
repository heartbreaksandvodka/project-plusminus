# EA Service Production Deployment

## Overview
This EA Service provides dedicated Expert Advisor management on port 8001, separate from the main Django backend (port 8000).

## Quick Start

### Windows
```bash
# Run the batch file
start_dev.bat
```

### Linux/Mac
```bash
# Make executable and run
chmod +x start_dev.sh
./start_dev.sh
```

### Manual Start
```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your settings
# Start service
python main.py
```

## Architecture

### Service Ports
- **Django Backend**: Port 8000 (Development & API)
- **EA Service**: Port 8001 (Production EA Management)

### Authentication
- JWT tokens from Django backend
- User authentication via `/auth/token`
- Protected endpoints require valid tokens

### API Endpoints

#### Authentication
- `POST /auth/token` - Get JWT token using Django credentials

#### EA Management
- `GET /algorithms` - List available EAs
- `GET /algorithms/status` - Get all EA statuses
- `POST /algorithms/{algorithm_id}/start` - Start EA
- `POST /algorithms/{algorithm_id}/stop` - Stop EA
- `POST /algorithms/{algorithm_id}/pause` - Pause EA
- `POST /algorithms/{algorithm_id}/resume` - Resume EA
- `GET /algorithms/{algorithm_id}/status` - Get EA status

#### WebSocket
- `WS /ws` - Real-time EA status updates

### EA Integration
- Uses dynamic credentials from Django backend
- Interfaces with ALGORITHMSMT5EA folder
- Maintains process monitoring and control
- File-based pause/resume system

## Configuration

### Environment Variables (.env)
```env
# Service Configuration
EA_SERVICE_HOST=0.0.0.0
EA_SERVICE_PORT=8001
DEBUG=True

# Django Backend Integration
DJANGO_BACKEND_URL=http://localhost:8000
DJANGO_SECRET_KEY=your-django-secret-key

# EA Configuration
ALGORITHMSMT5EA_PATH=../ALGORITHMSMT5EA
MT5_EXECUTABLE_PATH=C:/Program Files/MetaTrader 5/terminal64.exe
```

## Development

### File Structure
```
ea-service/
├── main.py              # FastAPI application
├── config.py           # Settings management
├── models.py           # Pydantic data models
├── auth.py             # Authentication integration
├── ea_manager.py       # EA lifecycle management
├── websocket_handler.py # Real-time communication
├── requirements.txt    # Dependencies
├── .env.example        # Configuration template
├── start_dev.bat       # Windows startup script
├── start_dev.sh        # Unix startup script
└── README.md           # This file
```

### Key Features
1. **Process Management**: Full EA lifecycle control
2. **Real-time Monitoring**: WebSocket status updates
3. **Authentication**: Django backend integration
4. **Dynamic Credentials**: Secure MT5 account management
5. **Error Handling**: Comprehensive error management
6. **Logging**: Detailed operation logging

### Integration with Django Backend
- EA Service handles process management
- Django backend provides authentication
- Shared credential system for MT5 accounts
- RESTful communication between services

## Production Deployment

### Security Considerations
- Change default secret keys
- Use HTTPS in production
- Implement rate limiting
- Configure proper CORS settings

### Monitoring
- Process health checks
- Resource usage monitoring
- Error logging and alerting
- Performance metrics

### Scalability
- Horizontal scaling capability
- Load balancer compatibility
- Database connection pooling
- Caching layer support

## Troubleshooting

### Common Issues
1. **Port Conflicts**: Ensure port 8001 is available
2. **EA Startup**: Check MT5 installation and permissions
3. **Authentication**: Verify Django backend connectivity
4. **Process Control**: Check file permissions for pause flags

### Logs
- Service logs: Console output during development
- EA logs: Individual EA log files in ALGORITHMSMT5EA folders
- Error logs: Detailed error information and stack traces

### Support
- Check Django backend logs for authentication issues
- Verify EA folder structure and permissions
- Ensure MT5 is properly installed and configured
