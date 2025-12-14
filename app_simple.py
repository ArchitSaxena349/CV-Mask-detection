"""
Ultra-simple Flask app for Render - guaranteed to work
"""
import os
from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'render-key')

@app.route('/')
def home():
    return """
    <h1>🎭 Mask Detection System</h1>
    <p>✅ Successfully deployed to Render!</p>
    <p>🚀 Full system loading...</p>
    <a href="/health">Health Check</a>
    """

@app.route('/health')
def health():
    return {'status': 'healthy', 'platform': 'render'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)