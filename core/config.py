import json
import os
from pathlib import Path

DEFAULT_CONFIG = {
    "echo_mimic_dir": "..\\EchoMimic",
    "echo_mimic_weights": "..\\EchoMimic\\pretrained_weights",
    "ffmpeg_path": "ffmpeg",
    "output_dir": "outputs",
    "image_size": 512,
    "tts": {
        "enable": True,
        "model_name": "tts_models/multilingual/multi-dataset/xtts_v2",
        "language": "en",
    },
}


def load_config(config_path: str | Path = "config.json") -> dict:
    path = Path(config_path)
    config = DEFAULT_CONFIG.copy()
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            user_cfg = json.load(f)
        config = _deep_merge(config, user_cfg)

    # Allow environment overrides
    config["echo_mimic_dir"] = os.environ.get("ECHO_MIMIC_DIR", config["echo_mimic_dir"])
    config["echo_mimic_weights"] = os.environ.get("ECHO_MIMIC_WEIGHTS", config["echo_mimic_weights"])
    config["ffmpeg_path"] = os.environ.get("FFMPEG_PATH", config["ffmpeg_path"])

    return config


def _deep_merge(base: dict, override: dict) -> dict:
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            base[key] = _deep_merge(base[key], value)
        else:
            base[key] = value
    return base
