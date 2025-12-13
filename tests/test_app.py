"""
Test Flask application
"""
import pytest
from app import create_app

def test_app_creation():
    """Test app factory"""
    app = create_app('testing')
    assert app.config['TESTING'] is True

def test_home_page(client):
    """Test home page"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'mask detector' in response.data.lower()

def test_image_detector_page(client):
    """Test image detector page"""
    response = client.get('/image-mask-detector')
    assert response.status_code == 200

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/api/v1/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert 'timestamp' in data

def test_detailed_health_check(client):
    """Test detailed health check"""
    response = client.get('/api/v1/health/detailed')
    assert response.status_code == 200
    data = response.get_json()
    assert 'system' in data
    assert 'model' in data

def test_metrics_endpoint(client):
    """Test metrics endpoint"""
    response = client.get('/api/v1/metrics')
    assert response.status_code == 200
    assert response.content_type == 'text/plain; charset=utf-8'