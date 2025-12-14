import os

import imutils
from tensorflow import keras
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import DepthwiseConv2D as KDepthwiseConv2D, Layer

from core.utils import load_cascade_detector, preprocess_face_frame, decode_prediction, write_bb

POSSIBLE_EXT = [".png", ".jpg", ".jpeg"]


class TrueDivide(Layer):
    """Compatibility layer for models containing a serialized 'TrueDivide' op.

    Applies MobileNetV2 normalization: scales to [-1, 1] range.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def call(self, inputs):
        # MobileNetV2 preprocessing: (x / 127.5) - 1
        return (inputs / 127.5) - 1.0
    
    def get_config(self):
        return super().get_config()


class CompatibleDepthwiseConv2D(KDepthwiseConv2D):
    """DepthwiseConv2D that ignores unsupported 'groups' in older saved models."""

    @classmethod
    def from_config(cls, config):
        config.pop("groups", None)
        return super().from_config(config)


# Try to load the model, fallback to None if it fails
try:
    from config import Config
    from core.model_loader import load_mask_model, resolve_model_path
    
    # Resolve model path robustly (honors MASK_MODEL_PATH env override)
    model_path = resolve_model_path(Config.MODEL_PATH)
    print(f"🔧 TensorFlow version: {tf.__version__}")
    print(f"📥 Resolved model path: {model_path}")
    
    if model_path is None:
        raise RuntimeError("Mask model file not found")
    
    # Use new weight-loading approach to avoid deserialization issues
    model = load_mask_model(model_path)
    
    if model is None:
        raise RuntimeError("Model loading returned None")
        
except Exception as e:
    print(f"⚠️ Could not load model: {e}")
    print("🔄 Falling back to face detection only")
    model = None

face_detector_model = load_cascade_detector()

# Configurable crop margin (fraction of width/height)
FACE_CROP_MARGIN = float(os.environ.get('FACE_CROP_MARGIN', '0.15'))


def detect_mask_in_image(image):
    image = imutils.resize(image, width=600)

    # convert an image from one color space to another
    # (to grayscale)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_detector_model.detectMultiScale(gray,
                                                 scaleFactor=1.05,
                                                 minNeighbors=4,
                                                 minSize=(40, 40),
                                                 flags=cv2.CASCADE_SCALE_IMAGE,
                                                 )
    clone_image = image.copy()

    faces_dict = {"faces_list": [],
                  "faces_rect": []
                  }

    h_img, w_img = image.shape[:2]

    for rect in faces:
        (x, y, w, h) = rect
        # expand crop by margin
        mx = int(FACE_CROP_MARGIN * w)
        my = int(FACE_CROP_MARGIN * h)
        x0 = max(0, x - mx)
        y0 = max(0, y - my)
        x1 = min(w_img, x + w + mx)
        y1 = min(h_img, y + h + my)

        face_frame = clone_image[y0:y1, x0:x1]
        # preprocess image
        face_frame_array = preprocess_face_frame(face_frame)

        faces_dict["faces_list"].append(face_frame_array)
        faces_dict["faces_rect"].append((x0, y0, x1 - x0, y1 - y0))

    if faces_dict["faces_list"] and model is not None:
        # Model includes preprocessing layer, so pass raw pixel values [0-255]
        faces_array = np.array(faces_dict["faces_list"])
        preds = model.predict(faces_array, verbose=0)
        for i, pred in enumerate(preds):
            mask_or_not, confidence = decode_prediction(pred)
            write_bb(mask_or_not, confidence, faces_dict["faces_rect"][i], clone_image)
    elif faces_dict["faces_list"]:
        # Fallback: just draw face detection without mask classification
        for rect in faces_dict["faces_rect"]:
            (x, y, w, h) = rect
            cv2.rectangle(clone_image, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(clone_image, 'Face Detected', (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 0), 2)

    return clone_image


def test_on_custom_image(path):
    filename, file_extension = os.path.splitext(path)
    if file_extension not in POSSIBLE_EXT:
        raise Exception("possible file extensions are .png, .jpg, .jpeg")
    if not os.path.exists(path):
        raise FileNotFoundError("file not found")
    image = cv2.imread(path)
    image_masked = detect_mask_in_image(image)
    cv2.imwrite(filename + "_mask_detected.png", image_masked)
    return


if __name__ == '__main__':
    path = input("please enter your image filepath:")
    test_on_custom_image(path)
