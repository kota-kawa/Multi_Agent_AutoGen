#!/bin/bash

# Simple development setup script for AutoGen Orchestrator
# This script provides an easy way to start development with Flask auto-reload

set -e

echo "🚀 AutoGen Orchestrator - Development Setup"
echo "============================================"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python
if ! command_exists python3; then
    echo "❌ Python 3 is required but not found"
    exit 1
fi

# Check if we're in the right directory
if [[ ! -f "app.py" ]]; then
    echo "❌ Please run this script from the orchestrator directory"
    exit 1
fi

# Create .env if it doesn't exist
if [[ ! -f ".env" ]]; then
    if [[ -f ".env.example" ]]; then
        echo "📝 Creating .env from .env.example..."
        cp .env.example .env
        echo "⚠️  Please edit .env and add your API keys before starting the server"
    else
        echo "⚠️  No .env file found. You may need to create one with your API keys"
    fi
fi

# Install dependencies if they don't exist
echo "📦 Checking dependencies..."
if ! python3 -c "import flask" >/dev/null 2>&1; then
    echo "Installing Flask dependencies..."
    pip3 install Flask gunicorn python-dotenv
else
    echo "✅ Dependencies are installed"
fi

# Choose start method
echo ""
echo "Choose how to start the development server:"
echo "1. Local Python server (recommended for development)"
echo "2. Docker (for containerized development)"
echo "3. Run tests only"
echo ""
read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo "🌟 Starting local Flask development server..."
        echo "   - Auto-reload: ✅"
        echo "   - Debug mode: ✅"
        echo "   - Hot refresh: ✅"
        echo ""
        python3 run_dev.py
        ;;
    2)
        echo "🐳 Starting Docker development environment..."
        if command_exists docker; then
            if command_exists docker-compose; then
                docker-compose up --build
            else
                docker compose up --build
            fi
        else
            echo "❌ Docker not found. Please install Docker or choose option 1"
            exit 1
        fi
        ;;
    3)
        echo "🧪 Running tests..."
        python3 test_flask_dev.py
        echo "✅ Tests completed"
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again and choose 1-3"
        exit 1
        ;;
esac