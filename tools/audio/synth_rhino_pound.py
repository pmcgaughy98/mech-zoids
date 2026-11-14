#!/usr/bin/env python3
"""Placeholder rhino ground pound sounds, synthesised from scratch (free, local, no samples).

Two files, because the kit signals two moments:
  pound_rear.wav  when ground pound starts (the rhino rears up): a hydraulic servo climbing
  pound_slam.wav  on the slam frame (the kit's impact signal): thump, crunch, hull clang,
                  falling debris and a rumble tail
These are stand-ins that prove the pipeline. Better takes (ElevenLabs sound effects or a library)
replace these files under the same names; nothing else has to change.
Run from the project folder: python tools/audio/synth_rhino_pound.py
"""
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000
OUT = Path(__file__).resolve().parents[2] / "audio" / "sfx" / "rhino"
rng = np.random.default_rng(7)


def axis(seconds):
    return np.arange(int(SR * seconds)) / SR


def bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], "bandpass", fs=SR, output="sos"), x)


def lp(x, f):
    return sosfilt(butter(2, f, "lowpass", fs=SR, output="sos"), x)


def hp(x, f):
    return sosfilt(butter(2, f, "highpass", fs=SR, output="sos"), x)


def place(buf, x, at):
    i = int(at * SR)
    n = min(len(x), len(buf) - i)
    buf[i:i + n] += x[:n]


def finish(x, peak_db, drive=2.0, fade=0.05):
    x = x / np.max(np.abs(x))
    x = np.tanh(drive * x) / np.tanh(drive)  # soft saturation glues the layers
    n = int(fade * SR)
    x[-n:] *= np.linspace(1, 0, n)
    return x / np.max(np.abs(x)) * 10 ** (peak_db / 20)


def clunk(ms=12, cutoff=1800):
    k = int(ms / 1000 * SR)
    return lp(rng.standard_normal(k), cutoff) * np.exp(-np.arange(k) / (0.25 * k))


def rear():
    t = axis(0.5)
    f = 130 * (380 / 130) ** np.clip(t / 0.42, 0, 1)  # servo pitch climbs as the body lifts
    phase = np.cumsum(f) / SR
    saw = 2 * (phase % 1.0) - 1
    sub = np.sign(np.sin(np.pi * phase))  # square wave an octave down
    env = np.minimum(1, t / 0.03) * np.where(t > 0.42, np.exp(-(t - 0.42) / 0.03), 1)
    x = bp(saw + 0.4 * sub, 200, 2600) * env
    x += hp(rng.standard_normal(len(t)), 3500) * 0.18 * np.minimum(1, t / 0.2) * env  # pneumatic hiss
    place(x, clunk() * 1.5, 0.0)    # locks release
    place(x, clunk(9, 2600), 0.41)  # joints lock at the top
    return finish(x, -7.0, drive=1.5)


def slam():
    dur = 1.7
    t = axis(dur)
    x = np.zeros_like(t)
    # 1. sub thump: a sine that drops from 72 to 33 Hz as it decays
    f = 33 + 39 * np.exp(-t / 0.06)
    x += np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.30)
    # 2. crunch: a burst of low noise, plates hitting stone, plus a sharp click on contact
    x += 0.8 * lp(rng.standard_normal(len(t)), 1600) * np.exp(-t / 0.06)
    k = int(0.004 * SR)
    x[:k] += rng.standard_normal(k) * np.linspace(1, 0, k) * 0.9
    # 3. hull clang: inharmonic partials of struck steel plate; the high ones die first
    for i, (fr, tau) in enumerate([(187, 0.70), (341, 0.55), (523, 0.45), (781, 0.36),
                                   (1163, 0.27), (1709, 0.19), (2477, 0.13)]):
        for detune in (1.0, 1.004):  # a close pair beats like a real plate
            x += (0.18 / (i + 1) ** 0.5 * np.exp(-t / tau) * np.minimum(1, t / 0.002)
                  * np.sin(2 * np.pi * fr * detune * t + rng.uniform(0, 2 * np.pi)))
    # 4. debris: stones and bolts landing, thinning out
    for _ in range(46):
        at = 0.08 + rng.exponential(0.25)
        if at > dur - 0.1:
            continue
        n = int(rng.uniform(0.002, 0.008) * SR)
        lo = rng.uniform(1200, 3000)
        grain = bp(rng.standard_normal(n) * np.exp(-np.arange(n) / (n / 3)), lo, min(lo * 2.2, 9000))
        place(x, grain * rng.uniform(0.15, 0.45) * np.exp(-at / 0.6), at)
    # 5. rumble tail: brown noise under 150 Hz, the ground settling
    r = lp(hp(np.cumsum(rng.standard_normal(len(t))), 20), 150)
    x += 0.5 * r / np.max(np.abs(r)) * np.exp(-t / 0.55) * np.minimum(1, t / 0.02)
    return finish(x, -2.0)


def save(name, x):
    OUT.mkdir(parents=True, exist_ok=True)
    wavfile.write(OUT / name, SR, (x * 32767).astype(np.int16))
    print(f"audio/sfx/rhino/{name}  {len(x) / SR:.2f} s")


if __name__ == "__main__":
    save("pound_rear.wav", rear())
    save("pound_slam.wav", slam())
