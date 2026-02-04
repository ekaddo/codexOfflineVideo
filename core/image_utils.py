from __future__ import annotations

from pathlib import Path
from typing import Tuple

import numpy as np
from PIL import Image

try:
    import cv2
except Exception:  # pragma: no cover
    cv2 = None


def load_image(path: str | Path) -> Image.Image:
    img = Image.open(path).convert("RGB")
    return img


def auto_crop_square(img: Image.Image, focus_y: float | None = None) -> Image.Image:
    width, height = img.size
    size = min(width, height)
    left = (width - size) // 2
    if focus_y is None:
        upper = (height - size) // 2
    else:
        desired_center = int(height * max(0.0, min(1.0, focus_y)))
        upper = desired_center - size // 2
        upper = max(0, min(upper, height - size))
    return img.crop((left, upper, left + size, upper + size))


def face_center_crop(img: Image.Image, focus_y: float | None = None) -> Image.Image:
    if focus_y is not None:
        return auto_crop_square(img, focus_y=focus_y)
    if cv2 is None:
        return auto_crop_square(img)

    gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)
    if len(faces) == 0:
        return auto_crop_square(img)

    x, y, w, h = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)[0]
    cx = x + w // 2
    cy = y + h // 2
    size = max(w, h) * 2

    left = max(cx - size // 2, 0)
    upper = max(cy - size // 2, 0)
    right = min(left + size, img.size[0])
    lower = min(upper + size, img.size[1])

    # Re-center if we hit an edge
    left = max(right - size, 0)
    upper = max(lower - size, 0)

    return img.crop((left, upper, right, lower))


def prepare_avatar_image(
    path: str | Path,
    out_path: str | Path,
    size: int = 512,
    focus_y: float | None = None,
) -> Path:
    img = load_image(path)
    img = face_center_crop(img, focus_y=focus_y)
    img = img.resize((size, size), Image.LANCZOS)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    return out_path
