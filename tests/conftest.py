"""
Pytest configuration and fixtures
"""
import pytest
import tempfile
import os
from app import create_app

@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app('testing')
    
    # Create a temporary file for testing database
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    
    with app.app_context():
        yield app
    
    os.close(db_fd)
    os.unlink(app.config['DATABASE'])

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()

@pytest.fixture
def sample_image():
    """Create a sample image for testing"""
    import numpy as np
    from PIL import Image
    import io
    
    # Create a simple test image
    img_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    img = Image.fromarray(img_array)
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return img_bytes