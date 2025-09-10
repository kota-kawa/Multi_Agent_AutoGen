# Multi_Agent_AutoGen

## Development Server

This application uses Flask's development server with automatic reload functionality instead of Gunicorn for a better development experience.

### Running the Application

#### Local Development
```bash
cd orchestrator
pip install -r requirements.txt
FLASK_ENV=development FLASK_DEBUG=1 python app.py
```

The server will automatically reload when you make changes to the code files.

#### Docker Development
```bash
cd orchestrator
docker-compose up --build
```

The development server runs with debug mode and auto-reload enabled.

### Features

- **Auto-reload**: Code changes are automatically reflected without restarting the server
- **Debug mode**: Enhanced error messages and debugging capabilities
- **Mock fallback**: Works without API keys for development and testing

### Endpoints

- `GET /` - Main application interface
- `GET /healthz` - Health check endpoint
- `GET /status` - Server status including debug and auto-reload information
- `POST /api/ask` - Main API endpoint for agent interactions