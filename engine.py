"""
Holi-fy Colorization Engine
============================
Handles model loading, inference, and post-processing for the
Color Restoration Engine.

Uses the Zhang et al. deep colorization model via OpenCV's DNN module
and applies a L*a*b* saturation boost ("Gulaal effect").
"""

from __future__ import annotations

import os
import urllib.request
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from PIL import Image

import config


# ─────────────────────────────────────────────────────────────────────────────
# Model Download Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _ensure_dir(path: str) -> None:
    """Create directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)


def _download_file(url: str, dest: str, description: str = "") -> None:
    """Download a file with progress feedback."""
    if os.path.exists(dest):
        return
    print(f"⬇  Downloading {description or dest} …")
    try:
        urllib.request.urlretrieve(url, dest)
        print(f"✅  {description or dest} downloaded successfully.")
    except Exception as exc:
        raise RuntimeError(
            f"Failed to download {description}: {exc}\n"
            f"URL: {url}"
        ) from exc


def download_model_assets(model_dir: Optional[str] = None) -> dict[str, str]:
    """
    Ensure all three model assets are available locally.

    Returns a dict with keys 'prototxt', 'caffemodel', 'hull_pts'
    mapping to their absolute file paths.
    """
    model_dir = model_dir or config.MODEL_DIR
    _ensure_dir(model_dir)

    paths = {
        "prototxt": os.path.join(model_dir, config.PROTOTXT_FILE),
        "caffemodel": os.path.join(model_dir, config.CAFFEMODEL_FILE),
        "hull_pts": os.path.join(model_dir, config.HULL_PTS_FILE),
    }

    _download_file(config.PROTOTXT_URL, paths["prototxt"], "prototxt")
    _download_file(config.CAFFEMODEL_URL, paths["caffemodel"], "caffemodel (~123 MB)")
    _download_file(config.HULL_PTS_URL, paths["hull_pts"], "hull cluster centres")

    # Validate caffemodel size — a corrupt download (e.g. HTML error page)
    # will be tiny compared to the expected ~123 MB file.
    caffemodel_size = os.path.getsize(paths["caffemodel"])
    if caffemodel_size < config.CAFFEMODEL_MIN_BYTES:
        os.remove(paths["caffemodel"])
        raise RuntimeError(
            f"Downloaded caffemodel is only {caffemodel_size / 1024:.0f} KB "
            f"(expected ≥ {config.CAFFEMODEL_MIN_BYTES / 1024 / 1024:.0f} MB). "
            f"The download URL may be dead. The corrupt file has been deleted — "
            f"please restart the app to retry."
        )

    return paths


# ─────────────────────────────────────────────────────────────────────────────
# Model Loading
# ─────────────────────────────────────────────────────────────────────────────

def load_colorization_model(
    paths: Optional[dict[str, str]] = None,
) -> cv2.dnn.Net:
    """
    Load the Caffe colorization DNN and inject the cluster centres
    as 1×1 convolution weights.
    """
    if paths is None:
        paths = download_model_assets()

    net = cv2.dnn.readNetFromCaffe(paths["prototxt"], paths["caffemodel"])

    # Load ab quantisation cluster centres (313 colours, shape 2×313)
    pts = np.load(paths["hull_pts"])            # (313, 2)
    pts = pts.transpose().reshape(2, 313, 1, 1)  # reshaping for 1x1 conv

    # Inject into the network's class-rebalancing layer
    net.getLayer(net.getLayerId("class8_ab")).blobs = [pts.astype(np.float32)]
    net.getLayer(net.getLayerId("conv8_313_rh")).blobs = [
        np.full([1, 313], 2.606, dtype=np.float32)
    ]

    return net


# ─────────────────────────────────────────────────────────────────────────────
# Inference
# ─────────────────────────────────────────────────────────────────────────────

def _resize_for_processing(img: np.ndarray, max_dim: int) -> np.ndarray:
    """Proportionally resize so that the longest side ≤ max_dim."""
    h, w = img.shape[:2]
    if max(h, w) <= max_dim:
        return img
    scale = max_dim / max(h, w)
    new_w, new_h = int(w * scale), int(h * scale)
    return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)


def colorize(
    net: cv2.dnn.Net,
    image: np.ndarray,
    max_dim: int = config.MAX_PROCESSING_DIM,
) -> np.ndarray:
    """
    Run the colorization network on a BGR or grayscale image.

    Parameters
    ----------
    net : cv2.dnn.Net
        The loaded Caffe colorization model.
    image : np.ndarray
        Input image (BGR uint8).
    max_dim : int
        Maximum processing dimension.

    Returns
    -------
    np.ndarray
        Colorized image in BGR uint8 format.
    """
    image = _resize_for_processing(image, max_dim)

    # Convert to float32 L*a*b*, extract L, and normalise
    img_float = image.astype(np.float32) / 255.0
    lab = cv2.cvtColor(img_float, cv2.COLOR_BGR2Lab)
    L_channel = lab[:, :, 0]            # lightness (0-100)
    L_centered = L_channel - 50         # centre around 0

    # Prepare the blob (224×224 expected by the net)
    blob = cv2.dnn.blobFromImage(L_centered, size=(224, 224))
    net.setInput(blob)
    ab_predicted = net.forward()[0]      # shape (2, 56, 56)

    # Resize predicted ab channels back to image dimensions
    ab_predicted = ab_predicted.transpose((1, 2, 0))   # (56, 56, 2)
    ab_predicted = cv2.resize(
        ab_predicted, (image.shape[1], image.shape[0])
    )

    # Combine with original L channel
    lab_colorized = np.zeros_like(lab)
    lab_colorized[:, :, 0] = L_channel
    lab_colorized[:, :, 1:] = ab_predicted

    # Convert back to BGR
    result = cv2.cvtColor(lab_colorized, cv2.COLOR_Lab2BGR)
    result = np.clip(result * 255.0, 0, 255).astype(np.uint8)
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Post-processing — Gulaal Saturation Boost
# ─────────────────────────────────────────────────────────────────────────────

def apply_gulaal_boost(
    image: np.ndarray,
    factor: float = config.DEFAULT_SATURATION_BOOST,
) -> np.ndarray:
    """
    Boost saturation in L*a*b* colour space by scaling the a* and b*
    channels.  This simulates the vivid, festive "Gulaal" look.

    Parameters
    ----------
    image : np.ndarray
        BGR uint8 image (the colorized output).
    factor : float
        Multiplication factor for the a* and b* channels.
        1.0 = no change, >1.0 = more vivid.

    Returns
    -------
    np.ndarray
        Saturation-boosted BGR uint8 image.
    """
    img_float = image.astype(np.float32) / 255.0
    lab = cv2.cvtColor(img_float, cv2.COLOR_BGR2Lab)

    # Scale the chrominance channels
    lab[:, :, 1] = lab[:, :, 1] * factor   # a* channel
    lab[:, :, 2] = lab[:, :, 2] * factor   # b* channel

    # Convert back
    result = cv2.cvtColor(lab, cv2.COLOR_Lab2BGR)
    result = np.clip(result * 255.0, 0, 255).astype(np.uint8)
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Convenience Pipeline
# ─────────────────────────────────────────────────────────────────────────────

def pil_to_cv2(pil_img: Image.Image) -> np.ndarray:
    """Convert a PIL Image (RGB) to an OpenCV BGR array."""
    rgb = np.array(pil_img.convert("RGB"))
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def cv2_to_pil(cv2_img: np.ndarray) -> Image.Image:
    """Convert an OpenCV BGR array to a PIL Image (RGB)."""
    rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)


def restore_colors(
    net: cv2.dnn.Net,
    pil_image: Image.Image,
    saturation_boost: float = config.DEFAULT_SATURATION_BOOST,
) -> Image.Image:
    """
    Full pipeline: PIL in → colorize → Gulaal boost → PIL out.
    """
    bgr = pil_to_cv2(pil_image)
    colorized = colorize(net, bgr)
    boosted = apply_gulaal_boost(colorized, factor=saturation_boost)
    return cv2_to_pil(boosted)
