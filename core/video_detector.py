import time
import numpy as np
import cv2
import imutils
from imutils.video import VideoStream
from tensorflow import keras
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.layers import DepthwiseConv2D as KDepthwiseConv2D

from core.utils import preprocess_face_frame, decode_prediction, write_bb, load_cascade_detector
from core.performance import monitor_performance
from core.logger import get_logger

logger = get_logger(__name__)

# Custom DepthwiseConv2D that ignores unsupported 'groups' argument in older models
class CompatibleDepthwiseConv2D(KDepthwiseConv2D):
    @classmethod
    def from_config(cls, config):
        config.pop("groups", None)
        return super().from_config(config)


# Try to load the model, fallback to None if it fails
try:
    from config import Config
    model_path = Config.MODEL_PATH

    # Handle TensorFlow version compatibility
    import tensorflow as tf
    print(f"🔧 TensorFlow version: {tf.__version__}")

    # Load model with compatibility settings
    model = keras.models.load_model(
        str(model_path),
        compile=False,
        custom_objects={"DepthwiseConv2D": CompatibleDepthwiseConv2D},
    )
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"⚠️ Could not load model: {e}")
    print("🔄 Falling back to face detection only")
    model = None

face_detector = load_cascade_detector()


def video_mask_detector():
    video = VideoStream(src=0).start()
    time.sleep(1.0)
    while True:
        # Capture frame-by-frame
        frame = video.read()

        frame = detect_mask_in_frame(frame)
        # Display the resulting frame
        # show the output frame
        cv2.imshow("Mask detector", frame)

        key = cv2.waitKey(1) & 0xFF
        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break
    # cleanup
    cv2.destroyAllWindows()
    video.stop()


@monitor_performance("video_frame_processing")
def detect_mask_in_frame(frame):
    frame = imutils.resize(frame, width=500)

    # convert an image from one color space to another
    # (to grayscale)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_detector.detectMultiScale(gray,
                                           scaleFactor=1.1,
                                           minNeighbors=5,
                                           minSize=(40, 40),
                                           flags=cv2.CASCADE_SCALE_IMAGE,
                                           )

    faces_dict = {"faces_list": [],
                  "faces_rect": []
                  }

    for rect in faces:
        (x, y, w, h) = rect
        face_frame = frame[y:y + h, x:x + w]
        # preprocess image
        face_frame_prepared = preprocess_face_frame(face_frame)

        faces_dict["faces_list"].append(face_frame_prepared)
        faces_dict["faces_rect"].append(rect)

    if faces_dict["faces_list"] and model is not None:
        faces_preprocessed = preprocess_input(np.array(faces_dict["faces_list"]))
        preds = model.predict(faces_preprocessed)

        for i, pred in enumerate(preds):
            mask_or_not, confidence = decode_prediction(pred)
            write_bb(mask_or_not, confidence, faces_dict["faces_rect"][i], frame)
    elif faces_dict["faces_list"]:
        # Fallback: just draw face detection without mask classification
        for rect in faces_dict["faces_rect"]:
            (x, y, w, h) = rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(frame, 'Face Detected', (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 0), 2)

    return frame


if __name__ == '__main__':
    video_mask_detector()
