import io

import cv2
import numpy as np
from matplotlib.figure import Figure
from PIL import Image

ALPHA = 1.0
IMAGE_EXTENSIONS = "Image (*.bmp *.jpg *.png *.gif){.bmp,.jpg,.png,.gif}"
PYTHON_EXTENSIONS = "Source file (*.py){.py}"
CSV_EXTENSIONS = "Segments (*.csv){.csv}"


def figure_texture(figure: Figure) -> list[float]:
    buffer = io.BytesIO()
    figure.savefig(buffer, format="png")
    buffer.seek(0)
    image = Image.open(buffer).convert("RGBA")
    texture = np.asarray(image, dtype=np.float32) / 255.0
    return texture.ravel().tolist()


def array_texture(
    image: np.ndarray,
    size: tuple[int, int] | None = None,
) -> list[float]:
    resized = image if size is None else cv2.resize(image, size)
    normalized = np.clip(resized, 0.0, 1.0).astype(np.float32)
    rgba = np.empty((*normalized.shape, 4), dtype=np.float32)
    rgba[..., :3] = normalized[..., None]
    rgba[..., 3] = ALPHA
    return rgba.ravel().tolist()


def segments_texture(segments: np.ndarray, size: tuple[int, int]) -> list[float]:
    width, height = size
    image = np.zeros((height, width), dtype=np.float32)
    scaled = segments * np.array([width, height])
    for start, end in scaled.astype(int):
        cv2.line(image, tuple(start), tuple(end), 1.0, 1)
    return array_texture(image)
