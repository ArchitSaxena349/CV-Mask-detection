import os
from pathlib import Path
import sys
import cv2
import numpy as np

# Ensure project root is on path for absolute imports
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from config import Config
from core.model_loader import load_mask_model
from core.utils import load_cascade_detector, preprocess_face_frame, decode_prediction, write_bb


def run_image_smoke_test(image_path: Path, model, face_detector) -> Path:
    """Run detection on a single image, save annotated output, and print predictions."""
    image = cv2.imread(str(image_path))
    if image is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")

    image = cv2.resize(image, (600, int(image.shape[0] * (600 / image.shape[1]))))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.05,
        minNeighbors=4,
        minSize=(40, 40),
        flags=cv2.CASCADE_SCALE_IMAGE,
    )

    clone_image = image.copy()
    face_arrays = []
    face_rects = []

    for (x, y, w, h) in faces:
        face_frame = clone_image[y:y + h, x:x + w]
        face_arrays.append(preprocess_face_frame(face_frame))
        face_rects.append((x, y, w, h))

    if face_arrays and model is not None:
        faces_array = np.array(face_arrays)
        preds = model.predict(faces_array, verbose=0)
        print(f"Found {len(preds)} face(s) in {image_path.name}")
        for i, pred in enumerate(preds):
            label, conf = decode_prediction(pred)
            print(f"  - Face {i+1}: {label} ({conf}%)")
            write_bb(label, conf, face_rects[i], clone_image)
    else:
        print(f"No faces detected in {image_path.name} or model not loaded.")

    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    out_path = logs_dir / f"smoke_{image_path.stem}.png"
    cv2.imwrite(str(out_path), clone_image)
    print(f"Saved annotated output to: {out_path}")
    return out_path


if __name__ == "__main__":
    # Resolve model and load
    print(f"Model path from config: {Config.MODEL_PATH}")
    model = load_mask_model(Config.MODEL_PATH)
    if model is None:
        raise SystemExit("Model failed to load. Check paths and formats.")

    # Prepare face detector
    face_detector = load_cascade_detector()

    # Sample images
    samples = [
        Path("app/static/images/mask.jpg"),
        Path("app/static/images/stay-safe.jpg"),
    ]

    for img in samples:
        run_image_smoke_test(img, model, face_detector)