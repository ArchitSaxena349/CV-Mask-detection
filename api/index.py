"""
Vercel entry point for the Mask Detection Flask Application
"""
import os
import sys

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

# Create the Flask application for Vercel
app = create_app('production')

# Vercel expects the app to be available as 'app'
if __name__ == "__main__":
    app.run()