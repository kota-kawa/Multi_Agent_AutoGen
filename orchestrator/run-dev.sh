#!/bin/bash

# Simple Flask development server runner
# This script starts the Flask development server with auto-reload enabled

echo "Starting Flask development server..."
echo "This uses Flask's built-in development server with auto-reload."
echo "Files will be automatically reloaded when changed."
echo "Access the application at http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo ""

# Set development environment
export FLASK_ENV=development
export FLASK_DEBUG=1

# Start Flask development server
python3 app.py