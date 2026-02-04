from __future__ import annotations

import math
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import subprocess


def generate_dummy_audio(out_wav: str | Path, duration_seconds: float = 4.0, freq_hz: float = 440.0) -> Path:
    out_wav = Path(out_wav)
    out_wav.parent.mkdir(parents=True, exist_ok=True)

    sample_rate = 44100
    amplitude = 0.2
    num_samples = int(duration_seconds * sample_rate)

    with wave.open(str(out_wav), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for i in range(num_samples):
            t = i / sample_rate
            sample = amplitude * math.sin(2 * math.pi * freq_hz * t)
            wf.writeframes(int(sample * 32767).to_bytes(2, byteorder="little", signed=True))

    return out_wav


def generate_dummy_image(out_path: str | Path, size: int = 512, label: str = "RealTalk Demo") -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGB", (size, size), (20, 24, 33))
    draw = ImageDraw.Draw(img)

    # Use default font for portability
    text = label
    bbox = draw.textbbox((0, 0), text)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (size - text_w) // 2
    y = (size - text_h) // 2
    draw.text((x, y), text, fill=(220, 230, 255))

    img.save(out_path)
    return out_path


def generate_dummy_video(
    image_path: str | Path,
    audio_path: str | Path,
    out_path: str | Path,
    ffmpeg_path: str = "ffmpeg",
) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        ffmpeg_path,
        "-y",
        "-loop",
        "1",
        "-i",
        str(image_path),
        "-i",
        str(audio_path),
        "-c:v",
        "libx264",
        "-tune",
        "stillimage",
        "-shortest",
        "-pix_fmt",
        "yuv420p",
        str(out_path),
    ]

    subprocess.run(cmd, check=True)
    return out_path
