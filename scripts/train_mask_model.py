import argparse
import os
from pathlib import Path

import tensorflow as tf
from tensorflow.keras import layers, models, optimizers
from tensorflow.keras.applications.mobilenet_v2 import (
    MobileNetV2,
    preprocess_input,
)

try:
    import kagglehub  # Optional: used when --use-kagglehub is passed
except ImportError:  # pragma: no cover - optional dependency
    kagglehub = None


AUTOTUNE = tf.data.AUTOTUNE


def build_datasets(data_dir: Path, image_size=(224, 224), batch_size: int = 32):
    """Build train/validation datasets from directory.

    Expects a directory with subfolders per class, e.g.:

        data_dir/
          with_mask/
          without_mask/
    """

    train_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=0.2,
        subset="training",
        seed=42,
        image_size=image_size,
        batch_size=batch_size,
    )

    val_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=0.2,
        subset="validation",
        seed=42,
        image_size=image_size,
        batch_size=batch_size,
    )

    class_names = train_ds.class_names
    print(f"Detected classes: {class_names}")

    # Cache and prefetch for performance
    train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

    return train_ds, val_ds, class_names


def build_model(num_classes: int, input_shape=(224, 224, 3)) -> tf.keras.Model:
    """Build a MobileNetV2-based classifier compatible with TF 2.20."""

    base_model = MobileNetV2(
        input_shape=input_shape,
        include_top=False,
        weights="imagenet",
    )
    base_model.trainable = False

    inputs = layers.Input(shape=input_shape)
    x = preprocess_input(inputs)
    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(128, activation="relu")(x)
    x = layers.Dropout(0.5)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)

    model = models.Model(inputs, outputs, name="mask_mobilenet_v2_compat")
    return model


def train(
    data_dir: Path,
    output_path: Path,
    epochs: int = 10,
    batch_size: int = 32,
):
    image_size = (224, 224)

    train_ds, val_ds, class_names = build_datasets(
        data_dir=data_dir,
        image_size=image_size,
        batch_size=batch_size,
    )

    num_classes = len(class_names)
    print(f"Number of classes: {num_classes}")

    model = build_model(num_classes=num_classes, input_shape=(*image_size, 3))

    model.compile(
        optimizer=optimizers.Adam(learning_rate=1e-4),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=3, restore_best_weights=True
        )
    ]

    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs,
        callbacks=callbacks,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    model.save(output_path, include_optimizer=False)
    print(f"Saved trained model to {output_path}")
    print(f"Classes: {class_names}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Train a MobileNetV2-based mask detection model on the Kaggle face-mask dataset.",
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        required=False,
        help=(
            "Path to the dataset root directory (e.g. the folder containing "
            "'with_mask' and 'without_mask' subfolders). "
            "Ignored if --use-kagglehub is provided."
        ),
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=10,
        help="Number of training epochs (default: 10)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Batch size (default: 32)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="models/mask_mobilenet_v2_compat.h5",
        help=(
            "Output path for the trained model (default: models/mask_mobilenet_v2_compat.h5). "
            "Relative to the project root."
        ),
    )

    parser.add_argument(
        "--use-kagglehub",
        action="store_true",
        help=(
            "Download the Omkar Gurav face-mask dataset via kagglehub and use that as data-dir. "
            "Requires kagglehub to be installed and Kaggle credentials configured."
        ),
    )

    return parser.parse_args()


def main():
    args = parse_args()

    # Determine dataset directory
    if args.use_kagglehub:
        if kagglehub is None:
            raise SystemExit(
                "kagglehub is not installed. Install it with 'pip install kagglehub' "
                "or run without --use-kagglehub and provide --data-dir manually."
            )
        print("Downloading Omkar Gurav face-mask dataset via kagglehub...")
        kaggle_path = kagglehub.dataset_download("omkargurav/face-mask-dataset")
        data_dir = Path(kaggle_path).expanduser().resolve()
        print(f"Downloaded dataset to: {data_dir}")

        # Some Kaggle datasets wrap the actual class folders in a single
        # top-level directory (e.g. `<root>/data/with_mask`, `without_mask`).
        # If we detect exactly one subdirectory, automatically descend into it
        # so that `image_dataset_from_directory` sees the real class folders.
        subdirs = [p for p in data_dir.iterdir() if p.is_dir()]
        if len(subdirs) == 1:
            print(
                "Detected a single subdirectory inside the Kaggle dataset root: "
                f"{subdirs[0]}. Using this as the data directory."
            )
            data_dir = subdirs[0]
    else:
        if not args.data_dir:
            raise SystemExit(
                "--data-dir is required when --use-kagglehub is not provided."
            )
        data_dir = Path(args.data_dir).expanduser().resolve()
        if not data_dir.exists():
            raise SystemExit(f"Dataset directory not found: {data_dir}")

    project_root = Path(__file__).resolve().parents[1]
    output_path = (project_root / args.output).resolve()

    print(f"Using dataset at: {data_dir}")
    print(f"Project root: {project_root}")
    print(f"Model will be saved to: {output_path}")

    train(
        data_dir=data_dir,
        output_path=output_path,
        epochs=args.epochs,
        batch_size=args.batch_size,
    )


if __name__ == "__main__":
    main()
