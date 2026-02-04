from __future__ import annotations

import os
import subprocess
from pathlib import Path
import tempfile

import soundfile as sf


def _write_config(
    echomimic_dir: Path,
    weights_dir: Path,
    image_path: Path,
    audio_path: Path,
    config_path: Path,
) -> None:
    inference_cfg = echomimic_dir / "configs" / "inference" / "inference_v2.yaml"
    config_text = f"""pretrained_base_model_path: \"{(weights_dir / 'sd-image-variations-diffusers').as_posix()}/\"
pretrained_vae_path: \"{(weights_dir / 'sd-vae-ft-mse').as_posix()}/\"
audio_model_path: \"{(weights_dir / 'audio_processor' / 'whisper_tiny.pt').as_posix()}\"

denoising_unet_path: \"{(weights_dir / 'denoising_unet.pth').as_posix()}\"
reference_unet_path: \"{(weights_dir / 'reference_unet.pth').as_posix()}\"
face_locator_path: \"{(weights_dir / 'face_locator.pth').as_posix()}\"
motion_module_path: \"{(weights_dir / 'motion_module.pth').as_posix()}\"

inference_config: \"{inference_cfg.as_posix()}\"
weight_dtype: 'fp16'

test_cases:
  \"{image_path.as_posix()}\": 
    - \"{audio_path.as_posix()}\"
"""
    config_path.write_text(config_text, encoding="utf-8")


def run_echomimic(
    echomimic_dir: str | Path,
    weights_dir: str | Path,
    image_path: str | Path,
    audio_path: str | Path,
    out_path: str | Path,
    ref_video: str | Path | None = None,
    config_name: str = "configs/infer_audio2vid.yaml",
) -> Path:
    echomimic_dir = Path(echomimic_dir).resolve()
    weights_dir = Path(weights_dir).resolve()
    image_path = Path(image_path).resolve()
    audio_path = Path(audio_path).resolve()
    out_path = Path(out_path).resolve()

    if not echomimic_dir.exists():
        raise FileNotFoundError(f"EchoMimic dir not found: {echomimic_dir}")
    if not weights_dir.exists():
        raise FileNotFoundError(f"EchoMimic weights not found: {weights_dir}")

    script_path = echomimic_dir / "infer_audio2vid.py"
    if not script_path.exists():
        raise FileNotFoundError(f"EchoMimic script not found: {script_path}")

    out_path = out_path.resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Build a temp config for the current inputs (EchoMimic CLI reads test_cases from config)
    tmp_dir = Path(tempfile.mkdtemp(prefix="echomimic_", dir=str(out_path.parent)))
    config_file = tmp_dir / "config.yaml"
    _write_config(echomimic_dir, weights_dir, image_path, audio_path, config_file)

    # Derive number of frames from audio length (default FPS 24)
    fps = 24
    duration_sec = sf.info(str(audio_path)).duration
    frames = max(12, int(duration_sec * fps))
    max_frames_env = os.environ.get("CODEXOFFLINEVIDEO_ECHOMIMIC_MAX_FRAMES")
    if max_frames_env:
        try:
            frames = min(frames, int(max_frames_env))
        except ValueError:
            pass

    cmd = [
        "python",
        str(script_path),
        "--config",
        str(config_file),
        "-W",
        "512",
        "-H",
        "512",
        "-L",
        str(frames),
        "--fps",
        str(fps),
        "--device",
        "cuda",
    ]

    steps_env = os.environ.get("CODEXOFFLINEVIDEO_ECHOMIMIC_STEPS")
    if steps_env:
        cmd.extend(["--steps", steps_env])

    env = os.environ.copy()
    subprocess.run(cmd, cwd=str(echomimic_dir), check=True, env=env)
    return out_path
