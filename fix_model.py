#!/usr/bin/env python3
"""
Script to fix the mask detection model for TensorFlow 2.20.0 compatibility.
This script loads the old model and saves it in a new format without the problematic TrueDivide layer.
"""
import os
os.environ['TF_USE_LEGACY_KERAS'] = '1'  # Try to use legacy Keras

import numpy as np
from tensorflow import keras
import tensorflow as tf

print(f"🔧 TensorFlow version: {tf.__version__}")
print(f"🔧 Keras version: {keras.__version__}")

# Try different loading approaches
model_path = "models/mask_mobilenet_v2_compat.h5"
backup_path = "models/mask_mobilenet_v2_compat_backup.h5"

print("\n📥 Attempting to load the model...")

# First, backup the original model
import shutil
if not os.path.exists(backup_path):
    shutil.copy(model_path, backup_path)
    print(f"✅ Backed up original model to: {backup_path}")

try:
    # Try loading with tf.compat.v1
    print("\n🔄 Attempting tf.compat.v1 approach...")
    import tensorflow.compat.v1 as tf1
    tf1.disable_v2_behavior()
    
    # Load using keras.saving
    from tensorflow.keras import saving
    model = saving.load_model(model_path, compile=False)
    print("✅ Model loaded successfully with tf.compat.v1!")
    
    # Save in new format
    new_model_path = "models/mask_mobilenet_v2_fixed.h5"
    model.save(new_model_path)
    print(f"✅ Saved fixed model to: {new_model_path}")
    
except Exception as e1:
    print(f"❌ tf.compat.v1 approach failed: {e1}")
    
    try:
        print("\n🔄 Attempting alternative loading with options...")
        # Try with options
        model = keras.models.load_model(
            model_path,
            compile=False,
            options=tf.saved_model.LoadOptions(experimental_io_device='/job:localhost')
        )
        print("✅ Model loaded successfully!")
        
        # Save in new format  
        new_model_path = "models/mask_mobilenet_v2_fixed.h5"
        model.save(new_model_path, save_format='h5')
        print(f"✅ Saved fixed model to: {new_model_path}")
        
    except Exception as e2:
        print(f"❌ Alternative approach failed: {e2}")
        
        print("\n🔄 Final attempt: Using legacy Keras...")
        try:
            import tf_keras as keras_legacy
            model = keras_legacy.models.load_model(model_path, compile=False)
            print("✅ Model loaded with legacy Keras!")
            
            new_model_path = "models/mask_mobilenet_v2_fixed.h5"
            model.save(new_model_path)
            print(f"✅ Saved fixed model to: {new_model_path}")
            
        except Exception as e3:
            print(f"❌ Legacy Keras failed: {e3}")
            print("\n⚠️ All loading approaches failed.")
            print("💡 The model needs to be retrained or converted using an older TensorFlow version.")
