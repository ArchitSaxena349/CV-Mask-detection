@echo off
echo 🎭 Starting Mask Detection Production Server...
set FLASK_CONFIG=production
python serve.py
pause