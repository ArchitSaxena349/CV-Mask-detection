"""
API routes for health checks and monitoring
"""
import psutil
import time
from datetime import datetime, timezone
from flask import jsonify, current_app, Response
from app.api import api_bp
from core.logger import get_logger

logger = get_logger(__name__)

@api_bp.route('/health')
def health_check():
    """Basic health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'version': current_app.config.get('VERSION', '1.0.0'),
        'service': 'mask-detection-system'
    })

@api_bp.route('/health/detailed')
def detailed_health_check():
    """Detailed health check with system metrics"""
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Check model availability
        from core.video_detector import model
        model_status = 'loaded' if model is not None else 'fallback'
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'version': current_app.config.get('VERSION', '1.0.0'),
            'service': 'mask-detection-system',
            'system': {
                'cpu_percent': cpu_percent,
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent
                },
                'disk': {
                    'total': disk.total,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100
                }
            },
            'model': {
                'status': model_status,
                'path': str(current_app.config.get('MODEL_PATH', 'N/A'))
            }
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'error': str(e)
        }), 500

@api_bp.route('/metrics')
def metrics():
    """Prometheus-style metrics endpoint"""
    try:
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        metrics_text = f"""# HELP cpu_usage_percent CPU usage percentage
# TYPE cpu_usage_percent gauge
cpu_usage_percent {cpu_percent}

# HELP memory_usage_percent Memory usage percentage
# TYPE memory_usage_percent gauge
memory_usage_percent {memory.percent}

# HELP memory_available_bytes Available memory in bytes
# TYPE memory_available_bytes gauge
memory_available_bytes {memory.available}
"""
        return Response(metrics_text, status=200, content_type='text/plain; charset=utf-8')
    except Exception as e:
        logger.error(f"Metrics collection failed: {e}")
        return Response("# Metrics collection failed", status=500, content_type='text/plain; charset=utf-8')