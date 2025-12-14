# PowerShell deployment script for Windows
param(
    [string]$Action = "install",
    [string]$Port = "8000",
    [string]$Environment = "production"
)

Write-Host "🎭 Mask Detection System - Windows Deployment" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

function Install-Dependencies {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
    
    # Check if Python is installed
    try {
        $pythonVersion = python --version
        Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Python not found. Please install Python 3.8+ first." -ForegroundColor Red
        exit 1
    }
    
    # Install requirements
    Write-Host "Installing Python packages..." -ForegroundColor Yellow
    pip install -r requirements.txt
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Dependencies installed successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
}

function Start-Application {
    Write-Host "🚀 Starting Mask Detection System..." -ForegroundColor Yellow
    Write-Host "Environment: $Environment" -ForegroundColor Cyan
    Write-Host "Port: $Port" -ForegroundColor Cyan
    
    $env:FLASK_CONFIG = $Environment
    $env:PORT = $Port
    
    if ($Environment -eq "development") {
        python run.py
    } else {
        python serve.py
    }
}

function Install-Service {
    Write-Host "🔧 Installing Windows Service..." -ForegroundColor Yellow
    
    # Check if pywin32 is installed
    try {
        python -c "import win32service"
        Write-Host "✅ pywin32 found" -ForegroundColor Green
    }
    catch {
        Write-Host "Installing pywin32..." -ForegroundColor Yellow
        pip install pywin32
    }
    
    # Install service
    python windows-service.py install
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Service installed successfully!" -ForegroundColor Green
        Write-Host "Use 'net start MaskDetectionService' to start the service" -ForegroundColor Cyan
    } else {
        Write-Host "❌ Failed to install service" -ForegroundColor Red
    }
}

function Show-Help {
    Write-Host "Usage: .\deploy-windows.ps1 -Action <action> [options]" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Actions:" -ForegroundColor Yellow
    Write-Host "  install     - Install dependencies"
    Write-Host "  start       - Start the application"
    Write-Host "  service     - Install as Windows service"
    Write-Host "  help        - Show this help"
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  -Port       - Port number (default: 8000)"
    Write-Host "  -Environment - Environment (development/production, default: production)"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Cyan
    Write-Host "  .\deploy-windows.ps1 -Action install"
    Write-Host "  .\deploy-windows.ps1 -Action start -Environment development"
    Write-Host "  .\deploy-windows.ps1 -Action service"
}

# Main execution
switch ($Action.ToLower()) {
    "install" { Install-Dependencies }
    "start" { Start-Application }
    "service" { Install-Service }
    "help" { Show-Help }
    default { 
        Write-Host "❌ Unknown action: $Action" -ForegroundColor Red
        Show-Help
    }
}

Write-Host ""
Write-Host "🎉 Operation completed!" -ForegroundColor Green