#!/usr/bin/env python3
"""
Main entry point for the Mask Detection Flask Application
"""
import os
from app import create_app

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    print("🎭 Starting Mask Detection Flask Application...")
    print(f"📍 Running in {app.config.get('FLASK_ENV', 'development')} mode")
    print(f"🔧 Debug mode: {app.config['DEBUG']}")
    
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    
    print(f"🌐 Server will be available at: http://{host}:{port}")
    print("📱 Use Ctrl+C to stop the server")
    
    app.run(
        host=host,
        port=port,
        debug=app.config['DEBUG']
    )