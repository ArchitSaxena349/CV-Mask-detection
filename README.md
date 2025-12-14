# 🎭 Mask Detection System

A modern Flask web application for real-time face mask detection using computer vision and deep learning.

![Demo](mask_detection_live.gif)

## ✨ Features

- **Real-time Detection**: Live camera feed with instant mask detection
- **Image Processing**: Upload and analyze static images
- **Face Detection**: Robust face detection using OpenCV
- **Modern UI**: Clean, responsive Bootstrap interface
- **Fallback Support**: Graceful degradation when ML model is unavailable

## 🏗️ Architecture

```
mask_detector/
├── app/                    # Flask application
│   ├── main/              # Main blueprint (routes)
│   ├── errors/            # Error handling
│   ├── static/            # Static assets
│   └── templates/         # HTML templates
├── core/                  # Core detection logic
│   ├── image_processor.py # Image processing
│   ├── video_detector.py  # Video processing
│   └── utils.py          # Utility functions
├── models/               # ML models
├── config.py            # Configuration
├── run.py              # Development server
└── wsgi.py            # Production WSGI
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Webcam (for live detection)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mask_detector
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   # Development
   python run.py
   
   # Or using Flask CLI
   flask run
   ```

5. **Access the application**
   - Open your browser to `http://127.0.0.1:5000`
   - Click "Start" to begin live detection
   - Or use "Image mask detector" to upload images

## 🛠️ Configuration

The application supports multiple environments through `config.py`:

- **Development**: Debug mode enabled, detailed logging
- **Production**: Optimized for deployment
- **Testing**: Configuration for automated tests

Set environment variables:
```bash
export FLASK_CONFIG=production
export SECRET_KEY=your-secret-key
```

## 🧠 Technology Stack

- **Backend**: Flask, OpenCV, TensorFlow/Keras
- **Frontend**: Bootstrap 4, jQuery
- **ML Model**: MobileNetV2 (fine-tuned for mask detection)
- **Face Detection**: Haar Cascade Classifier

## 📱 API Endpoints

- `GET /` - Home page with live detection
- `GET /image-mask-detector` - Image upload interface
- `POST /image-processing` - Process uploaded images
- `GET /video_feed` - Real-time video stream (MJPEG)
  - Query params:
    - `source`: `camera` (default) or `video`
    - `camera_index`: integer camera index (default `0`)
    - `path`: local video file path when `source=video`
  - Examples:
    - Camera: `http://127.0.0.1:5000/video_feed?source=camera&camera_index=0`
    - Video file: `http://127.0.0.1:5000/video_feed?source=video&path=C:\\videos\\sample.mp4`
  - Behavior:
    - If the selected source cannot be opened, an error frame is streamed once and logged.

### Confidence & Edge Cases
- Each face shows `Mask`, `No mask`, or `Improper` with confidence.
- `Improper` indicates ambiguous detection (e.g., partial mask or improper wear). Colored orange.

### Testing
- Run tests:
  ```bash
  pytest -q
  ```
- Includes health endpoints, metrics, video feed fallback, and classification decoding.

## 🔧 Development

### Project Structure
- Clean separation of concerns
- Blueprint-based Flask architecture
- Configuration management
- Error handling and logging

### Code Quality
- Type hints where applicable
- Comprehensive error handling
- Fallback mechanisms for model failures
- Clean, documented code

## 🚀 Deployment

### Production Deployment

#### Linux/Mac
```bash
# Using Gunicorn (Linux/Mac only)
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
```

#### Windows
```bash
# Using Waitress (Windows compatible)
python serve.py

# Or use batch file (from project root)
scripts\run-prod.bat

# Or use PowerShell script (from project root)
.\scripts\deploy-windows.ps1 -Action start
```

#### Docker (All platforms)
```bash
docker build -t mask-detector .
docker run -p 8000:8000 mask-detector
```

#### Windows Service
```bash
# Install as Windows service
.\scripts\deploy-windows.ps1 -Action service

# Start/stop service
net start MaskDetectionService
net stop MaskDetectionService
```

### Environment Variables
- `FLASK_CONFIG`: Configuration environment
- `SECRET_KEY`: Flask secret key (required for production)
- `PORT`: Server port (default: 5000)
- `HOST`: Server host (default: 127.0.0.1)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Original dataset: [Face Mask Dataset](https://www.kaggle.com/omkargurav/face-mask-dataset)
- MobileNetV2 architecture for efficient mobile deployment
- OpenCV community for computer vision tools

## 📞 Support

For questions or issues, please open an issue on GitHub or contact the maintainers.

---

**Stay Safe! Wear a Mask! 😷**

