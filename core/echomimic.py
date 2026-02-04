from __future__ import annotations

import os
import subprocess
from pathlib import Path


def run_echomimic(
    echomimic_dir: str | Path,
    weights_dir: str | Path,
    image_path: str | Path,
    audio_path: str | Path,
    out_path: str | Path,
    ref_video: str | Path | None = None,
    config_name: str = "configs/infer_audio2vid.yaml",
) -> Path:
    echomimic_dir = Path(echomimic_dir)
    weights_dir = Path(weights_dir)
    image_path = Path(image_path)
    audio_path = Path(audio_path)
    out_path = Path(out_path)

    if not echomimic_dir.exists():
        raise FileNotFoundError(f"EchoMimic dir not found: {echomimic_dir}")
    if not weights_dir.exists():
        raise FileNotFoundError(f"EchoMimic weights not found: {weights_dir}")

    script_path = echomimic_dir / "infer_audio2vid.py"
    if not script_path.exists():
        raise FileNotFoundError(f"EchoMimic script not found: {script_path}")

    out_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "python",
        str(script_path),
        "--config",
        str(echomimic_dir / config_name),
        "--ckpt_path",
        str(weights_dir),
        "--input_image",
        str(image_path),
        "--input_audio",
        str(audio_path),
        "--output_video",
        str(out_path),
    ]

    if ref_video:
        cmd.extend(["--input_video", str(ref_video)])

    env = os.environ.copy()
    subprocess.run(cmd, cwd=str(echomimic_dir), check=True, env=env)
    return out_path
