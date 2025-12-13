#!/usr/bin/env python3
"""
Production server script - Render compatible with full features
"""
import os
import sys
from waitress import serve
from app import create_app

def main():
    """Run the production server"""
    # Get configuration
    config_name = os.environ.get('FLASK_CONFIG', 'production')
    
    # Create app with full features
    app = create_app(config_name)
    
    # Server configuration for Render
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 10000))  # Render default
    threads = int(os.environ.get('THREADS', 4))
    
    print(f"🎭 Starting Mask Detection Production Server on Render...")
    print(f"📍 Configuration: {config_name}")
    print(f"🌐 Server: http://{host}:{port}")
    print(f"🧵 Threads: {threads}")
    print(f"🤖 ML Model: Loading TensorFlow model...")
    print(f"📱 Full features available!")
    
    try:
        serve(
            app,
            host=host,
            port=port,
            threads=threads,
            connection_limit=1000,
            cleanup_interval=30,
            channel_timeout=120,
            # Render-specific optimizations
            max_request_body_size=50 * 1024 * 1024,  # 50MB for image uploads
            expose_tracebacks=False,  # Security
            ident='MaskDetectionSystem/1.0'
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()