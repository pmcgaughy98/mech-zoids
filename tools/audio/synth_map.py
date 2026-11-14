#!/usr/bin/env python3
"""Map sounds for the MOBA map, synthesised from scratch (free, local, no samples).

Ambient beds, seamless loops played by MapAudio at the map's markers (audio/ambience/<zone>.ogg).
The "foundry" set (default; Preston picked the Foundry map look, industrial dusk, 2026-11-04):
  lane    wind working the corrugated walls, the plant droning far off, cooling sheet metal ticking, a far clank
  jungle  the machine yards: a drop forge and a press out of step, a conveyor, steam vents, chain, transformer buzz
  plaza   furnaces roaring past the cliffs, wind, the steel frame creaking and booming as it cools
  stream  a runoff channel: water down concrete, a drain gurgling, a pump hum, drips off the channel walls
  base    the core's plant: a throbbing generator, a turbine whine, cooling fans, pneumatic hiss, crackle
The first "wild" set (wind, insects, birds, water) is kept: --theme wild.
Match events, one-shots (audio/sfx/map/<name>.wav):
  tower_shot, tower_hit, tower_down, core_down, wave_spawn, minion_hit, camp_aggro,
  respawn, recall_start, recall_arrive, win, lose
These are stand-ins: a better take replaces a file under the same name and nothing else changes.
Run from the project folder: python tools/audio/synth_map.py
"""
import re
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000
ROOT = Path(__file__).resolve().parents[2]
BEDS = ROOT / "audio" / "ambience"
EVENTS = ROOT / "audio" / "sfx" / "map"
rng = np.random.default_rng(11)


# ---------- building blocks ----------
def axis(sec):
    return np.arange(int(SR * sec)) / SR


def white(n):
    return rng.standard_normal(n)


def pink(n):
    spec = np.fft.rfft(white(n))
    f = np.fft.rfftfreq(n, 1 / SR)
    spec[1:] /= np.sqrt(f[1:])
    spec[0] = 0
    x = np.fft.irfft(spec, n)
    return x / np.max(np.abs(x))


def brown(n):
    x = hp(np.cumsum(white(n)), 15)
    return x / np.max(np.abs(x))


def _sos(kind, f):
    return butter(2, f, kind, fs=SR, output="sos")


def lp(x, f):
    return sosfilt(_sos("lowpass", f), x)


def hp(x, f):
    return sosfilt(_sos("highpass", f), x)


def bp(x, lo, hi):
    return sosfilt(_sos("bandpass", [lo, hi]), x)


def osc(freq, n, shape="sin"):
    """freq: number or per-sample array. shape: sin, saw or square."""
    f = np.broadcast_to(np.asarray(freq, dtype=float), (n,))
    ph = np.cumsum(f) / SR
    if shape == "saw":
        return 2 * (ph % 1.0) - 1
    if shape == "square":
        return np.sign(np.sin(2 * np.pi * ph))
    return np.sin(2 * np.pi * ph)


def lfo(t, hz, depth, phase=0.0):
    return 1 - depth + depth * (0.5 + 0.5 * np.sin(2 * np.pi * hz * t + phase))


def place(buf, x, at):
    i = int(at * SR)
    if i >= len(buf):
        return
    n = min(len(x), len(buf) - i)
    buf[i:i + n] += x[:n]


def ping(freqs, taus, sec, amps=None):
    """Struck-metal partials: inharmonic sines with their own decay."""
    t = axis(sec)
    amps = amps or [1 / (i + 1) ** 0.5 for i in range(len(freqs))]
    out = np.zeros_like(t)
    for f, tau, a in zip(freqs, taus, amps):
        out += a * np.sin(2 * np.pi * f * t + rng.uniform(0, 2 * np.pi)) * np.exp(-t / tau)
    return out * np.minimum(1, t / 0.002)


def burst(sec, lo, hi, tau):
    t = axis(sec)
    return bp(white(len(t)), lo, hi) * np.exp(-t / tau)


def brass(freq, sec, bright=0.6):
    """A synth horn note: detuned saws, dark body plus a bright layer that fades after the attack."""
    t = axis(sec)
    n = len(t)
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.2 * t) * np.minimum(1, t / 0.3)
    saw = osc(freq * vib, n, "saw") + osc(freq * 1.004 * vib, n, "saw") + 0.5 * osc(freq / 2 * vib, n, "saw")
    env = np.minimum(1, t / 0.04) * np.minimum(1, (sec - t) / 0.25)
    body = lp(saw, 900) * env
    shine = lp(saw, 3200) * env * (np.exp(-t / 0.25) * bright + 0.15)
    return body + shine


def finish(x, peak_db=-1.0, drive=1.5, fade=0.03):
    x = x / np.max(np.abs(x))
    x = np.tanh(drive * x) / np.tanh(drive)
    k = int(fade * SR)
    x[-k:] *= np.linspace(1, 0, k)
    return x / np.max(np.abs(x)) * 10 ** (peak_db / 20)


def loop(x, sec, xfade=2.0, rms_db=-24.0):
    """Cut a seamless loop of `sec` from x (which runs `xfade` longer): the tail is crossfaded into
    the head with equal power, so the end flows straight back into the start."""
    n, k = int(sec * SR), int(xfade * SR)
    out = x[:n].copy()
    a = np.linspace(0, np.pi / 2, k)
    out[:k] = x[:k] * np.sin(a) + x[n:n + k] * np.cos(a)
    out *= 10 ** (rms_db / 20) / np.sqrt(np.mean(out ** 2))
    peak = np.max(np.abs(out))
    return out * (0.9 / peak if peak > 0.9 else 1.0)


# ---------- ambient beds, first "wild" set (16 s loops; the foundry set below replaced it) ----------
LEN, XF = 16.0, 2.0
T = axis(LEN + XF)
N = len(T)


def wild_lane():
    wind = bp(pink(N), 200, 1800) * lfo(T, 0.07, 0.5) * lfo(T, 0.19, 0.3, 1.0)
    drone = sum(a * osc(f, N) for f, a in [(41, 1.0), (82.3, 0.6), (123.1, 0.35)]) * lfo(T, 0.05, 0.3)
    x = 1.0 * wind + 0.12 * drone
    for at in rng.uniform(0.5, LEN, 4):  # distant clanks, dulled by distance
        place(x, 0.06 * lp(ping([310, 527, 845], [0.5, 0.35, 0.2], 1.0), 1500), at)
    return loop(x, LEN, XF, -24)


def wild_jungle():
    air = lp(pink(N), 800) * 0.4
    x = air.copy()
    for lo, hi, rate, gate_hz, amp in [(4200, 6500, 28, 0.9, 0.35), (5200, 7800, 34, 0.6, 0.25)]:
        pulse = 0.5 + 0.5 * np.sign(np.sin(2 * np.pi * rate * T))  # cricket pulse
        gate = (np.sin(2 * np.pi * gate_hz * T + rng.uniform(0, 6)) > -0.2).astype(float)
        x += amp * bp(white(N), lo, hi) * lp(pulse * gate, 300)
    for at in np.cumsum(rng.uniform(1.2, 2.8, 12)):  # chirp groups
        for j in range(rng.integers(2, 5)):
            tt = axis(0.08)
            f = np.linspace(2500, 4000, len(tt)) * rng.uniform(0.85, 1.15)
            place(x, 0.12 * osc(f, len(tt)) * np.sin(np.pi * tt / 0.08), at + j * 0.12)
    for at in rng.uniform(0, LEN, 7):  # leaf rustle
        d = rng.uniform(0.3, 0.8)
        tt = axis(d)
        place(x, 0.25 * hp(white(len(tt)), 2500) * np.sin(np.pi * tt / d) ** 2, at)
    x += 0.04 * (osc(120, N) + 0.5 * osc(240, N))  # the jungle is wired: a faint electric hum
    return loop(x, LEN, XF, -26)


def wild_plaza():
    x = 0.6 * bp(pink(N), 150, 1200) * lfo(T, 0.05, 0.6)
    x += 0.05 * sum(osc(f, N) for f in (100, 200, 300))
    for at in np.arange(0.8, LEN + XF, 3.7) + rng.uniform(-0.5, 0.5, len(np.arange(0.8, LEN + XF, 3.7))):
        place(x, 0.18 * lp(ping([97, 163, 241, 389], [2.6, 2.0, 1.4, 0.9], 3.0), 900), at)
    return loop(x, LEN, XF, -25)


def wild_stream():
    flicker = lp(np.abs(white(N)), 8)
    flicker /= np.max(flicker)
    x = 0.7 * bp(pink(N), 300, 3000) * (0.6 + 0.4 * flicker)
    x += 0.4 * lp(brown(N), 200)
    for at in rng.uniform(0, LEN + XF, int(30 * (LEN + XF))):  # bubbles, about 30 a second
        d = rng.uniform(0.015, 0.04)
        tt = axis(d)
        f0 = rng.uniform(400, 1500)
        place(x, rng.uniform(0.03, 0.12) * osc(f0 * (1 + 0.5 * tt / d), len(tt)) * np.exp(-tt / (d / 3)), at)
    return loop(x, LEN, XF, -24)


def wild_base():
    hum = sum(a * (osc(f, N) + osc(f + 0.3, N)) for f, a in [(55, 1.0), (110, 0.7), (165, 0.4), (220, 0.25)])
    buzz = bp(osc(110, N, "square"), 200, 1200) * 0.15
    vent = bp(pink(N), 400, 2500) * 0.35
    x = 0.25 * hum + buzz + vent
    for at in np.cumsum(rng.uniform(4.5, 7.0, 4)):  # pneumatic hiss
        tt = axis(0.6)
        place(x, 0.3 * hp(white(len(tt)), 3000) * np.minimum(1, tt / 0.05) * np.exp(-tt / 0.25), at)
    return loop(x, LEN, XF, -24)


# ---------- ambient beds, foundry set (2026-11-04: Preston picked "Foundry", industrial dusk) ----------
# Each bed has two layers. The noise layer runs LEN + XF and is crossfaded into a loop. The periodic layer is
# exactly LEN long and wraps on itself: its tones sit on a 1/16 Hz grid (a whole number of cycles per loop) and
# its one-shots wrap their tails round to the start, so rhythms like the drop forge never stutter at the seam.
NL = int(LEN * SR)
TL = axis(LEN)


def cyc(buf, x, at):
    """Add x into the periodic layer at `at` seconds, wrapping its tail round to the start."""
    idx = (int(at * SR) + np.arange(len(x))) % len(buf)
    np.add.at(buf, idx, x)


def tones(parts):
    """Sines on the 1/16 Hz grid, so each one runs a whole number of cycles per loop."""
    return sum(a * osc(f, NL) for f, a in parts)


def seam(noise, per, rms_db):
    k = int(XF * SR)
    a = np.linspace(0, np.pi / 2, k)
    out = noise[:NL].copy()
    out[:k] = noise[:k] * np.sin(a) + noise[NL:NL + k] * np.cos(a)
    out += per
    out *= 10 ** (rms_db / 20) / np.sqrt(np.mean(out ** 2))
    peak = np.max(np.abs(out))
    return out * (0.9 / peak if peak > 0.9 else 1.0)


def thump(f0, sec=0.7):
    """A heavy press or drop forge landing: a falling low sine and a short dull crunch."""
    t = axis(sec)
    body = np.sin(2 * np.pi * f0 * t * (1 + 0.8 * np.exp(-t / 0.025))) * np.exp(-t / 0.14)
    return body + 0.35 * lp(burst(sec, 80, 1200, 0.025), 1500)


def creak(f0, f1, sec):
    """Big steel shifting as it cools: a sliding saw buzz with a stick-slip roughness."""
    t = axis(sec)
    r = lp(np.abs(white(len(t))), 35)
    rough = 0.35 + 0.65 * r / np.max(r)
    tone = osc(np.linspace(f0, f1, len(t)), len(t), "saw") * rough
    return bp(tone, 180, 1600) * np.sin(np.pi * t / sec) ** 1.5


def drip(f0):
    """A drip in a concrete channel, with its slap off the walls."""
    t = axis(0.03)
    d = osc(f0 * (1 + 0.6 * t / 0.03), len(t)) * np.exp(-t / 0.008)
    out = np.zeros(int(0.2 * SR))
    for delay, g in [(0.0, 1.0), (0.047, 0.45), (0.094, 0.2), (0.141, 0.08)]:
        place(out, g * d, delay)
    return out


def foundry_lane():
    gust = lfo(T, 0.0625, 0.6) * lfo(T, 0.1875, 0.35, 1.0)
    noise = bp(pink(N), 180, 1600) * gust
    noise += 2.0 * (bp(white(N), 640, 760) + 0.7 * bp(white(N), 1050, 1180)) * gust ** 2  # air over corrugations
    per = 0.09 * tones([(50, 1.0), (100, 0.55), (150, 0.3), (200, 0.12)]) * lfo(TL, 0.125, 0.25)
    for at in rng.uniform(0, LEN, 10):  # sheet metal ticking as it cools
        f = rng.uniform(2200, 4200)
        cyc(per, rng.uniform(0.02, 0.05) * ping([f, f * 1.47], [0.03, 0.018], 0.1), at)
    for at in (3.1, 11.4):  # a heavy clank far down the line
        cyc(per, 0.07 * lp(ping([180, 297, 455, 690], [1.2, 0.9, 0.6, 0.35], 2.0), 1100), at)
    return seam(noise, per, -24)


def foundry_jungle():
    noise = 0.35 * lp(pink(N), 700)
    belt = lp(0.5 + 0.5 * osc(12, N, "square"), 60)  # conveyor chatter
    noise += 0.5 * bp(white(N), 1200, 3500) * belt * lfo(T, 0.0625, 0.7, 2.0)
    per = 0.04 * bp(osc(100, NL, "square"), 150, 900)  # transformer buzz
    for k in range(6):  # the drop forge, six blows a loop
        hit = 0.22 * thump(48, 0.8) + 0.05 * lp(ping([420, 690, 1130], [0.4, 0.3, 0.2], 0.8), 2000)
        cyc(per, hit, 0.4 + k * LEN / 6)
    for k in range(5):  # a lighter press, out of step with it
        cyc(per, 0.12 * thump(70, 0.5), 1.7 + k * LEN / 5)
    for at in (2.3, 7.9, 13.2):  # steam vents
        tt = axis(1.1)
        cyc(per, 0.16 * hp(white(len(tt)), 2500) * np.minimum(1, tt / 0.08) * np.exp(-tt / 0.45), at)
    for at in (5.2, 12.0):  # chain clinks
        for j in range(rng.integers(3, 6)):
            f = rng.uniform(1600, 3000)
            cyc(per, 0.05 * ping([f, f * 1.33], [0.06, 0.04], 0.15), at + j * rng.uniform(0.07, 0.14))
    return seam(noise, per, -26)


def foundry_plaza():
    noise = 0.9 * lp(brown(N), 220) * lfo(T, 0.0625, 0.45)  # furnace roar past the cliffs
    noise += 0.45 * bp(pink(N), 250, 1400) * lfo(T, 0.125, 0.5, 2.0)
    sparks = (white(N) > 3.6).astype(float) * white(N)  # sparse furnace crackle
    noise += 0.5 * bp(sparks, 1500, 6000)
    per = 0.04 * tones([(50, 1.0), (100, 0.6), (150, 0.35)])
    for at, f0, f1, d in [(2.0, 140, 112, 1.6), (9.5, 96, 120, 2.1)]:  # the frame creaking
        cyc(per, 0.12 * creak(f0, f1, d), at)
    for at in (5.6, 13.4):  # hollow booms from the frame
        cyc(per, 0.15 * lp(ping([97, 163, 241, 389], [2.6, 2.0, 1.4, 0.9], 3.0), 800), at)
    return seam(noise, per, -20)  # by LUFS, not RMS: leveled with the other beds


def foundry_stream():
    flicker = lp(np.abs(white(N)), 6)
    flicker /= np.max(flicker)
    noise = 0.7 * bp(pink(N), 250, 2600) * (0.6 + 0.4 * flicker)
    noise += 0.45 * lp(brown(N), 180)
    for at in rng.uniform(0, LEN + XF, int(12 * (LEN + XF))):  # the drain gurgling
        d = rng.uniform(0.02, 0.06)
        tt = axis(d)
        f0 = rng.uniform(250, 900)
        place(noise, rng.uniform(0.03, 0.1) * osc(f0 * (1 + 0.6 * tt / d), len(tt)) * np.exp(-tt / (d / 3)), at)
    per = 0.06 * tones([(25, 0.5), (50, 1.0), (100, 0.4), (150, 0.15)]) * lfo(TL, 0.5, 0.15)  # the pump
    for at in rng.uniform(0, LEN, 9):
        cyc(per, rng.uniform(0.04, 0.09) * drip(rng.uniform(900, 1700)), at)
    return seam(noise, per, -21.5)  # by LUFS, not RMS: leveled with the other beds


def foundry_base():
    blades = lp(0.5 + 0.5 * osc(18, N, "square"), 90)  # cooling fans
    noise = 0.4 * bp(pink(N), 300, 2200) * (0.75 + 0.25 * blades)
    gen = [(50, 1.0), (50.25, 0.8), (100, 0.6), (100.5, 0.4), (150, 0.35), (200, 0.15)]
    per = 0.28 * tones(gen) * lfo(TL, 0.5, 0.2)  # the generator, throbbing
    per += 0.012 * osc(2400 + 6 * osc(0.25, NL), NL)  # turbine whine
    per += 0.08 * bp(osc(100, NL, "square"), 200, 1200)
    for at in (4.1, 10.8):  # pneumatic hiss
        tt = axis(0.6)
        cyc(per, 0.3 * hp(white(len(tt)), 3000) * np.minimum(1, tt / 0.05) * np.exp(-tt / 0.25), at)
    for at in (7.3, 14.6):  # electrical crackle
        for j in range(rng.integers(3, 8)):
            cyc(per, 0.25 * burst(0.004, 2000, 9000, 0.001), at + j * rng.uniform(0.02, 0.09))
    return seam(noise, per, -21.5)  # by LUFS, not RMS: leveled with the other beds


# ---------- match events ----------
def tower_shot():
    t = axis(0.6)
    n = len(t)
    f = 300 + 1500 * np.exp(-t / 0.04)
    x = (osc(f, n) + 0.4 * osc(f, n, "saw")) * np.exp(-t / 0.12)
    place(x, 0.8 * burst(0.015, 2000, 9000, 0.004), 0)
    x += 0.7 * osc(60, n) * np.exp(-t / 0.1)
    return finish(x, -1.0)


def tower_hit():
    t = axis(0.5)
    x = 0.9 * burst(0.5, 300, 4000, 0.05) + 0.8 * osc(80, len(t)) * np.exp(-t / 0.08)
    for at in rng.uniform(0.01, 0.25, 22):  # electric crackle
        place(x, rng.uniform(0.1, 0.4) * burst(0.003, 3000, 12000, 0.001), at)
    return finish(x, -1.0, drive=2.5)


def tower_down():
    sec = 2.8
    t = axis(sec)
    n = len(t)
    x = 1.0 * lp(white(n), 900) * np.exp(-t / 0.35)
    x += 1.0 * osc(28 + 32 * np.exp(-t / 0.3), n) * np.exp(-t / 0.6)
    groan = sum(osc(f * (1 - 0.4 * np.minimum(1, t / 1.5)), n) for f in (300, 437, 611)) / 3
    x += 0.25 * groan * lfo(t, 7, 0.5) * np.exp(-t / 0.9)
    place(x, 0.8 * lp(white(int(0.6 * SR)), 1200) * np.exp(-axis(0.6) / 0.15), 0.6)  # the collapse lands
    for _ in range(60):  # debris
        at = 0.6 + rng.exponential(0.4)
        place(x, rng.uniform(0.1, 0.35) * burst(rng.uniform(0.003, 0.01), 1200, 6000, 0.002), at)
    return finish(x, -1.0, drive=2.0)


def core_down():
    sec = 4.5
    t = axis(sec)
    n = len(t)
    x = 1.2 * lp(white(n), 700) * np.exp(-t / 0.5)
    x += 1.0 * osc(24 + 40 * np.exp(-t / 0.4), n) * np.exp(-t / 1.0)
    fall = 25 + 195 * np.exp(-t / 0.8)  # the power dies: a hum sinks from 220 Hz to nothing
    x += 0.35 * lp(osc(fall, n, "saw"), 1200) * np.exp(-t / 1.6)
    x += 0.5 * lp(brown(n), 120) * np.exp(-t / 1.4)
    for at in rng.uniform(0.0, 0.8, 40):
        place(x, rng.uniform(0.1, 0.3) * burst(0.004, 3000, 12000, 0.001), at)
    return finish(x, -1.0, drive=2.0)


def wave_spawn():
    x = np.zeros(int(1.6 * SR))
    place(x, brass(220.0, 0.5), 0.0)
    place(x, brass(329.6, 1.05), 0.5)
    return finish(x, -6.0, drive=1.3, fade=0.1)


def minion_hit():
    x = ping([1210, 2130, 3390], [0.06, 0.045, 0.03], 0.2)
    place(x, 0.6 * burst(0.006, 2000, 9000, 0.002), 0)
    return finish(x, -6.0, drive=1.2, fade=0.02)


def camp_aggro():
    sec = 1.2
    t = axis(sec)
    n = len(t)
    jitter = 1 + 0.08 * lp(white(n), 12) / 0.05
    f0 = 70 * np.clip(jitter, 0.7, 1.3) * (1 + 0.3 * np.minimum(1, t / 0.3))
    growl = bp(osc(f0, n, "saw"), 300, 1100) * lfo(t, 25, 0.5)
    breath = bp(white(n), 300, 1500) * 0.4
    servo = 0.15 * bp(osc(400 + 300 * t / sec, n, "saw"), 600, 2400)
    env = np.minimum(1, t / 0.15) * np.minimum(1, (sec - t) / 0.35)
    return finish((growl + breath + servo) * env, -5.0, drive=2.2)


def respawn():
    sec = 1.4
    t = axis(sec)
    n = len(t)
    f = 300 * 3 ** np.minimum(1, t / 0.9)
    x = sum(a * osc(f * h, n) for h, a in [(1, 1.0), (2, 0.5), (3, 0.3), (5, 0.15)])
    env = np.minimum(1, t / 0.6) * np.minimum(1, (sec - t) / 0.4)
    x *= env
    for at in rng.uniform(0.3, 1.1, 14):
        place(x, 0.15 * ping([rng.uniform(3000, 6000)], [0.08], 0.25), at)
    return finish(x, -10.0, drive=1.2, fade=0.1)


def recall_start():
    sec = 2.0
    t = axis(sec)
    n = len(t)
    rate = 4 + 10 * t / sec  # the pulses speed up as it charges
    pulse = 0.5 + 0.5 * np.sin(2 * np.pi * np.cumsum(rate) / SR)
    tone = osc(600, n) * pulse ** 3
    hum = osc(150 + 250 * t / sec, n) * 0.6
    env = np.minimum(1, t / 0.2) * np.minimum(1, (sec - t) / 0.3)
    return finish((tone + hum) * env, -10.0, drive=1.2, fade=0.1)


def recall_arrive():
    sec = 0.9
    t = axis(sec)
    n = len(t)
    sweep = np.zeros(n)
    for i, f in enumerate(np.geomspace(6000, 800, 12)):  # a whoosh falling from 6 kHz to 800 Hz
        seg = slice(int(i * n / 14), int((i + 3) * n / 14))
        w = np.zeros(n)
        w[seg] = np.hanning(seg.stop - seg.start)
        sweep += bp(white(n), f * 0.8, min(f * 1.25, 20000)) * w
    x = 0.6 * sweep + 0.7 * osc(70, n) * np.exp(-t / 0.12)
    place(x, 0.5 * ping([880, 1320, 1760], [0.5, 0.4, 0.3], 0.8), 0.15)
    return finish(x, -6.0, drive=1.3, fade=0.05)


def stinger(notes, chord, step, sec, dark):
    x = np.zeros(int(sec * SR))
    for i, f in enumerate(notes):
        place(x, 0.7 * brass(f, step * 1.5, bright=0.6 - dark), i * step)
    start = len(notes) * step
    for f in chord:
        place(x, 0.5 * brass(f, sec - start, bright=0.5 - dark), start)
    hit = osc(55 if dark < 0.3 else 41, int(1.2 * SR)) * np.exp(-axis(1.2) / 0.35)
    place(x, 0.9 * hit, start)
    if dark:
        x = lp(x, 2500)
    return finish(x, -2.0, drive=1.3, fade=0.4)


def win():
    return stinger([261.6, 329.6, 392.0], [261.6, 329.6, 392.0, 523.3], 0.18, 3.2, 0.0)


def lose():
    return stinger([261.6, 207.7, 174.6], [130.8, 155.6, 196.0], 0.35, 3.4, 0.4)


# ---------- match events, foundry set (2026-11-04) ----------
# Towers are industrial turrets, the core is the plant, minions are small machines. win and lose keep the stingers.
def servo(f0, f1, sec, bright=1600):
    """A motor or hydraulic ram moving: a sliding saw buzz with a little wobble."""
    t = axis(sec)
    f = np.linspace(f0, f1, len(t)) * (1 + 0.01 * np.sin(2 * np.pi * 23 * t))
    return lp(osc(f, len(t), "saw"), bright) * np.sin(np.pi * t / sec) ** 0.7


def hiss(sec, attack=0.03, tau=0.3, lo=2500):
    """Steam or air let out."""
    t = axis(sec)
    return hp(white(len(t)), lo) * np.minimum(1, t / attack) * np.exp(-t / tau)


def sparks(sec, tau=0.12, lo=3000):
    n = int(sec * SR)
    return bp((white(n) > 3.0) * white(n), lo, 10000) * np.exp(-axis(sec) / tau)


def fe_tower_shot():
    """The turret fires a heavy bolt: a hard crack, a chest thump, a ringing barrel, then a steam vent."""
    x = np.zeros(int(0.9 * SR))
    place(x, 0.9 * burst(0.12, 1500, 9000, 0.012), 0)
    place(x, 0.8 * thump(62, 0.5), 0)
    place(x, 0.25 * ping([880, 1370, 2210, 3150], [0.25, 0.18, 0.1, 0.06], 0.6), 0)
    place(x, 0.18 * hiss(0.6, 0.04, 0.2, 3000), 0.08)
    return finish(x, -1.0, 2.0)


def fe_tower_hit():
    """The bolt lands: a metal crunch, a dull thud, sparks."""
    x = np.zeros(int(0.7 * SR))
    place(x, 0.9 * burst(0.15, 300, 6000, 0.035), 0)
    place(x, 0.6 * thump(85, 0.35), 0)
    place(x, 0.3 * ping([520, 810, 1290, 1870], [0.18, 0.13, 0.09, 0.06], 0.5), 0)
    place(x, 0.4 * sparks(0.4), 0.02)
    return finish(x, -1.0, 2.2)


def fe_tower_down():
    """A turret tower gives way: a deep boom, the frame groaning, pieces clanging down, a long steam hiss."""
    x = np.zeros(int(4.0 * SR))
    place(x, 1.0 * thump(38, 1.6), 0)
    place(x, 0.5 * lp(burst(1.2, 40, 900, 0.35), 700), 0)
    place(x, 0.35 * creak(120, 58, 1.4), 0.15)
    for at in np.sort(rng.uniform(0.4, 2.4, 9)):  # pieces clanging down
        f = rng.uniform(300, 900)
        place(x, rng.uniform(0.12, 0.3) * ping([f, f * 1.52, f * 2.31], [0.5, 0.3, 0.18], 0.8), at)
    place(x, 0.3 * burst(2.0, 800, 5000, 0.5), 0.3)
    place(x, 0.2 * hiss(2.4, 0.2, 0.9, 1800), 1.0)
    return finish(x, -1.0, 1.8, fade=0.3)


def fe_core_down():
    """The core's plant fails: the generator winds down under a huge blast, then metal and steam settle."""
    t = axis(5.0)
    f = 100 * np.exp(-t / 1.6) + 18
    x = 0.5 * sum(a * osc(f * k, len(t)) for k, a in [(1, 1.0), (2, 0.5), (3, 0.3)]) * np.exp(-t / 2.2)
    place(x, 1.0 * thump(32, 2.2), 0)
    place(x, 0.8 * lp(burst(3.0, 30, 1200, 0.8), 600), 0)
    place(x, 0.4 * burst(1.5, 1500, 8000, 0.25), 0.02)
    for at in np.sort(rng.uniform(0.8, 3.2, 8)):
        f0 = rng.uniform(200, 700)
        place(x, rng.uniform(0.1, 0.25) * ping([f0, f0 * 1.47, f0 * 2.2], [0.6, 0.35, 0.2], 0.9), at)
    place(x, 0.25 * hiss(3.0, 0.3, 1.2, 1500), 1.2)
    return finish(x, -1.0, 1.6, fade=0.4)


def fe_wave_spawn():
    """The shift horn, then the yard gates: the minions roll out."""
    x = np.zeros(int(2.2 * SR))
    place(x, 0.6 * lp(brass(147, 1.3, 0.25) + 0.8 * brass(185, 1.3, 0.25), 1400), 0)
    place(x, 0.5 * ping([150, 233, 371], [0.6, 0.45, 0.3], 1.0), 1.25)  # gate unlatching
    place(x, 0.3 * servo(70, 110, 0.8, 900), 1.3)  # gate rolling
    return finish(x, -1.0, 1.4, fade=0.15)


def fe_minion_hit():
    """A small machine hit: a light metal tick and a short crunch."""
    x = np.zeros(int(0.25 * SR))
    place(x, 0.6 * ping([1250, 1930, 2780], [0.06, 0.04, 0.03], 0.2), 0)
    place(x, 0.6 * burst(0.08, 800, 6000, 0.012), 0)
    return finish(x, -1.0, 2.0)


def fe_camp_aggro():
    """A yard machine wakes: a motor spinning up, a clank, a puff of steam."""
    x = np.zeros(int(1.1 * SR))
    place(x, 0.6 * servo(160, 520, 0.5, 2200), 0)
    place(x, 0.5 * ping([330, 520, 790], [0.35, 0.25, 0.15], 0.6), 0.45)
    place(x, 0.3 * thump(75, 0.3), 0.45)
    place(x, 0.25 * hiss(0.5, 0.03, 0.15, 2500), 0.5)
    return finish(x, -1.0, 1.6)


def fe_respawn():
    """Back on the field: a hydraulic lift rising, a power-up hum, the lock clunk."""
    t = axis(1.5)
    n = len(t)
    x = 0.35 * (osc(np.linspace(140, 560, n), n) + 0.4 * osc(np.linspace(280, 1120, n), n)) * np.sin(np.pi * t / 1.5) ** 0.8
    place(x, 0.4 * hiss(1.0, 0.05, 0.5, 1200), 0)
    place(x, 0.6 * thump(90, 0.3), 1.15)
    place(x, 0.3 * ping([600, 950], [0.2, 0.12], 0.3), 1.15)
    return finish(x, -1.0, 1.5, fade=0.08)


def fe_recall_start():
    """Recall charging: a rising power whine with a tremble, a few sparks."""
    t = axis(1.8)
    n = len(t)
    f = np.linspace(260, 1150, n)
    x = (osc(f, n) + 0.3 * osc(f * 2.01, n)) * (0.7 + 0.3 * np.sin(2 * np.pi * 9 * t))
    x *= np.minimum(1, t / 0.3) * np.minimum(1, (1.8 - t) / 0.3)
    for at in rng.uniform(0.3, 1.5, 5):
        place(x, 0.4 * burst(0.006, 2500, 9000, 0.002), at)
    return finish(x, -1.0, 1.3, fade=0.1)


def fe_recall_arrive():
    """Arriving at base: a discharge snap, a pneumatic thunk, the hum dying away."""
    t = axis(1.2)
    x = 0.2 * osc(np.linspace(600, 150, len(t)), len(t)) * np.exp(-t / 0.35)
    place(x, 0.8 * burst(0.05, 2000, 9000, 0.01), 0)
    place(x, 0.7 * thump(70, 0.4), 0.02)
    place(x, 0.35 * hiss(0.5, 0.02, 0.15, 2000), 0.05)
    return finish(x, -1.0, 1.6)


## Ear-weighted loudness targets (LUFS) for the foundry events: the big map moments loudest, minion hits softest.
EVENT_LUFS = {"tower_shot": -15, "tower_hit": -15, "tower_down": -13, "core_down": -12, "wave_spawn": -16,
              "minion_hit": -18, "camp_aggro": -16, "respawn": -17, "recall_start": -18, "recall_arrive": -17}


def lufs(x):
    """Integrated loudness by ffmpeg's ebur128, padded to 1 s so short sounds still measure."""
    pad = np.zeros(max(len(x), SR))
    pad[:len(x)] = x
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "m.wav"
        write_wav(wav, pad)
        out = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(wav), "-af", "ebur128", "-f", "null", "-"],
                             capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", out)[-1])


def level(x, target, tries=4):
    """Scale x to `target` LUFS. A sharp hit whose peaks would pass -1 dBFS first gets them soft-clipped
    (up to `tries` passes, which adds a little punch), then is pulled back if it still can't get there."""
    for _ in range(tries):
        x = x * 10 ** ((target - lufs(x)) / 20)
        if np.max(np.abs(x)) <= 0.89:
            return x
        x = 0.89 * np.tanh(x / 0.89)
    return x * (0.89 / max(0.89, np.max(np.abs(x))))


# ---------- write ----------
def write_wav(path, x):
    path.parent.mkdir(parents=True, exist_ok=True)
    wavfile.write(path, SR, (x * 32767).astype(np.int16))


def write_ogg(path, x):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "bed.wav"
        write_wav(wav, x)
        subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(wav),
                        "-c:a", "libvorbis", "-q:a", "5", str(path)], check=True)


# ---------- structure hums (2026-11-04): loops under the map lane's turning heads (*TowerGem, *CoreGem) ----------
# Same seam as the foundry beds (16 s, tones on the 1/16 Hz grid, noise crossfaded). The heads turn at 0.8 rad/s,
# one turn per 7.85 s. The turret's scan swells once per 8 s and the reactor's four posts pass the drum at
# 0.5 Hz; MapAudio plays both at pitch 1.0186, which speeds those rates up to the real turn.
HUM_LUFS = {"turret_hum": -27, "core_hum": -24}


def turret_hum():
    sweep = 0.5 + 0.5 * np.cos(2 * np.pi * 0.125 * T)  # one scan pass per 8 s
    gears = bp(white(N), 900, 2600) * lp(0.5 + 0.5 * osc(24, N, "square"), 120)  # the slewing ring's teeth
    noise = 0.25 * gears * (0.3 + 0.7 * sweep) + 0.08 * bp(pink(N), 150, 900)
    sw = sweep[:NL]
    per = tones([(75, 1.0), (150, 0.5), (225, 0.3), (300, 0.15)]) * (0.75 + 0.25 * sw)  # the drive motor
    whine = osc(1250 + 40 * np.sin(2 * np.pi * 0.125 * TL), NL)  # the servo, bending up through each pass
    per = 0.5 * per + 0.12 * whine * (0.15 + 0.85 * sw ** 2)
    for k in range(2):  # a soft sensor blip at the top of each pass
        cyc(per, 0.05 * ping([2400, 3600], [0.05, 0.03], 0.12), k * 8.0)
        cyc(per, 0.035 * ping([2400, 3600], [0.05, 0.03], 0.12), k * 8.0 + 0.14)
    return seam(noise, per, -27)


def core_hum():
    posts = 0.5 + 0.5 * np.cos(2 * np.pi * 0.5 * T)  # four posts passing the drum, 0.5 Hz
    noise = 0.5 * bp(pink(N), 200, 1400) * (0.3 + 0.7 * posts ** 3)  # air pushed round by each post
    arcs = (white(N) > 3.4).astype(float) * white(N)  # sparse arcing off the drum
    noise += 0.6 * bp(arcs, 2500, 7000)
    per = tones([(40, 1.0), (40.25, 0.8), (80, 0.6), (80.5, 0.4), (120, 0.35), (160, 0.2)])  # the drum, beating
    per += 0.25 * bp(osc(120, NL, "square"), 240, 2000) * lfo(TL, 0.25, 0.4)  # electric buzz
    per += 0.06 * tones([(660, 1.0), (990, 0.6)]) * lfo(TL, 0.125, 0.8)  # the glow, a faint shimmer
    return seam(0.6 * noise, 0.5 * per, -24)


HUMS = {"turret_hum": turret_hum, "core_hum": core_hum}

THEMES = {
    "foundry": {"lane": foundry_lane, "jungle": foundry_jungle, "plaza": foundry_plaza,
                "stream": foundry_stream, "base": foundry_base},
    "wild": {"lane": wild_lane, "jungle": wild_jungle, "plaza": wild_plaza, "stream": wild_stream,
             "base": wild_base},
}

EVENT_SETS = {
    "foundry": {"tower_shot": fe_tower_shot, "tower_hit": fe_tower_hit, "tower_down": fe_tower_down,
                "core_down": fe_core_down, "wave_spawn": fe_wave_spawn, "minion_hit": fe_minion_hit,
                "camp_aggro": fe_camp_aggro, "respawn": fe_respawn, "recall_start": fe_recall_start,
                "recall_arrive": fe_recall_arrive, "win": win, "lose": lose},
    "wild": {f.__name__: f for f in [tower_shot, tower_hit, tower_down, core_down, wave_spawn, minion_hit,
                                     camp_aggro, respawn, recall_start, recall_arrive, win, lose]},
}

## Usage: python tools/audio/synth_map.py [beds] [events] [hums] [--theme foundry|wild]  (no parts: all three)
## The random detail is drawn in order, so the events in the game were rendered after the wild beds;
## running "events" again re-rolls their detail. "beds" alone leaves the event files untouched.
if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    theme = args[args.index("--theme") + 1] if "--theme" in args else "foundry"
    parts = [a for a in args if a in ("beds", "events", "hums")] or ["beds", "events", "hums"]
    if "hums" in parts:  # the turret and core heads, any theme
        for name, make in HUMS.items():
            x = level(make(), HUM_LUFS[name])
            write_ogg(BEDS / f"{name}.ogg", x)
            print(f"audio/ambience/{name}.ogg  {LEN:.0f} s loop  {lufs(x):.1f} LUFS")
    if "beds" in parts:
        for name, make in THEMES[theme].items():
            write_ogg(BEDS / f"{name}.ogg", make())
            print(f"audio/ambience/{name}.ogg  {LEN:.0f} s loop ({theme})")
    if "events" in parts:
        for name, make in EVENT_SETS[theme].items():
            x = make()
            if theme == "foundry" and name in EVENT_LUFS:
                x = level(x, EVENT_LUFS[name])
            write_wav(EVENTS / f"{name}.wav", x)
            print(f"audio/sfx/map/{name}.wav  {len(x) / SR:.2f} s  {lufs(x):.1f} LUFS ({theme})")
