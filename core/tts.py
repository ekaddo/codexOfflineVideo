from __future__ import annotations

from pathlib import Path


def generate_tts(text: str, speaker_wav: str | Path, out_wav: str | Path, model_name: str, language: str = "en") -> Path:
    try:
        from TTS.api import TTS
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "Coqui TTS is not installed. Install with: pip install TTS"
        ) from exc

    if not text.strip():
        raise ValueError("Text is empty")

    speaker_wav = str(speaker_wav)
    out_wav = Path(out_wav)
    out_wav.parent.mkdir(parents=True, exist_ok=True)

    tts = TTS(model_name=model_name, progress_bar=False, gpu=True)
    tts.tts_to_file(text=text, speaker_wav=speaker_wav, language=language, file_path=str(out_wav))
    return out_wav
