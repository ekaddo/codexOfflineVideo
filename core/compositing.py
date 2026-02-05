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
    duration_seconds: float | None = None,
    encoder: str = "libx264",
    preset_speed: str = "veryfast",
    crf: int = 23,
    subtitle_ass: str | Path | None = None,
) -> Path:
    background_path = Path(background_path)
    avatar_video_path = Path(avatar_video_path)
    out_path = Path(out_path)
    background_path = background_path.resolve()
    avatar_video_path = avatar_video_path.resolve()
    out_path = out_path.resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    bg_is_image = background_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp"}
    width, height = preset.resolution
    av_w, av_h = preset.avatar_box
    av_x, av_y = preset.avatar_pos

    filter_complex = (
        f"[0:v]scale={width}:{height}[bg];"
        f"[1:v]scale={av_w}:{av_h}[av];"
        f"[bg][av]overlay={av_x}:{av_y}:format=auto[ov]"
    )
    if subtitle_ass:
        subtitle_ass = Path(subtitle_ass)
        filter_complex += f";[ov]subtitles={subtitle_ass.name},format=yuv420p[v]"
    else:
        filter_complex += ";[ov]format=yuv420p[v]"

    cmd = [ffmpeg_path, "-y"]
    if bg_is_image:
        cmd += ["-loop", "1", "-i", str(background_path)]
    else:
        cmd += ["-i", str(background_path)]
    cmd += ["-i", str(avatar_video_path)]
    quality_flag = "-crf"
    extra_rc = []
    if "nvenc" in encoder:
        quality_flag = "-cq"
        extra_rc = ["-rc", "vbr"]

    cmd += [
        "-filter_complex",
        filter_complex,
        "-r",
        str(preset.fps),
        "-map",
        "[v]",
        "-map",
        "1:a?",
        "-c:v",
        encoder,
        "-preset",
        preset_speed,
        *extra_rc,
        quality_flag,
        str(crf),
        "-pix_fmt",
        "yuv420p",
        "-shortest",
    ]
    if duration_seconds:
        cmd += ["-t", f"{duration_seconds:.3f}"]
    cmd += [str(out_path)]

    subprocess.run(cmd, check=True, cwd=str(out_path.parent))
    return out_path
