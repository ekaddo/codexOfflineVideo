from __future__ import annotations

from pathlib import Path
import re

import soundfile as sf

from .presets import Preset


def build_karaoke_ass(
    script_text: str,
    audio_path: str | Path,
    preset: Preset,
    out_path: str | Path,
) -> Path | None:
    if not script_text.strip() or preset.content_box is None:
        return None

    words = _tokenize(script_text)
    if not words:
        return None

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    duration = float(sf.info(str(audio_path)).duration)
    if duration <= 0:
        return None

    x, y, w, _h = preset.content_box
    video_w, video_h = preset.resolution
    margin_l = max(20, x + 20)
    margin_r = max(20, video_w - (x + w) + 20)
    margin_v = max(20, y + 20)

    weights = [_weight_word(word) for word in words]
    total_weight = max(1e-6, sum(weights))
    durations = [duration * (w_i / total_weight) for w_i in weights]

    lines_per_event = 3
    words_per_line = 7
    words_per_event = lines_per_event * words_per_line

    events = []
    t = 0.0
    for idx in range(0, len(words), words_per_event):
        chunk_words = words[idx : idx + words_per_event]
        chunk_durations = durations[idx : idx + words_per_event]
        start = t
        end = t + sum(chunk_durations)
        t = end
        text = _build_karaoke_chunk(chunk_words, chunk_durations, words_per_line=words_per_line)
        events.append((start, end, text))

    ass = _render_ass(
        events=events,
        width=video_w,
        height=video_h,
        margin_l=margin_l,
        margin_r=margin_r,
        margin_v=margin_v,
    )
    out_path.write_text(ass, encoding="utf-8")
    return out_path


def _tokenize(text: str) -> list[str]:
    text = text.replace("\n", " ")
    tokens = [tok for tok in re.split(r"\s+", text) if tok]
    return tokens


def _weight_word(word: str) -> float:
    alpha = re.sub(r"[^A-Za-z0-9]", "", word)
    base = max(1.0, len(alpha) * 0.35)
    if re.search(r"[.,;:!?]$", word):
        base += 0.8
    return base


def _build_karaoke_chunk(words: list[str], durations: list[float], words_per_line: int) -> str:
    parts = []
    for i, (word, dur) in enumerate(zip(words, durations)):
        centis = max(1, int(round(dur * 100)))
        safe_word = _escape_ass_text(word)
        parts.append(r"{\kf" + str(centis) + "}" + safe_word)
        if (i + 1) % words_per_line == 0 and i != len(words) - 1:
            parts.append(r"\N")
        else:
            parts.append(" ")
    return "".join(parts).strip()


def _escape_ass_text(text: str) -> str:
    return text.replace("\\", r"\\").replace("{", "(").replace("}", ")")


def _fmt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def _render_ass(
    events: list[tuple[float, float, str]],
    width: int,
    height: int,
    margin_l: int,
    margin_r: int,
    margin_v: int,
) -> str:
    lines = []
    lines.append("[Script Info]")
    lines.append("ScriptType: v4.00+")
    lines.append(f"PlayResX: {width}")
    lines.append(f"PlayResY: {height}")
    lines.append("WrapStyle: 2")
    lines.append("ScaledBorderAndShadow: yes")
    lines.append("")
    lines.append("[V4+ Styles]")
    lines.append(
        "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,"
        "Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,"
        "Alignment,MarginL,MarginR,MarginV,Encoding"
    )
    lines.append(
        f"Style: Speech,Segoe UI,40,&H00FFFFFF,&H0010B8FF,&H00202020,&H64000000,"
        f"0,0,0,0,100,100,0,0,1,2,1,7,{margin_l},{margin_r},{margin_v},1"
    )
    lines.append("")
    lines.append("[Events]")
    lines.append("Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text")
    for start, end, text in events:
        lines.append(
            "Dialogue: 0,"
            + _fmt_time(start)
            + ","
            + _fmt_time(end)
            + ",Speech,,0,0,0,,"
            + text
        )
    lines.append("")
    return "\n".join(lines)
