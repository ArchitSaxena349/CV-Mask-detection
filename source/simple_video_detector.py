import cv2
import numpy as np

def video_mask_detector():
    # Initialize the video stream
    video = cv2.VideoCapture(0)
    
    while True:
        # Read frame
        ret, frame = video.read()
        if not ret:
            break
            
        # Process frame
        frame = detect_mask_in_frame(frame)
        
        # Convert to JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)
        if ret:
            yield jpeg.tobytes()
            
    video.release()

def detect_mask_in_frame(frame):
    # Load the face cascade classifier
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    # Process each detected face
    for (x, y, w, h) in faces:
        # Extract the face region
        face_region = gray[y:y+h, x:x+w]
        
        # Apply adaptive thresholding to detect mask in face region
        mask = cv2.adaptiveThreshold(face_region, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                    cv2.THRESH_BINARY_INV, 11, 2)
        
        # Find contours in the face region
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Process each contour
        for contour in contours:
            area = cv2.contourArea(contour)
            # Filter by area - masks are typically larger than small objects
            if 500 < area < 20000:  # Adjusted for face region
                # Get bounding box relative to face
                cx, cy, cw, ch = cv2.boundingRect(contour)
                
                # Convert to global coordinates
                gx = x + cx
                gy = y + cy
                gw = cw
                gh = ch
                
                # Filter by aspect ratio - masks are typically rectangular
                aspect_ratio = gw / float(gh)
                if 0.5 < aspect_ratio < 2.0:  # Masks are usually between these ratios
                    # Draw rectangle and label
                    cv2.rectangle(frame, (gx, gy), (gx + gw, gy + gh), (0, 255, 0), 2)
                    cv2.putText(frame, 'Mask', (gx, gy - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Draw face detection rectangle
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.putText(frame, 'Face', (x, y - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    
    return frame
