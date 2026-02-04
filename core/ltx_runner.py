from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Iterable


def run_ltx_command(
    command: Iterable[str],
    prompt: str,
    out_path: str | Path,
    image_path: str | Path | None = None,
    duration_seconds: int | None = None,
    workdir: str | Path | None = None,
) -> Path:
    if not command:
        raise RuntimeError(
            "LTX-2 command is not configured. Set engine.ltx.command in config.json."
        )

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    replacements = {
        "{prompt}": prompt,
        "{out_path}": str(out_path),
        "{image_path}": "" if image_path is None else str(image_path),
        "{duration}": "" if duration_seconds is None else str(duration_seconds),
    }

    resolved = []
    for token in command:
        for key, value in replacements.items():
            token = token.replace(key, value)
        if token != "":
            resolved.append(token)

    env = os.environ.copy()
    subprocess.run(resolved, check=True, cwd=str(workdir) if workdir else None, env=env)
    return out_path
