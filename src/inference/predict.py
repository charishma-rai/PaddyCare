
"""Run real PaddyCare disease inference with the trained MobileNetV2 model.

Place mobilenetv2_final.keras in the project's models/ directory.
The model includes its MobileNetV2 preprocessing layer.
Inference inputs must therefore be RGB pixels in the [0, 255] range.
"""

from functools import lru_cache
import logging
import os
from pathlib import Path

import numpy as np
from PIL import Image

from src.explain.gradcam import generate_gradcam_overlay
from src.inference.quality import check_quality

logger = logging.getLogger(__name__)


# Keep this order exactly aligned with the model's training class_to_index.
MODEL_CLASS_NAMES = [
    "bacterial_leaf_blight",
    "blast",
    "brown_spot",
    "normal",
]

DISPLAY_NAMES = {
    "bacterial_leaf_blight": "Bacterial leaf blight",
    "blast": "Blast",
    "brown_spot": "Brown spot",
    "normal": "Healthy",
}

CLASS_NAMES = [DISPLAY_NAMES[name] for name in MODEL_CLASS_NAMES]

IMAGE_SIZE = (224, 224)
CONFIDENCE_THRESHOLD = 0.70
IS_DEMO = False

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models" / "mobilenetv2_final.keras"


def _model_path() -> Path:
    """Allow an alternate model location without changing application code."""
    configured = os.environ.get("PADDYCARE_MODEL_PATH")
    return Path(configured).expanduser() if configured else DEFAULT_MODEL_PATH


@lru_cache(maxsize=1)
def _load_model(model_path: str):
    """Load the trained Keras model once per app process."""

    path = Path(model_path)

    if not path.is_file():
        raise FileNotFoundError(
            "Trained MobileNetV2 model not found. Place "
            "'mobilenetv2_final.keras' in the project's models/ folder. "
            "You can also set the PADDYCARE_MODEL_PATH environment variable."
        )

    try:
        import tensorflow as tf
        from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

    except ImportError as exc:
        raise RuntimeError(
            "TensorFlow is required for real predictions. Install the project "
            "dependencies with: pip install -r requirements.txt"
        ) from exc

    # Register MobileNetV2 preprocessing so Keras can load the saved model.
    return tf.keras.models.load_model(
        path,
        custom_objects={"preprocess_input": preprocess_input},
        compile=False
    )


def predict(image: Image.Image) -> dict:
    """Return a real four-class prediction in the format used by the UI."""

    quality = check_quality(image)

    model = _load_model(str(_model_path().resolve()))

    # Prepare RGB image. Preprocessing is already included inside the model.
    rgb = image.convert("RGB").resize(
        IMAGE_SIZE,
        Image.Resampling.BILINEAR
    )

    batch = np.asarray(rgb, dtype=np.float32)[np.newaxis, ...]

    probabilities = np.asarray(
        model.predict(batch, verbose=0)
    )[0]

    if probabilities.shape != (len(MODEL_CLASS_NAMES),):
        raise RuntimeError(
            "The loaded model must return exactly four probabilities in this order: "
            + ", ".join(MODEL_CLASS_NAMES)
        )

    if not np.isfinite(probabilities).all():
        raise RuntimeError("The model returned invalid prediction values.")

    # Guard against tiny numerical deviations from a probability distribution.
    probabilities = np.clip(probabilities, 0.0, None)

    total = float(probabilities.sum())

    if total <= 0:
        raise RuntimeError(
            "The model returned an empty probability distribution."
        )

    probabilities = probabilities / total

    top = int(np.argmax(probabilities))
    confidence = float(probabilities[top])

    display_probs = {
        DISPLAY_NAMES[class_name]: float(probability)
        for class_name, probability in zip(
            MODEL_CLASS_NAMES,
            probabilities
        )
    }

    # Grad-CAM for the predicted class, computed from the same `batch` that was
    # just passed to model.predict (preprocessing stays inside the model).
    # A Grad-CAM failure must never break or alter the prediction itself, and
    # must never produce a misleading image: on any error the heatmap is None
    # and the reason is returned in "heatmap_error".
    heatmap = None
    heatmap_error = None
    try:
        heatmap = generate_gradcam_overlay(
            model,
            batch,
            image.convert("RGB"),
            top,
            reference_probs=probabilities,
        )
    except Exception as exc:  # noqa: BLE001 - explanation is optional
        logger.warning("Grad-CAM unavailable: %s", exc, exc_info=True)
        heatmap_error = str(exc) or exc.__class__.__name__

    return {
        "label": DISPLAY_NAMES[MODEL_CLASS_NAMES[top]],
        "confidence": confidence,
        "probs": display_probs,
        "heatmap": heatmap,
        "heatmap_error": heatmap_error,
        "uncertain": (
            confidence < CONFIDENCE_THRESHOLD or not quality["ok"]
        ),
        "quality": quality,
        "demo": False,
    }
