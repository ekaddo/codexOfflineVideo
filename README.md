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
- Built-in presenter presets with composited backgrounds (News Anchor, Corporate Presenter, Teacher, Coach)

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

### Presenter Presets + Background Compositing
Presets control framing, background style, and layout for “news anchor” or “corporate presenter” looks.
- Default preset in `config.json`: `preset` (`news_anchor`, `corporate_presenter`, `teacher`, `coach`, `podcast_closeup`, `ceo_keynote`, or `none`)
- Optional custom background image: `preset_background`
 - Composition settings: `composition.encoder`, `composition.preset`, `composition.crf`

For GPU encoding on NVIDIA, set `composition.encoder` to `h264_nvenc` and a NVENC preset like `p4`.

The GUI includes a preset dropdown and optional background image picker.

### EchoMimic Runtime Controls
These environment variables let you cap runtime for quick previews:
- `CODEXOFFLINEVIDEO_ECHOMIMIC_MAX_FRAMES` (e.g., `48`)
- `CODEXOFFLINEVIDEO_ECHOMIMIC_STEPS` (e.g., `15`)

### Long-Form Chunking (6-Minute Segments)
The pipeline can split long audio into 6-minute chunks and stitch the video back together.
- Set in `config.json` under `chunking.chunk_seconds` (default `360`)
- Override per run with `CODEXOFFLINEVIDEO_CHUNK_SECONDS`

## Notes
- If XTTS is not installed, the app will prompt you to install it.
- EchoMimic runs as a subprocess; keep it on a fast SSD.
- Outputs are saved in `outputs/` with timestamps.
