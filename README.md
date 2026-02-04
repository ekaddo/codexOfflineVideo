# codexOfflineVideo (RealTalk: Talking Avatar Creator ULTIMATE)

A Windows desktop application for generating photorealistic talking avatar videos offline using EchoMimic and XTTS v2.

This repo is scaffolded to run on the target machine in the provided Belarc profile:
- Windows 11 Enterprise 25H2
- Intel i7-10700
- 128 GB RAM
- NVIDIA RTX 4060 Ti

The app uses a Tkinter GUI and a Python pipeline that can call EchoMimic and Coqui TTS when installed locally.

## Key Features (Pipeline-Ready)
- High-fidelity avatar animation via EchoMimic (AAAI 2025)
- Voice cloning with Coqui XTTS v2
- Motion cloning via optional reference video
- Auto-smart cropping to 512x512 to avoid tensor size issues
- Tkinter desktop GUI (no CLI required)
- Optional LTX-2 renderer mode (not default; ≤30s clips; separate flag)

## What’s Included
- `avatar_app_ultimate.py`: Tkinter GUI
- `core/`: pipeline modules for image prep, TTS, and EchoMimic invocation
- `outputs/`: generated videos
- `config.json`: local paths and defaults
- `build_exe.ps1`: PyInstaller build script

## Quick Start (Python 3.11)
1. Create and activate a venv
```powershell
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies
```powershell
pip install -r requirements.txt
```

3. Install PyTorch (CUDA 11.8 example)
```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

4. Install EchoMimic and weights (outside this repo recommended)
```powershell
git clone https://github.com/BadToBest/EchoMimic ..\EchoMimic
cd ..\EchoMimic
git lfs install
git clone https://huggingface.co/BadToBest/EchoMimic pretrained_weights
cd -
```

5. (Optional) Install Coqui TTS for voice cloning
```powershell
pip install TTS
```

6. Run the app
```powershell
python avatar_app_ultimate.py
```

## Build Windows EXE
```powershell
.\build_exe.ps1
```
The output will be in `dist/`.

## Configuration
Edit `config.json` to point to your local EchoMimic repo and weights. The app will also read:
- `ECHO_MIMIC_DIR`
- `ECHO_MIMIC_WEIGHTS`
- `FFMPEG_PATH`

### LTX-2 (Optional, Never Default)
The LTX-2 renderer is intended for experimental “HQ Intro Mode” only:
- Separate engine flag
- ≤30 second clips
- Never the default renderer

This repo wires LTX-2 as an optional external renderer via `engine.ltx.command`. LTX-2 has a separate, stricter runtime stack: the official docs note Python >= 3.12, CUDA > 12.7, and PyTorch ~= 2.7.

Quick start (from the official LTX-2 repo) uses `uv` to create its environment and requires downloading model weights.

Configure `engine.ltx` in `config.json` like this (replace placeholders with your actual LTX-2 CLI/module):
```json
{
  "engine": {
    "ltx": {
      "enabled": true,
      "duration_seconds": 10,
      "command": [
        "C:\\\\path\\\\to\\\\ltx-venv\\\\Scripts\\\\python.exe",
        "-m",
        "<ltx_cli_module>",
        "--prompt",
        "{prompt}",
        "--output",
        "{out_path}",
        "--duration",
        "{duration}",
        "--image",
        "{image_path}"
      ],
      "workdir": "C:\\\\path\\\\to\\\\LTX-2"
    }
  }
}
```

Notes:
- LTX-2 mode uses the Script text as the prompt. Voice sample is ignored.
- If you provide an avatar image, it will be cropped and passed as `{image_path}`.

## Notes
- If XTTS is not installed, the app will prompt you to install it.
- EchoMimic runs as a subprocess; keep it on a fast SSD.
- Outputs are saved in `outputs/` with timestamps.
