from __future__ import annotations

import os
import sys
from pathlib import Path
import shutil
import wave
import math

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.pipeline import AvatarPipeline, PipelineInputs
from core.presets import list_presets


def make_dummy_avatar(path: Path) -> Path:
    size = 768
    img = Image.new("RGB", (size, size), (16, 20, 28))
    draw = ImageDraw.Draw(img)
    draw.ellipse((200, 160, 560, 600), fill=(60, 110, 220))
    draw.rectangle((260, 520, 500, 720), fill=(30, 40, 60))
    draw.text((260, 720 - 40), "Preset Preview", fill=(230, 235, 245))
    img.save(path)
    return path


def make_dummy_voice(path: Path, seconds: float = 2.0, freq: float = 220.0) -> Path:
    rate = 44100
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        for i in range(int(rate * seconds)):
            t = i / rate
            sample = 0.2 * math.sin(2 * math.pi * freq * t)
            wf.writeframes(int(sample * 32767).to_bytes(2, byteorder="little", signed=True))
    return path


def main() -> None:
    os.environ["CODEXOFFLINEVIDEO_DUMMY"] = "1"

    out_dir = ROOT / "outputs" / "preset_previews"
    out_dir.mkdir(parents=True, exist_ok=True)

    avatar = make_dummy_avatar(out_dir / "avatar.png")
    voice = make_dummy_voice(out_dir / "voice.wav")
    script = "Preset preview render for layout verification."

    pipeline = AvatarPipeline()
    rendered = []
    for preset in list_presets():
        outputs = pipeline.run(
            PipelineInputs(
                avatar_image=avatar,
                script_text=script,
                voice_sample=voice,
                reference_video=None,
                preset_name=preset.key,
                background_image=None,
            )
        )
        final_path = out_dir / f"preview_{preset.key}.mp4"
        shutil.copy2(outputs.video_path, final_path)
        rendered.append(final_path)

    print("Rendered previews:")
    for path in rendered:
        print(path)


if __name__ == "__main__":
    main()
