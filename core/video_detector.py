import os

import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import DepthwiseConv2D as KDepthwiseConv2D, Layer

from core.utils import preprocess_face_frame, load_cascade_detector, decode_prediction, write_bb
from core.model_loader import load_mask_model, resolve_model_path
from config import Config


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


print(f"🔧 TensorFlow version: {tf.__version__}")

model_path = resolve_model_path(Config.MODEL_PATH)
print(f"📥 Resolved model path: {model_path}")

if model_path is None:
    raise RuntimeError("Mask model file not found")

model = load_mask_model(model_path)

face_cascade = load_cascade_detector()

# Configurable crop margin (fraction of width/height)
FACE_CROP_MARGIN = float(os.environ.get('FACE_CROP_MARGIN', '0.15'))


def detect_mask_in_frame(frame):
    frame = cv2.resize(frame, (600, int(frame.shape[0] * (600 / frame.shape[1]))))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=4,
                                          minSize=(40, 40), flags=cv2.CASCADE_SCALE_IMAGE)

    faces_dict = {"faces_list": [],
                  "faces_rect": []
                  }

    h_img, w_img = frame.shape[:2]

    for rect in faces:
        (x, y, w, h) = rect
        # expand crop by margin
        mx = int(FACE_CROP_MARGIN * w)
        my = int(FACE_CROP_MARGIN * h)
        x0 = max(0, x - mx)
        y0 = max(0, y - my)
        x1 = min(w_img, x + w + mx)
        y1 = min(h_img, y + h + my)

        face_frame = frame[y0:y1, x0:x1]
        face_frame = preprocess_face_frame(face_frame)
        faces_dict["faces_list"].append(face_frame)
        faces_dict["faces_rect"].append((x0, y0, x1 - x0, y1 - y0))

    if len(faces_dict["faces_list"]) > 0:
        faces_array = np.array(faces_dict["faces_list"])
        predictions = model.predict(faces_array, verbose=0)
        for i, pred in enumerate(predictions):
            mask_or_not, confidence = decode_prediction(pred)
            rect = faces_dict["faces_rect"][i]
            write_bb(mask_or_not, confidence, rect, frame)

    return frame
