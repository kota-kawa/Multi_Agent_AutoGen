#!/bin/bash

# Setup script for development environment with auto-reload

echo "Setting up AutoGen Orchestrator development environment..."

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env file and add your API keys"
fi

# Build and start the development environment
echo "Building Docker containers..."
docker-compose -f docker-compose.dev.yml build

echo "Starting Flask development server with auto-reload..."
echo "Using Flask built-in development server (not gunicorn) for instant code reloading."
echo "The server will automatically reload when you change code files."
echo "Access the application at http://localhost:8000"
echo "Press Ctrl+C to stop the server"

docker-compose -f docker-compose.dev.yml up