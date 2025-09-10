#!/usr/bin/env python3
"""
Test script for Flask development server functionality.
Verifies that the Flask development server can start and serves the expected endpoints.
"""

import sys
import os
import time
import threading
import requests
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_flask_app():
    """Test Flask development server functionality."""
    
    # Set development environment
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    
    # Import Flask app
    from app import app
    
    print("🧪 Testing Flask Development Server")
    print("-" * 40)
    
    # Test 1: Basic app configuration
    print("✅ Test 1: App configuration")
    assert app.config['DEBUG'] is True, "Debug mode should be enabled"
    assert app.config['TEMPLATES_AUTO_RELOAD'] is True, "Template auto-reload should be enabled"
    print("   - Debug mode: ✅")
    print("   - Template auto-reload: ✅")
    
    # Test 2: Routes are registered
    print("✅ Test 2: Route registration")
    routes = [rule.rule for rule in app.url_map.iter_rules()]
    expected_routes = ['/', '/api/ask', '/healthz', '/status']
    
    for route in expected_routes:
        assert route in routes, f"Route {route} should be registered"
        print(f"   - {route}: ✅")
    
    # Test 3: Test with development client
    print("✅ Test 3: Endpoint responses")
    with app.test_client() as client:
        # Test health endpoint
        response = client.get('/healthz')
        assert response.status_code == 200
        assert b'auto-reload verified' in response.data
        print("   - /healthz: ✅")
        
        # Test status endpoint
        response = client.get('/status')
        assert response.status_code == 200
        data = response.get_json()
        assert data['debug_mode'] is True
        assert data['auto_reload'] is True
        print("   - /status: ✅")
        
        # Test main page
        response = client.get('/')
        assert response.status_code == 200
        print("   - /: ✅")
    
    print("\n🎉 All tests passed! Flask development server is working correctly.")
    print("🚀 The application is ready for development with auto-reload enabled.")
    
    return True

if __name__ == '__main__':
    try:
        success = test_flask_app()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)