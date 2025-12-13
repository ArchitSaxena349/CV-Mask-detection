"""
Configuration and input validation utilities
"""
import os
from pathlib import Path
from PIL import Image
import cv2
import numpy as np
from core.exceptions import InvalidImageError, ConfigurationError
from core.logger import get_logger

logger = get_logger(__name__)

def validate_config(config):
    """Validate application configuration"""
    errors = []
    
    # Check model path
    if hasattr(config, 'MODEL_PATH'):
        model_path = Path(config.MODEL_PATH)
        if not model_path.exists():
            errors.append(f"Model file not found: {model_path}")
    
    # Check secret key in production
    if hasattr(config, 'DEBUG') and not config.DEBUG:
        if not config.SECRET_KEY or config.SECRET_KEY == 'dev-secret-key-change-in-production':
            errors.append("SECRET_KEY must be set for production")
    
    # Check upload settings
    if hasattr(config, 'MAX_CONTENT_LENGTH'):
        if config.MAX_CONTENT_LENGTH <= 0:
            errors.append("MAX_CONTENT_LENGTH must be positive")
    
    if errors:
        raise ConfigurationError(f"Configuration validation failed: {'; '.join(errors)}")
    
    logger.info("Configuration validation passed")

def validate_image_file(file_storage):
    """Validate uploaded image file"""
    if not file_storage:
        raise InvalidImageError("No file provided")
    
    if file_storage.filename == '':
        raise InvalidImageError("No file selected")
    
    # Check file extension
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    file_ext = file_storage.filename.rsplit('.', 1)[1].lower() if '.' in file_storage.filename else ''
    
    if file_ext not in allowed_extensions:
        raise InvalidImageError(f"Invalid file type. Allowed: {', '.join(allowed_extensions)}")
    
    # Try to open and validate the image
    try:
        file_storage.seek(0)  # Reset file pointer
        image = Image.open(file_storage)
        image.verify()  # Verify it's a valid image
        file_storage.seek(0)  # Reset for further processing
        return True
    except Exception as e:
        raise InvalidImageError(f"Invalid image file: {str(e)}")

def validate_image_array(image_array):
    """Validate numpy image array"""
    if image_array is None:
        raise InvalidImageError("Image array is None")
    
    if not isinstance(image_array, np.ndarray):
        raise InvalidImageError("Image must be a numpy array")
    
    if len(image_array.shape) not in [2, 3]:
        raise InvalidImageError("Image must be 2D (grayscale) or 3D (color)")
    
    if image_array.shape[0] == 0 or image_array.shape[1] == 0:
        raise InvalidImageError("Image dimensions cannot be zero")
    
    return True

def validate_camera_index(camera_index):
    """Validate camera index"""
    try:
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            raise InvalidImageError(f"Cannot open camera with index {camera_index}")
        cap.release()
        return True
    except Exception as e:
        raise InvalidImageError(f"Camera validation failed: {str(e)}")