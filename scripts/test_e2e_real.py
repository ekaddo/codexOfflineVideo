from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.pipeline import AvatarPipeline, PipelineInputs


def main() -> None:
    os.environ.pop("CODEXOFFLINEVIDEO_DUMMY", None)
    os.environ["CODEXOFFLINEVIDEO_ECHOMIMIC_MAX_FRAMES"] = "48"
    os.environ["CODEXOFFLINEVIDEO_ECHOMIMIC_STEPS"] = "15"

    avatar = Path(r"I:\dev\codex\codexOfflineVideo\EchoMimic\assets\test_imgs\a.png")
    voice = Path(r"I:\dev\codex\codexOfflineVideo\EchoMimic\assets\test_audios\echomimic_en.wav")

    script = (
        "Hello! This is a short end to end test for the RealTalk avatar pipeline. "
        "We are verifying TTS generation and EchoMimic rendering."
    )

    pipeline = AvatarPipeline()
    outputs = pipeline.run(
        PipelineInputs(
            avatar_image=avatar,
            script_text=script,
            voice_sample=voice,
            reference_video=None,
        )
    )

    print("E2E real render complete:", outputs.video_path)


if __name__ == "__main__":
    main()
