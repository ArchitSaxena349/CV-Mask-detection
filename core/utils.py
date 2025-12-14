import os
import cv2
from tensorflow.keras.utils import img_to_array
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input as mv2_preprocess_input

# Optional: control class order if the trained model outputs ['without_mask', 'with_mask']
MASK_CLASS_ORDER = os.environ.get('MASK_CLASS_ORDER', 'mask_first').lower()

# Configurable confidence thresholds (defaults tuned for moderate models)
MASK_CONF_THRESHOLD = float(os.environ.get('MASK_CONF_THRESHOLD', '0.80'))
NO_MASK_CONF_THRESHOLD = float(os.environ.get('NO_MASK_CONF_THRESHOLD', '0.80'))
IMPROPER_CONF_THRESHOLD = float(os.environ.get('IMPROPER_CONF_THRESHOLD', '0.65'))
# Minimum gap between top two probabilities to consider decision confident
CONF_DELTA_THRESHOLD = float(os.environ.get('CONF_DELTA_THRESHOLD', '0.20'))

# Selection mode: if set to '1', always use argmax to choose label
FORCE_ARGMAX = os.environ.get('FORCE_ARGMAX', '0').strip() == '1'
# Optional debug for prediction vectors
DEBUG_PRED = os.environ.get('DEBUG_PRED', '0').strip() == '1'

# Preprocessing mode: 'none' or 'mobilenet_v2'
PREPROCESS_MODE = os.environ.get('PREPROCESS_MODE', 'mobilenet_v2').strip().lower()


def preprocess_face_frame(face_frame):
    # convert to RGB
    face_frame = cv2.cvtColor(face_frame, cv2.COLOR_BGR2RGB)
    # preprocess input image for mobilenet
    face_frame_resized = cv2.resize(face_frame, (224, 224))
    face_frame_array = img_to_array(face_frame_resized)
    # Optional normalization to match MobileNetV2 training
    if PREPROCESS_MODE in ('mobilenet_v2', 'mv2'):
        face_frame_array = mv2_preprocess_input(face_frame_array)
    return face_frame_array


def decode_prediction(pred):
    """Decode model prediction into human-readable label.

    Supports 2-class (mask/no_mask) and 3-class (mask/no_mask/improper) outputs.
    Uses thresholds and an ambiguity delta to flag potential improper/partial mask wear.
    """
    # Normalize to Python list for safety
    probs = list(pred)

    if DEBUG_PRED:
        try:
            print(f"🔎 Raw probs: {probs}")
        except Exception:
            pass

    if FORCE_ARGMAX:
        # Simple argmax selection (handles any class count)
        top_idx = int(max(range(len(probs)), key=lambda i: probs[i]))
        labels_map_2 = ['Mask', 'No mask'] if MASK_CLASS_ORDER != 'no_mask_first' else ['No mask', 'Mask']
        labels_map_3 = ['Mask', 'No mask', 'Improper'] if MASK_CLASS_ORDER != 'no_mask_first' else ['No mask', 'Mask', 'Improper']
        if len(probs) == 2:
            lbl = labels_map_2[top_idx]
        elif len(probs) == 3:
            lbl = labels_map_3[top_idx]
        else:
            lbl = f"Class{top_idx}"
        return lbl, f"{(probs[top_idx] * 100):.2f}"

    # Helper to compute top-two gap
    def top_gap(values):
        if len(values) < 2:
            return 1.0
        sorted_vals = sorted(values, reverse=True)
        return sorted_vals[0] - sorted_vals[1]

    if len(probs) == 2:
        # Handle possible class order differences (2-class)
        if MASK_CLASS_ORDER == 'no_mask_first':
            no_mask_prob, mask_prob = probs
        else:
            mask_prob, no_mask_prob = probs

        # Ambiguity rule: if top two are close, mark as Improper
        gap = abs(mask_prob - no_mask_prob)
        if gap < CONF_DELTA_THRESHOLD:
            label = "Improper"
            confidence = f"{(max(mask_prob, no_mask_prob) * 100):.2f}"
            return label, confidence

        if mask_prob >= MASK_CONF_THRESHOLD and mask_prob > no_mask_prob:
            label = "Mask"
            confidence = f"{(mask_prob * 100):.2f}"
        elif no_mask_prob >= NO_MASK_CONF_THRESHOLD and no_mask_prob > mask_prob:
            label = "No mask"
            confidence = f"{(no_mask_prob * 100):.2f}"
        else:
            label = "Improper"
            confidence = f"{(max(mask_prob, no_mask_prob) * 100):.2f}"
        return label, confidence

    elif len(probs) == 3:
        # Assume default order [mask, no_mask, improper]; allow swapping first two via MASK_CLASS_ORDER
        mask_prob, no_mask_prob, improper_prob = probs
        if MASK_CLASS_ORDER == 'no_mask_first':
            no_mask_prob, mask_prob, improper_prob = no_mask_prob, mask_prob, improper_prob

        # Ambiguity rule across all three classes
        gap = top_gap([mask_prob, no_mask_prob, improper_prob])
        if gap < CONF_DELTA_THRESHOLD:
            top_val = max(mask_prob, no_mask_prob, improper_prob)
            return "Improper", f"{(top_val * 100):.2f}"

        # Prioritize explicit improper classification if high
        if improper_prob >= IMPROPER_CONF_THRESHOLD and improper_prob >= max(mask_prob, no_mask_prob):
            return "Improper", f"{(improper_prob * 100):.2f}"
        if mask_prob >= MASK_CONF_THRESHOLD and mask_prob > no_mask_prob:
            return "Mask", f"{(mask_prob * 100):.2f}"
        if no_mask_prob >= NO_MASK_CONF_THRESHOLD and no_mask_prob > mask_prob:
            return "No mask", f"{(no_mask_prob * 100):.2f}"
        # Ambiguous
        top = max(mask_prob, no_mask_prob, improper_prob)
        if top == improper_prob:
            return "Improper", f"{(improper_prob * 100):.2f}"
        elif top == mask_prob:
            return "Mask", f"{(mask_prob * 100):.2f}"
        else:
            return "No mask", f"{(no_mask_prob * 100):.2f}"

    else:
        # Fallback: unknown class count
        top_idx = int(max(range(len(probs)), key=lambda i: probs[i]))
        labels = ["Class0", "Class1", "Class2", "Class3"]
        lbl = labels[top_idx] if top_idx < len(labels) else f"Class{top_idx}"
        return lbl, f"{(probs[top_idx] * 100):.2f}"


def write_bb(mask_or_not, confidence, box, frame):
    (x, y, w, h) = box
    if mask_or_not == "Mask":
        color = (0, 255, 0)  # green
    elif mask_or_not == "No mask":
        color = (0, 0, 255)  # red
    else:
        color = (255, 165, 0)  # orange for improper/partial

    label = f"{mask_or_not}: {confidence}%"

    cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)


def load_cascade_detector():
    cascade_path = os.path.dirname(cv2.__file__) + "/data/haarcascade_frontalface_alt2.xml"
    face_detector = cv2.CascadeClassifier(cascade_path)
    return face_detector
