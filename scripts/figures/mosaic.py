from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageSequence

from emitter_optimizer.service.paths import PROJECT_ROOT
from scripts.figures.photo_cases import FIGURES

SPACES = PROJECT_ROOT / "docs" / "figures"
TILES = (
    ("Sprinklers", FIGURES / "garden.webp"),
    ("Lifeguards", FIGURES / "beach.webp"),
    ("Wi-Fi", FIGURES / "marina.webp"),
    ("Lamps", FIGURES / "harbor.webp"),
    ("Sirens", FIGURES / "ramparts.webp"),
    ("Stations on Earth", SPACES / "case_globe.gif"),
    ("Access points in a building", SPACES / "case_building.gif"),
    ("Atoms in a crystal", SPACES / "case_urea.gif"),
)
COLUMNS = 4
TILE = (360, 240)
FRAMES = 36
FRAME_MILLISECONDS = 110
GAP = 4
BACKGROUND = "#0f1216"
LABEL = ImageFont.load_default(size=17)


def _fit(frame: Image.Image) -> Image.Image:
    tile = Image.new("RGB", TILE, BACKGROUND)
    scale = max(TILE[0] / frame.width, TILE[1] / frame.height)
    if frame.width / frame.height > 2.0 or frame.width == frame.height:
        scale = min(TILE[0] / frame.width, TILE[1] / frame.height)
    size = (round(frame.width * scale), round(frame.height * scale))
    fitted = frame.convert("RGB").resize(size, Image.Resampling.LANCZOS)
    tile.paste(fitted, ((TILE[0] - size[0]) // 2, (TILE[1] - size[1]) // 2))
    return tile


def _frames(path: Path) -> list[Image.Image]:
    source = [frame.copy() for frame in ImageSequence.Iterator(Image.open(path))]
    picks = [round(i * (len(source) - 1) / (FRAMES - 1)) for i in range(FRAMES)]
    return [_fit(source[pick]) for pick in picks]


def _label(tile: Image.Image, text: str) -> None:
    draw = ImageDraw.Draw(tile, "RGBA")
    box = draw.textbbox((10, TILE[1] - 12), text, font=LABEL, anchor="lb")
    draw.rectangle(
        (box[0] - 5, box[1] - 4, box[2] + 5, box[3] + 4), fill=(10, 12, 16, 190)
    )
    draw.text((10, TILE[1] - 12), text, fill="#ffffff", font=LABEL, anchor="lb")


def render() -> None:
    columns = [(label, _frames(path)) for label, path in TILES]
    rows = (len(TILES) + COLUMNS - 1) // COLUMNS
    size = (
        COLUMNS * TILE[0] + (COLUMNS - 1) * GAP,
        rows * TILE[1] + (rows - 1) * GAP,
    )
    sheets = []
    for frame in range(FRAMES):
        sheet = Image.new("RGB", size, BACKGROUND)
        for index, (label, frames) in enumerate(columns):
            tile = frames[frame].copy()
            _label(tile, label)
            at = (
                (index % COLUMNS) * (TILE[0] + GAP),
                (index // COLUMNS) * (TILE[1] + GAP),
            )
            sheet.paste(tile, at)
        sheets.append(sheet)
    buffer = BytesIO()
    sheets[0].save(
        buffer,
        format="WEBP",
        save_all=True,
        append_images=sheets[1:],
        duration=[FRAME_MILLISECONDS] * (FRAMES - 1) + [1800],
        loop=0,
        quality=68,
        method=4,
    )
    (FIGURES / "mosaic.webp").write_bytes(buffer.getvalue())
