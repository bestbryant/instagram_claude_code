"""A short, original ambient pad for each Reel (no licensing to worry about)."""
from __future__ import annotations

import wave

import numpy as np

SR = 48000

CHORDS = [[0, 7, 12, 16, 19], [0, 7, 12, 15, 19], [0, 5, 12, 14, 19], [0, 7, 14, 16, 21], [0, 3, 10, 15, 19]]
PENTA = [0, 2, 4, 7, 9, 12, 14]


def _lowpass(x, cutoff):
    spec = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(len(x), 1 / SR)
    spec *= 1 / (1 + (freqs / cutoff) ** 4)
    return np.fft.irfft(spec, len(x))


def _reverb(x, rng, seconds=2.8):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ir = np.stack([_lowpass(rng.normal(0, 1, n), 5000) * np.exp(-t / 0.9) for _ in range(2)], 1)
    ir /= np.abs(ir).sum(0) ** 0.5 * 30
    size = 1 << int(np.ceil(np.log2(len(x) + n)))
    out = np.zeros((len(x), 2))
    for c in range(2):
        y = np.fft.irfft(np.fft.rfft(x[:, c], size) * np.fft.rfft(ir[:, c], size), size)
        out[:, c] = y[:len(x)]
    return out


def ambient(seconds: float, seed: int, path: str) -> str:
    rng = np.random.default_rng(seed & 0xFFFFFFFF)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    root = 98.0 * 2 ** (int(rng.integers(0, 9)) / 12)
    chord = CHORDS[int(rng.integers(0, len(CHORDS)))]
    sig = np.zeros((n, 2))
    for k, semi in enumerate(chord):
        f = root * 2 ** (semi / 12)
        for det, pan in ((-0.18, 0.25), (0.18, 0.75)):
            ph = rng.uniform(0, 2 * np.pi)
            lfo = 0.55 + 0.45 * np.sin(2 * np.pi * (0.04 + 0.025 * k) * t + ph)
            w = np.sin(2 * np.pi * (f + det) * t + ph) + 0.2 * np.sin(2 * np.pi * 2 * (f + det) * t + ph)
            amp = 0.1 / (1 + 0.4 * k) * lfo
            sig[:, 0] += w * amp * (1 - pan)
            sig[:, 1] += w * amp * pan

    # a few soft bell notes
    for _ in range(int(rng.integers(5, 9))):
        start = rng.uniform(0.8, seconds - 2.5)
        f = root * 4 * 2 ** (PENTA[int(rng.integers(0, len(PENTA)))] / 12)
        dt = np.clip(t - start, 0, None)
        env = (t >= start) * np.exp(-dt / 1.4) * (1 - np.exp(-dt / 0.01))
        w = (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-dt / 0.3)) * env * 0.05
        p = rng.uniform(0.2, 0.8)
        sig[:, 0] += w * (1 - p)
        sig[:, 1] += w * p

    # wind
    wind = _lowpass(rng.normal(0, 1, n), 380)
    wind *= (0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * t + rng.uniform(0, 6))) * 0.06 / (np.abs(wind).max() + 1e-9)
    sig += wind[:, None]

    sig = sig * 0.55 + _reverb(sig, rng) * 0.9
    fade = np.minimum(1, t / 1.5) * np.minimum(1, (seconds - t) / 2.0)
    sig *= fade[:, None]
    sig *= 0.5 / (np.abs(sig).max() + 1e-9)

    pcm = (np.clip(sig, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes(pcm.tobytes())
    return path
