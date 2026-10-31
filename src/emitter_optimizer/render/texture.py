import io

import numpy as np
from PIL import Image, ImageDraw

ALPHA = 1.0
IMAGE_EXTENSIONS = "Image (*.bmp *.jpg *.png *.gif){.bmp,.jpg,.png,.gif}"
PYTHON_EXTENSIONS = "Source file (*.py){.py}"
CSV_EXTENSIONS = "Segments (*.csv){.csv}"


def texture_from_png(data: bytes) -> list[float]:
    image = Image.open(io.BytesIO(data)).convert("RGBA")
    pixels = np.asarray(image, dtype=np.float32) / 255.0
    return pixels.ravel().tolist()


def array_texture(
    image: np.ndarray,
    size: tuple[int, int],
) -> list[float]:
    values = np.asarray(image, dtype=np.float32)
    if values.ndim == 3:
        values = values.mean(axis=2)
    grey = np.clip(values, 0.0, 1.0)
    resized = Image.fromarray((grey * 255.0).astype(np.uint8), mode="L").resize(
        size, Image.Resampling.NEAREST
    )
    pixels = np.asarray(resized, dtype=np.float32) / 255.0
    rgba = np.empty((*pixels.shape, 4), dtype=np.float32)
    rgba[..., :3] = pixels[..., None]
    rgba[..., 3] = ALPHA
    return rgba.ravel().tolist()


def segments_texture(segments: np.ndarray, size: tuple[int, int]) -> list[float]:
    width, height = size
    image = Image.new("L", size, 0)
    draw = ImageDraw.Draw(image)
    scaled = np.asarray(segments, dtype=np.float64) * np.array([width, height])
    for start, end in scaled:
        draw.line([tuple(start), tuple(end)], fill=255, width=1)
    return array_texture(np.asarray(image, dtype=np.float32) / 255.0, size)
