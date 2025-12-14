"""
Model loader utilities for compatibility with newer TensorFlow/Keras versions.
Builds a MobileNetV2-based architecture and loads weights by name to avoid
legacy deserialization issues in old .h5 model files.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

import os
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.layers import DepthwiseConv2D as KDepthwiseConv2D, Layer


def build_compat_model(input_shape=(224, 224, 3), classes: int = 2) -> keras.Model:
    inputs = keras.Input(shape=input_shape, name="input_layer_1")
    x = layers.Rescaling(1.0 / 127.5, offset=-1.0, name="preprocessing")(inputs)

    base = keras.applications.MobileNetV2(
        include_top=False,
        weights="imagenet",
        input_shape=input_shape,
        pooling=None,
        alpha=1.0,
    )
    base.trainable = False
    x = base(x)

    x = layers.GlobalAveragePooling2D(name="global_average_pooling2d")(x)
    x = layers.Dropout(0.2, name="dropout")(x)
    x = layers.Dense(128, activation="relu", name="dense")(x)
    outputs = layers.Dense(classes, activation="softmax", name="dense_1")(x)

    model = keras.Model(inputs=inputs, outputs=outputs, name="mask_mobilenet_v2_compat")
    return model


def resolve_model_path(configured_path: Path | str,
                       candidates: Optional[Iterable[str]] = None) -> Optional[Path]:
    env_path = os.environ.get("MASK_MODEL_PATH")
    if env_path:
        p = Path(env_path).expanduser().resolve()
        if p.exists():
            print(f"🔎 Using MASK_MODEL_PATH from environment: {p}")
            return p
        else:
            print(f"⚠️ MASK_MODEL_PATH not found: {p}")

    cfg = Path(configured_path).expanduser().resolve()
    if cfg.exists():
        print(f"🔎 Using configured model path: {cfg}")
        return cfg
    else:
        print(f"⚠️ Configured model path not found: {cfg}")

    root = Path(__file__).resolve().parents[1]
    models_dir = root / "models"
    common_names = [
        "mask_mobilenet_v2_compat.h5",
        "mask_mobilenet.h5",
        "mask_detector.h5",
        "mask_model.h5",
    ]
    if candidates:
        common_names = list(candidates) + common_names

    for name in common_names:
        candidate = (models_dir / name).resolve()
        if candidate.exists():
            print(f"🔎 Found model at: {candidate}")
            return candidate

    print("❌ No mask model file found in models/ directory.")
    return None


# Custom objects to support older serialized models
# Function variant that accepts extra kwargs (e.g., name)
def TrueDivide(x, denom=127.5, **kwargs):
    return (x / denom) - 1.0

class CompatibleDepthwiseConv2D(KDepthwiseConv2D):
    @classmethod
    def from_config(cls, config):
        config.pop("groups", None)
        return super().from_config(config)


def _infer_classes_from_h5(model_path: Path) -> Optional[int]:
    try:
        import h5py
        with h5py.File(str(model_path), 'r') as f:
            mw = f.get('model_weights')
            if mw is None:
                return None
            for key in mw.keys():
                if key.startswith('dense_1') or key == 'dense_1':
                    grp = mw.get(key)
                    if grp is None:
                        continue
                    for wname in grp.keys():
                        if 'kernel' in wname:
                            ds = grp.get(wname)
                            if ds is None:
                                continue
                            shape = ds.shape
                            if len(shape) == 2:
                                classes = int(shape[1])
                                print(f"🔎 Inferred classes from weights: {classes}")
                                return classes
            for key in mw.keys():
                if 'dense' in key:
                    grp = mw.get(key)
                    if grp is None:
                        continue
                    for wname in grp.keys():
                        if 'kernel' in wname:
                            ds = grp.get(wname)
                            if ds is None:
                                continue
                            shape = ds.shape
                            if len(shape) == 2:
                                classes = int(shape[1])
                                print(f"🔎 Inferred classes from weights (fallback): {classes}")
                                return classes
    except Exception as e:
        print(f"⚠️ Could not infer class count from H5: {e}")
    return None


def load_mask_model(model_path: Path | str) -> keras.Model | None:
    model_path = Path(model_path)

    # 1) Prefer legacy tf.keras load with custom objects
    try:
        print("🔄 Attempting legacy model load with tf.keras (custom_objects)...")
        legacy = keras.models.load_model(
            str(model_path), compile=False,
            custom_objects={
                'TrueDivide': TrueDivide,
                'CompatibleDepthwiseConv2D': CompatibleDepthwiseConv2D,
                'DepthwiseConv2D': CompatibleDepthwiseConv2D,
            }
        )
        print("✅ Legacy model loaded successfully.")
        return legacy
    except Exception as e1:
        print(f"❌ Legacy tf.keras load failed: {e1}")

    # 2) Attempt tf_keras if available
    try:
        print("🔄 Attempting legacy load via tf_keras (if installed)...")
        import tf_keras as keras_legacy  # type: ignore
        legacy2 = keras_legacy.models.load_model(str(model_path), compile=False)
        print("✅ Legacy tf_keras model loaded successfully.")
        return legacy2
    except Exception as e2:
        print(f"❌ tf_keras load failed: {e2}")

    # 3) Fallback: build compatible architecture and load weights by name
    inferred_classes = _infer_classes_from_h5(model_path) or 2
    if inferred_classes != 2:
        print(f"ℹ️ Building compatible model with {inferred_classes} output classes")
    model = build_compat_model(classes=inferred_classes)
    try:
        model.load_weights(str(model_path), by_name=True, skip_mismatch=True)
        print("✅ Weights loaded into compatible architecture.")
        return model
    except Exception as e3:
        print(f"⚠️ Could not load weights into compat architecture: {e3}")
        print("💡 Consider retraining or converting the model to a compatible format.")
        return None
