"""Simple photo-quality checks (blur, too dark, too bright).

These run BEFORE the model so the app can ask for a retake early.
The thresholds are starting values - tune them later using your own
field photos (look at the scores of good and bad photos).
"""
import numpy as np
from PIL import Image

BLUR_THRESHOLD = 60.0     # below this the photo is probably blurry
DARK_THRESHOLD = 50       # mean brightness (0-255) below this = too dark
BRIGHT_THRESHOLD = 215    # above this = too bright / washed out


def _laplacian_variance(gray: np.ndarray) -> float:
    """Variance of the Laplacian: low value = few sharp edges = blurry."""
    g = gray.astype(np.float32)
    lap = (-4 * g[1:-1, 1:-1] + g[:-2, 1:-1] + g[2:, 1:-1]
           + g[1:-1, :-2] + g[1:-1, 2:])
    return float(lap.var())


def check_quality(image: Image.Image) -> dict:
    small = image.convert("L")
    small.thumbnail((512, 512))
    gray = np.asarray(small)
    blur_score = _laplacian_variance(gray)
    brightness = float(gray.mean())

    issues = []
    if blur_score < BLUR_THRESHOLD:
        issues.append("The photo looks blurry. Hold the phone steady and let it focus before taking the photo.")
    if brightness < DARK_THRESHOLD:
        issues.append("The photo is too dark. Move to better light or avoid your own shadow on the leaf.")
    if brightness > BRIGHT_THRESHOLD:
        issues.append("The photo is too bright. Avoid direct glare on the leaf.")
    return {"ok": not issues, "issues": issues,
            "blur_score": round(blur_score, 1), "brightness": round(brightness, 1)}
