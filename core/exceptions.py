"""
Custom exceptions for the Mask Detection System
"""

class MaskDetectionError(Exception):
    """Base exception for mask detection errors"""
    pass

class ModelLoadError(MaskDetectionError):
    """Raised when the ML model fails to load"""
    pass

class CameraError(MaskDetectionError):
    """Raised when camera operations fail"""
    pass

class ImageProcessingError(MaskDetectionError):
    """Raised when image processing fails"""
    pass

class InvalidImageError(MaskDetectionError):
    """Raised when an invalid image is provided"""
    pass

class ConfigurationError(MaskDetectionError):
    """Raised when configuration is invalid"""
    pass