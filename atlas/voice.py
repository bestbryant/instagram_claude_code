"""The cartographer's voice: each line of a story Reel read aloud, offline (Kokoro TTS).

The model (about 330 MB) is downloaded once into ATLAS_TTS_DIR (default ~/.cache/atlas-tts),
never into the repo. Each spoken line is cached there too, so re-renders don't re-synthesise.
"""
from __future__ import annotations

import hashlib
import os
import re
import urllib.request
from pathlib import Path

import numpy as np

SR = 48000                       # the Reel's audio rate (Kokoro speaks at 24 kHz)
VOICE = "bf_emma"                # dry, British, unhurried: the cartographer
SPEED = 0.94
LANG = "en-gb"
VERSION = 1                      # bump to re-synthesise every cached line
DIR = Path(os.environ.get("ATLAS_TTS_DIR", Path.home() / ".cache" / "atlas-tts"))
HF = "https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX/resolve/main"

_kokoro = None


def _fetch(url: str, path: Path):
    tmp = path.with_suffix(path.suffix + ".part")
    with urllib.request.urlopen(url, timeout=120) as r, open(tmp, "wb") as f:
        while chunk := r.read(1 << 20):
            f.write(chunk)
    os.replace(tmp, path)


def _model():
    global _kokoro
    if _kokoro is None:
        from kokoro_onnx import Kokoro
        DIR.mkdir(parents=True, exist_ok=True)
        model, voices = DIR / "model.onnx", DIR / "voices.npz"
        if not model.exists():
            _fetch(f"{HF}/onnx/model.onnx", model)
        if not voices.exists():
            raw = DIR / f"{VOICE}.bin"
            _fetch(f"{HF}/voices/{VOICE}.bin", raw)
            np.savez(voices, **{VOICE: np.fromfile(raw, dtype=np.float32).reshape(510, 1, 256)})
        _kokoro = Kokoro(str(model), str(voices))
    return _kokoro


def spoken(text: str) -> str:
    """What the narrator says for an on-screen line: one sentence flow, no line breaks."""
    s = re.sub(r"\s*\n\s*", " ", text).strip()
    s = s.replace("…", "...")
    if s and s[-1] not in ".!?'\"’”":
        s += "."
    return s


def _upsample2(x: np.ndarray) -> np.ndarray:
    """24 kHz -> 48 kHz, band-limited (zero-padded spectrum)."""
    n = len(x)
    X = np.fft.rfft(x)
    Y = np.zeros(n + 1, complex)
    Y[:len(X)] = X
    return np.fft.irfft(Y, 2 * n) * 2


def line(text: str) -> np.ndarray:
    """The line read aloud: mono float32 at 48 kHz, peak 0.9, trimmed of silence at both ends."""
    s = spoken(text)
    if not s:
        return np.zeros(0, np.float32)
    key = hashlib.sha1(f"{VERSION}|{VOICE}|{SPEED}|{LANG}|{s}".encode()).hexdigest()[:16]
    cache = DIR / "lines" / f"{key}.npy"
    if cache.exists():
        return np.load(cache)
    audio, sr = _model().create(s, voice=VOICE, speed=SPEED, lang=LANG)
    a = np.asarray(audio, np.float64)
    if sr == 24000:
        a = _upsample2(a)
    elif sr != SR:
        a = np.interp(np.linspace(0, len(a) - 1, int(len(a) * SR / sr)), np.arange(len(a)), a)
    loud = np.flatnonzero(np.abs(a) > 0.01)
    if len(loud):
        a = a[max(0, loud[0] - int(0.02 * SR)):loud[-1] + int(0.08 * SR)]
    a = (a * 0.9 / (np.abs(a).max() + 1e-9)).astype(np.float32)
    cache.parent.mkdir(parents=True, exist_ok=True)
    np.save(cache, a)
    return a


def seconds(text: str) -> float:
    return len(line(text)) / SR


def available() -> bool:
    try:
        import kokoro_onnx  # noqa: F401
        return True
    except ImportError:
        return False
