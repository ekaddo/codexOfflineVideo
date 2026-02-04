from __future__ import annotations

from pathlib import Path
from typing import List

from pydub import AudioSegment


def split_audio(
    audio_path: str | Path,
    out_dir: str | Path,
    chunk_seconds: int,
    prefix: str = "chunk",
) -> List[Path]:
    audio_path = Path(audio_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    audio = AudioSegment.from_file(audio_path)
    chunk_ms = chunk_seconds * 1000
    chunks = []
    for i, start in enumerate(range(0, len(audio), chunk_ms), start=1):
        segment = audio[start : start + chunk_ms]
        out_path = out_dir / f"{prefix}_{i:03d}.wav"
        segment.export(out_path, format="wav")
        chunks.append(out_path)

    return chunks
