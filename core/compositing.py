from __future__ import annotations

from pathlib import Path
import subprocess

from .presets import Preset


def compose_video(
    background_path: str | Path,
    avatar_video_path: str | Path,
    out_path: str | Path,
    preset: Preset,
    ffmpeg_path: str = "ffmpeg",
) -> Path:
    background_path = Path(background_path)
    avatar_video_path = Path(avatar_video_path)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    bg_is_image = background_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp"}
    width, height = preset.resolution
    av_w, av_h = preset.avatar_box
    av_x, av_y = preset.avatar_pos

    filter_complex = (
        f"[0:v]scale={width}:{height}[bg];"
        f"[1:v]scale={av_w}:{av_h}[av];"
        f"[bg][av]overlay={av_x}:{av_y}:format=auto,format=yuv420p[v]"
    )

    cmd = [ffmpeg_path, "-y"]
    if bg_is_image:
        cmd += ["-loop", "1", "-i", str(background_path)]
    else:
        cmd += ["-i", str(background_path)]
    cmd += ["-i", str(avatar_video_path)]
    cmd += [
        "-filter_complex",
        filter_complex,
        "-map",
        "[v]",
        "-map",
        "1:a?",
        "-shortest",
        str(out_path),
    ]

    subprocess.run(cmd, check=True)
    return out_path
