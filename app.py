"""
Simplified Flask app for Vercel deployment
"""
import os
from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
from PIL import Image
import base64
from io import BytesIO

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'vercel-deployment-key')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

@app.route('/')
def home():
    """Home page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mask Detection System</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-header bg-primary text-white">
                            <h1 class="card-title mb-0">🎭 Mask Detection System</h1>
                        </div>
                        <div class="card-body">
                            <p class="lead">AI-powered face mask detection system deployed on Vercel.</p>
                            
                            <div class="alert alert-info">
                                <strong>Note:</strong> This is a simplified version for Vercel deployment. 
                                Camera features are not available in serverless environments.
                            </div>
                            
                            <h3>Upload Image for Detection</h3>
                            <form id="uploadForm" enctype="multipart/form-data">
                                <div class="mb-3">
                                    <input type="file" class="form-control" id="imageFile" accept="image/*" required>
                                </div>
                                <button type="submit" class="btn btn-primary">Detect Faces</button>
                            </form>
                            
                            <div id="result" class="mt-4" style="display: none;">
                                <h4>Detection Result:</h4>
                                <img id="resultImage" class="img-fluid" alt="Detection Result">
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            document.getElementById('uploadForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const fileInput = document.getElementById('imageFile');
                const file = fileInput.files[0];
                
                if (!file) {
                    alert('Please select an image file');
                    return;
                }
                
                const formData = new FormData();
                formData.append('image', file);
                
                try {
                    const response = await fetch('/api/detect', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        document.getElementById('resultImage').src = result.image;
                        document.getElementById('result').style.display = 'block';
                    } else {
                        alert('Error: ' + result.error);
                    }
                } catch (error) {
                    alert('Error processing image: ' + error.message);
                }
            });
        </script>
    </body>
    </html>
    """

@app.route('/api/detect', methods=['POST'])
def detect_faces():
    """Simple face detection API endpoint"""
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image provided'})
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No image selected'})
        
        # Read image
        image = Image.open(file.stream)
        image_array = np.array(image)
        
        # Convert to BGR for OpenCV
        if len(image_array.shape) == 3:
            image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        else:
            image_bgr = image_array
        
        # Simple face detection using OpenCV
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        # Draw rectangles around faces
        for (x, y, w, h) in faces:
            cv2.rectangle(image_bgr, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(image_bgr, 'Face Detected', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
        
        # Convert back to RGB
        result_image = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        result_pil = Image.fromarray(result_image)
        
        # Convert to base64 for web display
        buffer = BytesIO()
        result_pil.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        img_data = f"data:image/png;base64,{img_str}"
        
        return jsonify({
            'success': True,
            'image': img_data,
            'faces_detected': len(faces)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'mask-detection-system',
        'version': '1.0.0',
        'deployment': 'vercel'
    })

if __name__ == '__main__':
    app.run(debug=True)