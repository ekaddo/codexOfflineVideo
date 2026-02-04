from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .config import load_config
from .echomimic import run_echomimic
from .image_utils import prepare_avatar_image
from .tts import generate_tts


@dataclass
class PipelineInputs:
    avatar_image: Path
    script_text: str
    voice_sample: Path
    reference_video: Path | None = None


@dataclass
class PipelineOutputs:
    audio_path: Path
    image_path: Path
    video_path: Path


class AvatarPipeline:
    def __init__(self, config_path: str | Path = "config.json"):
        self.config = load_config(config_path)

    def run(self, inputs: PipelineInputs) -> PipelineOutputs:
        output_dir = Path(self.config["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)

        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prepared_image = output_dir / f"avatar_{stamp}.png"
        audio_path = output_dir / f"audio_{stamp}.wav"
        video_path = output_dir / f"generated_{stamp}.mp4"

        # Prepare image
        prepare_avatar_image(
            inputs.avatar_image, prepared_image, size=self.config.get("image_size", 512)
        )

        # TTS
        tts_cfg = self.config.get("tts", {})
        if tts_cfg.get("enable", True):
            generate_tts(
                text=inputs.script_text,
                speaker_wav=inputs.voice_sample,
                out_wav=audio_path,
                model_name=tts_cfg.get("model_name"),
                language=tts_cfg.get("language", "en"),
            )
        else:
            raise RuntimeError("TTS is disabled in config.json")

        run_echomimic(
            echomimic_dir=self.config["echo_mimic_dir"],
            weights_dir=self.config["echo_mimic_weights"],
            image_path=prepared_image,
            audio_path=audio_path,
            out_path=video_path,
            ref_video=inputs.reference_video,
        )

        return PipelineOutputs(
            audio_path=audio_path,
            image_path=prepared_image,
            video_path=video_path,
        )
