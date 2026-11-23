"""Grad-CAM for the PaddyCare MobileNetV2 classifier.

Why this file does not use the textbook ``Model(inputs, [conv_output, preds])``
recipe
----------------------------------------------------------------------------
The saved model ``models/mobilenetv2_final.keras`` is a ``Sequential`` stack:

    Lambda(preprocess_input)                  <- preprocessing lives in the model
    Functional "mobilenetv2_1.00_224"         <- nested MobileNetV2 backbone
    GlobalAveragePooling2D
    Dropout(0.3)
    Dense(4, softmax)

The backbone is a *nested* model, so the inner ``out_relu`` tensor is not
reachable from the outer model's input and the usual "build a sub-model that
returns the conv output" trick fails. Instead this module runs the model's own
layers one after another inside a ``tf.GradientTape``:

    batch --Lambda--> backbone --> feature map (7x7x1280) --head--> class logits

* The feature map is the backbone's output, i.e. the ``out_relu`` activation
  that directly follows the last convolution (``Conv_1`` -> ``Conv_1_bn`` ->
  ``out_relu``). It is also exactly what the GlobalAveragePooling2D layer
  consumes, which is what Grad-CAM needs.
* The layer is found by inspecting the loaded model, never by a hard-coded name.
* Preprocessing is applied exactly once, by the model's own Lambda layer. The
  input must be the same raw [0, 255] float32 batch that ``predict()`` feeds to
  ``model.predict``.
* The score being differentiated is the pre-softmax logit of the class, because
  the softmax probability saturates for confident predictions and makes the
  gradients vanish or mix classes together.

Any structural surprise or numerical inconsistency raises ``GradCAMError``
instead of returning a heatmap that could be misleading.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
from PIL import Image


class GradCAMError(RuntimeError):
    """Raised when a trustworthy Grad-CAM heatmap cannot be produced."""


# --------------------------------------------------------------------------- #
# Locating the layers (inspected from the real loaded model)
# --------------------------------------------------------------------------- #

def _is_spatial(layer) -> bool:
    """True if the layer outputs a 4-D (batch, H, W, C) feature map."""
    try:
        shape = layer.output.shape
    except (AttributeError, ValueError):
        return False
    return len(shape) == 4


def _last_conv_name(layer) -> Optional[str]:
    """Name of the last convolution inside a nested backbone (for validation)."""
    inner_layers = getattr(layer, "layers", None)
    if not inner_layers:
        return None
    conv_types = ("Conv2D", "DepthwiseConv2D", "SeparableConv2D")
    for inner in reversed(inner_layers):
        if type(inner).__name__ in conv_types:
            return inner.name
    return None


def _resolve_structure(model) -> dict:
    """Split the model into: layers before the feature map, the layer that
    produces the feature map, and the classifier head after it.

    Only a linear stack (Sequential) is supported, which is what the saved
    PaddyCare model is. Anything else raises GradCAMError.
    """
    layers = list(getattr(model, "layers", []))
    if not layers:
        raise GradCAMError("The loaded model has no layers to explain.")

    # The feature layer is the LAST layer that still outputs a spatial map.
    feature_idx = None
    for idx, layer in enumerate(layers):
        if _is_spatial(layer):
            feature_idx = idx
    if feature_idx is None:
        raise GradCAMError(
            "No convolutional (4-D) feature map was found in the model."
        )

    feature_layer = layers[feature_idx]
    pre_layers = layers[:feature_idx]
    head_layers = layers[feature_idx + 1:]

    if not head_layers:
        raise GradCAMError("The model has no classifier layers after its feature map.")

    # The feature map must be a down-sampled convolutional map, not the
    # (preprocessed) input image itself.
    in_shape = model.input_shape
    fh, fw = int(feature_layer.output.shape[1]), int(feature_layer.output.shape[2])
    if in_shape[1] is not None and (fh >= int(in_shape[1]) or fw >= int(in_shape[2])):
        raise GradCAMError(
            "The detected feature map is not smaller than the input image, so it "
            "is not a convolutional feature map."
        )

    # The head must collapse the spatial map to class scores.
    final = head_layers[-1]
    if type(final).__name__ != "Dense":
        raise GradCAMError(
            f"Expected the model to end with a Dense layer, found {type(final).__name__}."
        )

    n_channels = int(feature_layer.output.shape[-1])
    last_conv = _last_conv_name(feature_layer)
    if last_conv is not None:
        conv_layer = feature_layer.get_layer(last_conv)
        conv_filters = getattr(conv_layer, "filters", None)
        if conv_filters is not None and int(conv_filters) != n_channels:
            raise GradCAMError(
                f"The feature map has {n_channels} channels but the last "
                f"convolution '{last_conv}' has {conv_filters} filters, so the "
                "feature map is not the output of the final convolutional block."
            )

    return {
        "pre_layers": pre_layers,
        "feature_layer": feature_layer,
        "head_layers": head_layers,
        "final_dense": final,
        "last_conv": last_conv,
        "feature_shape": tuple(int(d) for d in feature_layer.output.shape[1:]),
    }


def describe_target_layer(model) -> dict:
    """Report which layers Grad-CAM uses (handy for logs and for verification)."""
    s = _resolve_structure(model)
    return {
        "feature_layer": s["feature_layer"].name,
        "last_conv_layer": s["last_conv"],
        "feature_map_shape": s["feature_shape"],
        "preprocessing_layers": [layer.name for layer in s["pre_layers"]],
        "head_layers": [layer.name for layer in s["head_layers"]],
    }


# --------------------------------------------------------------------------- #
# Grad-CAM core
# --------------------------------------------------------------------------- #

def compute_gradcam(
    model,
    batch: np.ndarray,
    class_index: int,
    reference_probs: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Return a Grad-CAM map in [0, 1] with the spatial size of the feature map.

    Args:
        model: the loaded ``mobilenetv2_final.keras`` model.
        batch: float32 array (1, 224, 224, 3), raw RGB pixels in [0, 255] -
            the very array ``predict()`` passes to ``model.predict``.
            Do NOT preprocess it; the model's Lambda layer does that.
        class_index: the class to explain (the one the model predicted).
        reference_probs: optional probabilities from ``model.predict`` for the
            same batch. When given, the Grad-CAM forward pass must reproduce
            them, otherwise the explanation would not describe the prediction.
    """
    import tensorflow as tf

    batch = np.asarray(batch)
    if batch.ndim != 4 or batch.shape[0] != 1 or batch.shape[-1] != 3:
        raise GradCAMError(
            f"Grad-CAM expects one image of shape (1, H, W, 3), got {batch.shape}."
        )
    if not np.isfinite(batch).all():
        raise GradCAMError("The input image contains invalid pixel values.")

    s = _resolve_structure(model)

    try:
        n_classes = int(s["final_dense"].units)
        class_index = int(class_index)
    except (TypeError, ValueError) as exc:
        raise GradCAMError("Invalid class index for Grad-CAM.") from exc
    if not 0 <= class_index < n_classes:
        raise GradCAMError(f"Class index {class_index} is outside 0..{n_classes - 1}.")

    final_dense = s["final_dense"]
    activation_name = getattr(final_dense.activation, "__name__", "")
    if activation_name not in ("softmax", "linear"):
        raise GradCAMError(
            f"Unsupported final activation '{activation_name}' for Grad-CAM."
        )

    x = tf.convert_to_tensor(batch, dtype=tf.float32)

    with tf.GradientTape() as tape:
        # 1) The model's own preprocessing (applied once, inside the model).
        for layer in s["pre_layers"]:
            x = layer(x, training=False)

        # 2) Backbone -> feature map. Gradients are taken w.r.t. this tensor.
        feature_map = s["feature_layer"](x, training=False)
        tape.watch(feature_map)

        # 3) Classifier head (inference mode: dropout off).
        h = feature_map
        for layer in s["head_layers"][:-1]:
            h = layer(h, training=False)

        # 4) Final Dense: use the pre-softmax logits as the class score.
        logits = tf.matmul(h, final_dense.kernel)
        if final_dense.bias is not None:
            logits = logits + final_dense.bias
        class_score = logits[:, class_index]

    grads = tape.gradient(class_score, feature_map)
    if grads is None:
        raise GradCAMError("No gradient could be computed for the feature map.")

    probs = tf.nn.softmax(logits, axis=-1).numpy()[0]

    # Guard: the explanation must describe the model's actual prediction.
    if int(np.argmax(probs)) != class_index:
        raise GradCAMError(
            "Grad-CAM forward pass disagrees with the predicted class; "
            "refusing to show a heatmap for a different class."
        )
    if reference_probs is not None:
        reference = np.asarray(reference_probs, dtype=np.float64).reshape(-1)
        if reference.shape != probs.shape or not np.allclose(
            probs, reference, atol=1e-3
        ):
            raise GradCAMError(
                "Grad-CAM forward pass does not reproduce the model's prediction; "
                "refusing to show a possibly misleading heatmap."
            )

    # Channel weights = spatial mean of gradients; CAM = ReLU(sum_k w_k * A_k).
    weights = tf.reduce_mean(grads, axis=(1, 2))                      # (1, C)
    cam = tf.reduce_sum(feature_map * weights[:, None, None, :], axis=-1)
    cam = tf.nn.relu(cam)[0].numpy().astype(np.float32)               # (h, w)

    if not np.isfinite(cam).all():
        raise GradCAMError("Grad-CAM produced invalid (NaN/Inf) values.")

    peak = float(cam.max())
    if peak <= 1e-12:
        raise GradCAMError(
            "The model found no region supporting this class, so there is "
            "nothing meaningful to highlight."
        )

    return cam / peak


# --------------------------------------------------------------------------- #
# Overlay rendering
# --------------------------------------------------------------------------- #

def _jet(values: np.ndarray) -> np.ndarray:
    """Jet-style colormap, (H, W) in [0, 1] -> (H, W, 3) float in [0, 1].

    Implemented with NumPy so the project needs no extra dependency
    (OpenCV / Matplotlib).
    """
    v = np.clip(values, 0.0, 1.0)
    r = np.clip(1.5 - np.abs(4.0 * v - 3.0), 0.0, 1.0)
    g = np.clip(1.5 - np.abs(4.0 * v - 2.0), 0.0, 1.0)
    b = np.clip(1.5 - np.abs(4.0 * v - 1.0), 0.0, 1.0)
    return np.stack([r, g, b], axis=-1)


def make_overlay(image: Image.Image, cam: np.ndarray) -> Image.Image:
    """Blend the Grad-CAM map onto the original leaf photo.

    Weakly activated areas keep the original leaf visible; strongly activated
    areas become red/yellow. Returns an RGB ``PIL.Image`` (accepted directly by
    ``st.image``).
    """
    cam = np.asarray(cam, dtype=np.float32)
    if cam.ndim != 2 or not np.isfinite(cam).all():
        raise GradCAMError("Invalid Grad-CAM map for the overlay.")

    base = image.convert("RGB")
    width, height = base.size

    # predict() resizes the whole photo straight to 224x224 (no crop, no padding),
    # so stretching the map back to the photo's size keeps it aligned.
    cam_img = Image.fromarray(cam, mode="F").resize((width, height), Image.Resampling.BILINEAR)
    cam_big = np.clip(np.asarray(cam_img, dtype=np.float32), 0.0, 1.0)

    colour = _jet(cam_big)
    photo = np.asarray(base, dtype=np.float32) / 255.0

    alpha = (0.15 + 0.55 * cam_big)[..., None]       # 15% .. 70% heat colour
    blended = photo * (1.0 - alpha) + colour * alpha

    return Image.fromarray(np.clip(blended * 255.0 + 0.5, 0, 255).astype(np.uint8), mode="RGB")


def generate_gradcam_overlay(
    model,
    batch: np.ndarray,
    image: Image.Image,
    class_index: int,
    reference_probs: Optional[np.ndarray] = None,
) -> Image.Image:
    """Grad-CAM for ``class_index`` overlaid on ``image`` (RGB PIL image).

    ``batch`` must be the same array that was fed to ``model.predict``.
    Raises ``GradCAMError`` if a reliable heatmap cannot be produced.
    """
    cam = compute_gradcam(model, batch, class_index, reference_probs=reference_probs)
    return make_overlay(image, cam)
