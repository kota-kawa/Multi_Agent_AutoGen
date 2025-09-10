#!/usr/bin/env python3
"""
Local development server runner for AutoGen Orchestrator.
Runs Flask development server with auto-reload for immediate file change reflection.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path so we can import app
sys.path.insert(0, str(Path(__file__).parent))

def find_available_port(start_port=8000, max_attempts=10):
    """Find an available port starting from start_port."""
    import socket
    for i in range(max_attempts):
        port = start_port + i
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(('0.0.0.0', port))
                return port
            except OSError:
                continue
    return None

def main():
    """Run Flask development server with optimal settings for local development."""
    
    # Set development environment variables
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    
    # Import after setting environment variables
    from app import app
    
    # Find available port
    port = find_available_port(8000)
    if not port:
        print("❌ Could not find an available port. Please check if other services are running.")
        sys.exit(1)
    
    # Configure Flask for development
    app.config.update(
        DEBUG=True,
        TEMPLATES_AUTO_RELOAD=True,
        SEND_FILE_MAX_AGE_DEFAULT=0,
        # Additional development settings
        EXPLAIN_TEMPLATE_LOADING=False,  # Set to True for template debugging
    )
    
    print("🚀 Starting AutoGen Orchestrator Development Server")
    print("📁 Auto-reload enabled for:")
    print("   • Python files (.py)")
    print("   • HTML templates")
    print("   • CSS and JavaScript files")
    print("   • Environment files (.env)")
    print(f"🌐 Server will be available at: http://localhost:{port}")
    if port != 8000:
        print(f"⚠️  Note: Using port {port} instead of 8000 (port was in use)")
    print("⚡ Press Ctrl+C to stop the server")
    print("-" * 60)
    
    try:
        # Run Flask development server with optimal settings
        app.run(
            host='0.0.0.0',  # Accept connections from all interfaces
            port=port,       # Use available port
            debug=True,      # Enable debug mode
            use_reloader=True,    # Enable auto-reload on file changes
            use_debugger=True,    # Enable interactive debugger
            threaded=True,   # Enable threading for better performance
            extra_files=[    # Additional files to watch for changes
                '.env',
                'requirements.txt'
            ]
        )
    except KeyboardInterrupt:
        print("\n👋 Development server stopped.")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()