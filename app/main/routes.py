from base64 import b64encode
from io import BytesIO
import cv2
import numpy as np
from PIL import Image
from flask import render_template, Response, flash, request, current_app
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from werkzeug.exceptions import abort
from wtforms import FileField, SubmitField
from app.main import main_bp


from core.video_detector import detect_mask_in_frame
from core.image_processor import detect_mask_in_image
from core.logger import get_logger

logger = get_logger(__name__)


@main_bp.route("/")
def home_page():
    return render_template("home_page.html")


def gen(source, camera_index, video_path):
    # Decide capture source
    if source == "video" and video_path:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"Failed to open video file: {video_path}")
            # Yield a single error frame for user feedback
            error_frame = np.zeros((360, 640, 3), dtype=np.uint8)
            cv2.putText(error_frame, "Error: cannot open video", (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
            ret, jpeg = cv2.imencode('.jpg', error_frame)
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
            return
    else:
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            logger.error(f"Failed to open camera index: {camera_index}")
            # Yield a single error frame for user feedback
            error_frame = np.zeros((360, 640, 3), dtype=np.uint8)
            cv2.putText(error_frame, "Error: cannot access camera", (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
            ret, jpeg = cv2.imencode('.jpg', error_frame)
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
            return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.warning("Frame read failed or end of stream reached")
                break

            # Process frame
            frame = detect_mask_in_frame(frame)

            # Convert to JPEG
            ret, jpeg = cv2.imencode('.jpg', frame)
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
    except Exception as e:
        logger.exception(f"Video feed error: {e}")
    finally:
        cap.release()


@main_bp.route('/video_feed')
def video_feed():
    # Extract query params within request context
    source = request.args.get("source", "camera")
    camera_index = int(request.args.get("camera_index", 0))
    video_path = request.args.get("path")
    return Response(gen(source, camera_index, video_path),
        mimetype='multipart/x-mixed-replace; boundary=frame')



@main_bp.route("/image-mask-detector", methods=["GET", "POST"])
def image_mask_detection():
    return render_template("image_detector.html",
                           form=PhotoMaskForm())


@main_bp.route("/image-processing", methods=["POST"])
def image_processing():
    form = PhotoMaskForm()

    if not form.validate_on_submit():
        flash("Invalid submission", "danger")
        abort(Response("Error", 400))

    try:
        from core.validators import validate_image_file
        validate_image_file(form.image.data)

        pil_image = Image.open(form.image.data)
        image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        array_image = detect_mask_in_image(image)
        rgb_image = cv2.cvtColor(array_image, cv2.COLOR_BGR2RGB)
        image_detected = Image.fromarray(rgb_image, 'RGB')

        with BytesIO() as img_io:
            image_detected.save(img_io, 'PNG')
            img_io.seek(0)
            base64img = "data:image/png;base64," + b64encode(img_io.getvalue()).decode('ascii')
            return base64img
    except Exception as e:
        logger.exception(f"Image processing failed: {e}")
        flash("Image processing failed. Please check the file and try again.", "danger")
        abort(Response("Image processing failed", 400))


# form
class PhotoMaskForm(FlaskForm):
    image = FileField('Choose image:',
                      validators=[
                          FileAllowed(['jpg', 'jpeg', 'png'], 'The allowed extensions are: .jpg, .jpeg and .png')])

    submit = SubmitField('Detect mask')
