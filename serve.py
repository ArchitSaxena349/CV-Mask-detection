#!/usr/bin/env python3
"""
Production server script using Waitress (Windows compatible)
"""
import os
import sys
from waitress import serve
from app import create_app

def main():
    """Run the production server"""
    # Get configuration
    config_name = os.environ.get('FLASK_CONFIG', 'production')
    
    # Create app
    app = create_app(config_name)
    
    # Server configuration
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 8000))
    threads = int(os.environ.get('THREADS', 4))
    
    print(f"🎭 Starting Mask Detection Production Server...")
    print(f"📍 Configuration: {config_name}")
    print(f"🌐 Server: http://{host}:{port}")
    print(f"🧵 Threads: {threads}")
    print(f"📱 Use Ctrl+C to stop the server")
    
    try:
        serve(
            app,
            host=host,
            port=port,
            threads=threads,
            connection_limit=1000,
            cleanup_interval=30,
            channel_timeout=120
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()