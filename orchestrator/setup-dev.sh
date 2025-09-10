#!/bin/bash

# Setup script for development environment with auto-reload

echo "Setting up AutoGen Orchestrator development environment with Flask dev server..."

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env 2>/dev/null || echo "Note: No .env.example found. You may need to create .env manually with API keys."
    echo "Please edit .env file and add your API keys (optional for development)"
fi

# Build and start the development environment
echo "Building Docker containers..."
docker compose build

echo "Starting Flask development server with auto-reload..."
echo "The server will automatically reload when you change code files."
echo "Access the application at http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo ""
echo "Features enabled:"
echo "- Flask development server (not Gunicorn)"  
echo "- Auto-reload on file changes"
echo "- Debug mode with enhanced error messages"
echo "- Mock mode (works without API keys)"

docker compose up