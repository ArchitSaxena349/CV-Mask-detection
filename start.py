#!/usr/bin/env python3
"""
Simple startup script for Render deployment
"""
import os
from waitress import serve
from app import create_app

# Force production mode
os.environ['FLASK_CONFIG'] = 'production'

# Create Flask app
app = create_app('production')

# Get port from Render environment
port = int(os.environ.get('PORT', 10000))

print(f"🎭 Starting Mask Detection System...")
print(f"🌐 Binding to 0.0.0.0:{port}")
print(f"🚀 Ready for Render deployment!")

# Start server with Render-compatible settings
if __name__ == '__main__':
    serve(
        app,
        host='0.0.0.0',
        port=port,
        threads=4,
        connection_limit=1000
    )