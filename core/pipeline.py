from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import os
import subprocess

from .audio_utils import split_audio
from .config import load_config
from .dummy_renderer import generate_dummy_audio, generate_dummy_image, generate_dummy_video
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

        if os.environ.get("CODEXOFFLINEVIDEO_DUMMY", "0") == "1":
            duration = min(30.0, max(3.0, len(inputs.script_text) / 15))
            dummy_image = generate_dummy_image(prepared_image, size=self.config.get("image_size", 512))
            dummy_audio = generate_dummy_audio(audio_path, duration_seconds=duration)
            generate_dummy_video(
                image_path=dummy_image,
                audio_path=dummy_audio,
                out_path=video_path,
                ffmpeg_path=self.config.get("ffmpeg_path", "ffmpeg"),
            )
        else:
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

            chunk_cfg = self.config.get("chunking", {})
            chunk_enabled = chunk_cfg.get("enabled", False)
            chunk_seconds = int(chunk_cfg.get("chunk_seconds", 360))
            env_chunk_seconds = os.environ.get("CODEXOFFLINEVIDEO_CHUNK_SECONDS")
            if env_chunk_seconds:
                try:
                    chunk_seconds = int(env_chunk_seconds)
                except ValueError:
                    pass

            if chunk_enabled and chunk_seconds > 0:
                chunk_dir = output_dir / f"chunks_{stamp}"
                chunk_audios = split_audio(audio_path, chunk_dir, chunk_seconds)
                chunk_videos = []
                for idx, chunk_audio in enumerate(chunk_audios, start=1):
                    chunk_video = output_dir / f"chunk_{stamp}_{idx:03d}.mp4"
                    run_echomimic(
                        echomimic_dir=self.config["echo_mimic_dir"],
                        weights_dir=self.config["echo_mimic_weights"],
                        image_path=prepared_image,
                        audio_path=chunk_audio,
                        out_path=chunk_video,
                        ref_video=inputs.reference_video,
                    )
                    chunk_videos.append(chunk_video)

                concat_list = output_dir / f"concat_{stamp}.txt"
                concat_list.write_text(
                    "\n".join([f"file '{p.resolve().as_posix()}'" for p in chunk_videos]),
                    encoding="utf-8",
                )
                ffmpeg_path = self.config.get("ffmpeg_path", "ffmpeg")
                subprocess.run(
                    [
                        ffmpeg_path,
                        "-y",
                        "-f",
                        "concat",
                        "-safe",
                        "0",
                        "-i",
                        str(concat_list),
                        "-c",
                        "copy",
                        str(video_path),
                    ],
                    check=True,
                )
            else:
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
