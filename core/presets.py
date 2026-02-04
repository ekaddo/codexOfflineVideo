from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable

from PIL import Image, ImageDraw


@dataclass(frozen=True)
class Preset:
    key: str
    label: str
    resolution: tuple[int, int]
    fps: int
    avatar_box: tuple[int, int]
    avatar_pos: tuple[int, int]
    content_box: tuple[int, int, int, int] | None
    background_style: str
    crop_focus_y: float | None


PRESETS: Dict[str, Preset] = {
    "news_anchor": Preset(
        key="news_anchor",
        label="News Anchor",
        resolution=(1280, 720),
        fps=24,
        avatar_box=(480, 600),
        avatar_pos=(70, 80),
        content_box=(640, 130, 560, 330),
        background_style="news",
        crop_focus_y=0.55,
    ),
    "corporate_presenter": Preset(
        key="corporate_presenter",
        label="Corporate Presenter",
        resolution=(1280, 720),
        fps=24,
        avatar_box=(440, 580),
        avatar_pos=(70, 90),
        content_box=(560, 140, 640, 320),
        background_style="corporate",
        crop_focus_y=0.52,
    ),
    "teacher": Preset(
        key="teacher",
        label="Teacher",
        resolution=(1280, 720),
        fps=24,
        avatar_box=(420, 560),
        avatar_pos=(70, 100),
        content_box=(590, 110, 620, 380),
        background_style="teacher",
        crop_focus_y=0.5,
    ),
    "coach": Preset(
        key="coach",
        label="Coach",
        resolution=(1280, 720),
        fps=24,
        avatar_box=(480, 600),
        avatar_pos=(70, 80),
        content_box=(620, 140, 560, 300),
        background_style="coach",
        crop_focus_y=0.58,
    ),
    "podcast_closeup": Preset(
        key="podcast_closeup",
        label="Podcast Close-up",
        resolution=(1280, 720),
        fps=24,
        avatar_box=(640, 640),
        avatar_pos=(320, 40),
        content_box=None,
        background_style="podcast",
        crop_focus_y=0.42,
    ),
    "ceo_keynote": Preset(
        key="ceo_keynote",
        label="CEO Keynote",
        resolution=(1280, 720),
        fps=24,
        avatar_box=(420, 560),
        avatar_pos=(760, 100),
        content_box=(80, 120, 600, 360),
        background_style="keynote",
        crop_focus_y=0.55,
    ),
}


def list_presets() -> Iterable[Preset]:
    return PRESETS.values()


def get_preset(key: str | None) -> Preset | None:
    if not key:
        return None
    return PRESETS.get(key)


def resolve_preset_key(label_or_key: str | None) -> str | None:
    if not label_or_key:
        return None
    lower = label_or_key.strip().lower().replace(" ", "_")
    if lower in PRESETS:
        return lower
    for preset in PRESETS.values():
        if preset.label.lower() == label_or_key.strip().lower():
            return preset.key
    return None


def render_background(preset: Preset, out_dir: Path, custom_path: Path | None = None) -> Path:
    if custom_path:
        return custom_path

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{preset.key}_bg.png"
    if out_path.exists():
        return out_path

    width, height = preset.resolution
    if preset.background_style == "news":
        top = (8, 22, 45)
        bottom = (12, 30, 60)
        accent = (30, 120, 210)
        desk = (15, 25, 35)
    elif preset.background_style == "corporate":
        top = (230, 235, 240)
        bottom = (200, 205, 215)
        accent = (40, 90, 180)
        desk = (210, 215, 225)
    elif preset.background_style == "teacher":
        top = (246, 234, 210)
        bottom = (230, 215, 190)
        accent = (60, 120, 80)
        desk = (220, 205, 180)
    elif preset.background_style == "podcast":
        top = (18, 16, 24)
        bottom = (8, 8, 12)
        accent = (220, 150, 60)
        desk = (18, 20, 26)
    elif preset.background_style == "keynote":
        top = (12, 12, 18)
        bottom = (4, 4, 8)
        accent = (70, 140, 255)
        desk = (10, 10, 14)
    else:
        top = (20, 24, 33)
        bottom = (10, 12, 18)
        accent = (200, 140, 40)
        desk = (18, 20, 26)

    img = _gradient(width, height, top, bottom)
    draw = ImageDraw.Draw(img)

    # Desk strip
    draw.rectangle((0, int(height * 0.75), width, height), fill=desk)

    # Content panel area
    if preset.content_box:
        x, y, w, h = preset.content_box
        _rounded_rect(draw, (x, y, x + w, y + h), 16, outline=accent, fill=(0, 0, 0, 0), width=4)
        _rounded_rect(draw, (x + 6, y + 6, x + w - 6, y + h - 6), 14, outline=None, fill=(255, 255, 255, 30))

    # Lower third bar
    draw.rectangle((0, int(height * 0.68), width, int(height * 0.72)), fill=accent)

    img.save(out_path)
    return out_path


def _gradient(width: int, height: int, top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    base = Image.new("RGB", (width, height), top)
    draw = ImageDraw.Draw(base)
    for y in range(height):
        ratio = y / max(1, height - 1)
        r = int(top[0] * (1 - ratio) + bottom[0] * ratio)
        g = int(top[1] * (1 - ratio) + bottom[1] * ratio)
        b = int(top[2] * (1 - ratio) + bottom[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    return base


def _rounded_rect(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    radius: int,
    outline=None,
    fill=None,
    width: int = 1,
) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=radius, outline=outline, fill=fill, width=width)
