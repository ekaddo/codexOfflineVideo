from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import os
import subprocess

import soundfile as sf

from .audio_utils import split_audio
from .config import load_config
from .compositing import compose_video
from .dummy_renderer import generate_dummy_audio, generate_dummy_image, generate_dummy_video
from .echomimic import run_echomimic
from .image_utils import prepare_avatar_image
from .presets import get_preset, render_background, resolve_preset_key
from .tts import generate_tts


@dataclass
class PipelineInputs:
    avatar_image: Path
    script_text: str
    voice_sample: Path
    reference_video: Path | None = None
    preset_name: str | None = None
    background_image: Path | None = None


@dataclass
class PipelineOutputs:
    audio_path: Path
    image_path: Path
    video_path: Path
    raw_video_path: Path | None = None
    composed_video_path: Path | None = None


class AvatarPipeline:
    def __init__(self, config_path: str | Path = "config.json"):
        self.config = load_config(config_path)

    def run(self, inputs: PipelineInputs) -> PipelineOutputs:
        output_dir = Path(self.config["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)

        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prepared_image = output_dir / f"avatar_{stamp}.png"
        audio_path = output_dir / f"audio_{stamp}.wav"
        raw_video_path = output_dir / f"raw_{stamp}.mp4"
        final_video_path = output_dir / f"generated_{stamp}.mp4"

        if os.environ.get("CODEXOFFLINEVIDEO_DUMMY", "0") == "1":
            duration = min(30.0, max(3.0, len(inputs.script_text) / 15))
            dummy_image = generate_dummy_image(prepared_image, size=self.config.get("image_size", 512))
            dummy_audio = generate_dummy_audio(audio_path, duration_seconds=duration)
            generate_dummy_video(
                image_path=dummy_image,
                audio_path=dummy_audio,
                out_path=raw_video_path,
                ffmpeg_path=self.config.get("ffmpeg_path", "ffmpeg"),
            )
        else:
            # Prepare image
            preset_key = _resolve_preset_key(inputs.preset_name, self.config.get("preset"))
            preset = get_preset(preset_key)
            prepare_avatar_image(
                inputs.avatar_image,
                prepared_image,
                size=self.config.get("image_size", 512),
                focus_y=preset.crop_focus_y if preset else None,
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
                        str(raw_video_path),
                    ],
                    check=True,
                )
            else:
                run_echomimic(
                    echomimic_dir=self.config["echo_mimic_dir"],
                    weights_dir=self.config["echo_mimic_weights"],
                    image_path=prepared_image,
                    audio_path=audio_path,
                    out_path=raw_video_path,
                    ref_video=inputs.reference_video,
                )

        preset_key = _resolve_preset_key(inputs.preset_name, self.config.get("preset"))
        preset = get_preset(preset_key)
        if preset:
            background_override = inputs.background_image
            if not background_override:
                configured_bg = self.config.get("preset_background", "").strip()
                if configured_bg:
                    background_override = Path(configured_bg)
            bg_path = render_background(preset, output_dir / "presets", background_override)
            duration_sec = None
            try:
                duration_sec = float(sf.info(str(audio_path)).duration)
            except Exception:
                duration_sec = None
            compose_video(
                background_path=bg_path,
                avatar_video_path=raw_video_path,
                out_path=final_video_path,
                preset=preset,
                ffmpeg_path=self.config.get("ffmpeg_path", "ffmpeg"),
                duration_seconds=duration_sec,
                encoder=self.config.get("composition", {}).get("encoder", "libx264"),
                preset_speed=self.config.get("composition", {}).get("preset", "veryfast"),
                crf=int(self.config.get("composition", {}).get("crf", 23)),
            )
            composed_path = final_video_path
        else:
            if raw_video_path != final_video_path:
                final_video_path = raw_video_path
            composed_path = None

        return PipelineOutputs(
            audio_path=audio_path,
            image_path=prepared_image,
            video_path=final_video_path,
            raw_video_path=raw_video_path,
            composed_video_path=composed_path,
        )


def _resolve_preset_key(input_value: str | None, default_value: str | None) -> str | None:
    if input_value and input_value.strip().lower() in {"none", "off", "raw"}:
        return None
    if default_value and str(default_value).strip().lower() in {"none", "off", "raw"}:
        default_value = None
    return resolve_preset_key(input_value) or resolve_preset_key(default_value) or default_value
