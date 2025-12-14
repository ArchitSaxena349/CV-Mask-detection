# 🪟 Windows Setup Guide

Complete guide for setting up the Mask Detection System on Windows.

## 📋 Prerequisites

### Required Software
- **Python 3.8+** - [Download from python.org](https://www.python.org/downloads/)
- **Git** (optional) - [Download from git-scm.com](https://git-scm.com/download/win)
- **Visual Studio Build Tools** (for some packages) - [Download](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

### Hardware Requirements
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Camera**: USB webcam for live detection (optional)

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
```powershell
# 1. Download and extract the project
# 2. Open PowerShell as Administrator
# 3. Navigate to project directory
cd path\to\mask_detector

# 4. Run automated setup (from project root)
.\scripts\deploy-windows.ps1 -Action install

# 5. Start the application (from project root)
.\scripts\deploy-windows.ps1 -Action start
```

### Option 2: Manual Setup
```cmd
# 1. Create virtual environment
python -m venv .venv

# 2. Activate virtual environment
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run development server
python run.py

# OR run production server
python serve.py
```

### Option 3: Batch Files (Easiest)
```cmd
# 1. Double-click scripts\install.bat
# 2. Double-click scripts\run-dev.bat (development)
# OR double-click scripts\run-prod.bat (production)
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:
```env
FLASK_CONFIG=production
SECRET_KEY=your-secret-key-here
HOST=127.0.0.1
PORT=8000
```

### Windows-Specific Settings
```env
# Use Windows-compatible paths
MODEL_PATH=models\mask_mobilenet.h5

# Windows service configuration
THREADS=4
CONNECTION_LIMIT=1000
```

## 🏃‍♂️ Running the Application

### Development Mode
```cmd
# Method 1: Batch file
scripts\run-dev.bat

# Method 2: Python script
python run.py

# Method 3: PowerShell
.\scripts\deploy-windows.ps1 -Action start -Environment development
```

### Production Mode
```cmd
# Method 1: Batch file
scripts\run-prod.bat

# Method 2: Python script
python serve.py

# Method 3: PowerShell
.\scripts\deploy-windows.ps1 -Action start -Environment production
```

### Windows Service
```powershell
# Install service (run as Administrator)
.\scripts\deploy-windows.ps1 -Action service

# Start service
net start MaskDetectionService

# Stop service
net stop MaskDetectionService

# Remove service
python windows-service.py remove
```

## 🐳 Docker on Windows

### Prerequisites
- **Docker Desktop for Windows** - [Download](https://www.docker.com/products/docker-desktop)

### Commands
```cmd
# Build image
docker build -t mask-detector .

# Run container
docker run -p 8000:8000 mask-detector

# Using Docker Compose
docker-compose up -d
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Python Not Found
```cmd
# Add Python to PATH or use full path
C:\Python39\python.exe run.py
```

#### 2. Permission Errors
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 3. Package Installation Fails
```cmd
# Upgrade pip
python -m pip install --upgrade pip

# Install Visual Studio Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

#### 4. Camera Access Issues
```cmd
# Check camera permissions in Windows Settings
# Settings > Privacy > Camera > Allow apps to access camera
```

#### 5. Port Already in Use
```cmd
# Find process using port
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /PID <process_id> /F
```

### Performance Optimization

#### 1. Increase Virtual Memory
- Control Panel > System > Advanced > Performance Settings
- Set custom size: Initial = 4096MB, Maximum = 8192MB

#### 2. Disable Windows Defender Real-time Protection
- Temporarily for better performance during development

#### 3. Use SSD Storage
- Install on SSD for faster model loading

## 📊 Monitoring on Windows

### Task Manager
- Monitor CPU and memory usage
- Check if service is running

### Event Viewer
- Windows Logs > Application
- Look for "MaskDetectionService" entries

### Performance Monitor
```cmd
# Open Performance Monitor
perfmon

# Add counters for Python processes
```

## 🔐 Security Considerations

### Firewall Configuration
```powershell
# Allow application through Windows Firewall
New-NetFirewallRule -DisplayName "Mask Detection System" -Direction Inbound -Port 8000 -Protocol TCP -Action Allow
```

### User Account Control (UAC)
- Run as Administrator for service installation
- Use standard user for normal operation

### Antivirus Exclusions
Add project folder to antivirus exclusions for better performance.

## 📱 Accessing the Application

Once running, access the application at:
- **Local**: http://localhost:8000
- **Network**: http://YOUR_IP:8000

### Default Endpoints
- **Home**: http://localhost:8000/
- **Image Detector**: http://localhost:8000/image-mask-detector
- **Health Check**: http://localhost:8000/api/v1/health
- **Metrics**: http://localhost:8000/api/v1/metrics

## 🆘 Getting Help

### Log Files
Check logs in the `logs/` directory:
```cmd
type logs\mask_detector.log
```

### System Information
```cmd
# Get system info
systeminfo

# Check Python version
python --version

# Check installed packages
pip list
```

### Support Resources
- Check GitHub Issues
- Review application logs
- Use Windows Event Viewer for service issues

---

**Need more help?** Check the main [README.md](README.md) or create an issue on GitHub.