"""Synthesize the battle sounds (Claude, 2026-10-16; Preston: "go" on the open items after the battle effects pass).

Every sound is built here from shaped noise and tones with fixed seeds, so the set is ours outright and re-runnable:
no samples, no paid tools. The method follows Hollowtide's build_*_sounds.py scripts and its sound direction
(D:/dev/hollowtide/docs/audio/game-sound-direction-2026-09-30.md): each impact is layers with one job each (a transient
above 1 kHz, a sub drop, a body, the material, a short room tail), and hits carry a soft tonal tick on top so they read
at low volume. Machines are metal, so the material layer is mostly struck plate: a few inharmonic partials.

Tuning: Hollowtide is A = 432 Hz; this game's tuning is Preston's call (docs/team/how-preston-works.md: "ask before
assuming the same here"). A4 below sets every pitched element; most sounds are noise and have no pitch at all.
`python tools/audio/build_battle_sfx.py` writes audio/sfx/battle/<name>.wav at A4 = 440 and the same set at 432 in
audio/sfx/battle_432/, so the switch is a folder name in scripts/battle/sfx.gd.

  python tools/audio/build_battle_sfx.py
Writes 44.1 kHz mono 16-bit WAV files; prints each name, length and peak.
"""
import sys
import wave
from pathlib import Path

import numpy as np

SR = 44100
ROOT = Path(__file__).resolve().parent.parent.parent
A4 = 440.0


# --- building blocks ---------------------------------------------------------------------------------------------------

def n_of(seconds):
    return int(seconds * SR)


def noise(seconds, seed):
    return np.random.default_rng(seed).standard_normal(n_of(seconds))


def env(n, attack, decay):
    t = np.arange(n) / SR
    return np.minimum(1.0, t / max(attack, 1e-4)) * np.exp(-t / max(decay, 1e-4))


def band(x, lo, hi, soft=0.15):
    """FFT band filter with soft edges (lo=0: lowpass, hi=None: highpass)."""
    if len(x) == 0:
        return x
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X = np.fft.rfft(x)
    m = np.ones_like(f)
    if lo > 0:
        m *= 1 / (1 + np.exp(-(f - lo) / max(1.0, lo * soft)))
    if hi is not None:
        m *= 1 / (1 + np.exp((f - hi) / max(1.0, hi * soft)))
    return np.fft.irfft(X * m, len(x))


def lowpass(x, hi):
    return band(x, 0, hi)


def highpass(x, lo):
    return band(x, lo, None)


def put(out, x, at, gain=1.0):
    i = int(at * SR)
    n = min(len(x), len(out) - i)
    if n > 0 and i >= 0:
        out[i:i + n] += x[:n] * gain


def fade(x, a, b):
    na, nb = n_of(a), n_of(b)
    if na:
        x[:na] *= np.linspace(0, 1, na)
    if nb:
        x[-nb:] *= np.linspace(1, 0, nb)
    return x


def sweep(seconds, f0, f1, shape="sine", seed=0):
    """A tone gliding from f0 to f1 (exponential glide)."""
    n = n_of(seconds)
    f = f0 * (f1 / f0) ** (np.arange(n) / max(1, n - 1))
    ph = 2 * np.pi * np.cumsum(f) / SR
    if shape == "sine":
        return np.sin(ph)
    if shape == "saw":   # band-limited enough at these pitches: a few harmonics
        return sum(np.sin(k * ph) / k for k in range(1, 9)) * 0.6
    if shape == "pulse":   # a softened chip pulse (Hollowtide's CHIP layer)
        return np.tanh(3 * np.sin(ph))
    raise ValueError(shape)


def note(semitones):
    """Frequency `semitones` above A4 (negative: below)."""
    return A4 * 2 ** (semitones / 12)


def sub_drop(seconds, f0, f1):
    n = n_of(seconds)
    return sweep(seconds, f0, f1) * env(n, 0.002, seconds * 0.35)


def click(seed, length=0.006, lo=2500):
    return highpass(noise(length, seed), lo) * env(n_of(length), 0.0002, length * 0.3)


def plate(seconds, base, seed, decay=None, ratios=(1.0, 2.76, 5.40, 8.93, 13.3)):
    """Struck metal plate: inharmonic partials, the higher ones dying faster."""
    n = n_of(seconds)
    t = np.arange(n) / SR
    rng = np.random.default_rng(seed)
    out = np.zeros(n)
    d = decay or seconds * 0.3
    for k, r in enumerate(ratios):
        f = base * r * rng.uniform(0.98, 1.02)
        if f > SR / 2.2:
            continue
        out += np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28)) * np.exp(-t / (d / (1 + k * 0.8))) / (1 + k * 0.6)
    return out


def whoosh(seconds, seed, f0, f1, rise=True):
    """Air rushing past: noise through a band sweeping from f0 to f1."""
    n = n_of(seconds)
    x = noise(seconds, seed)
    out = np.zeros(n)
    steps = 12
    seg = max(1, n // steps)
    for s in range(steps):
        k = s / (steps - 1)
        f = f0 * (f1 / f0) ** k
        a, b = s * seg, min(n, (s + 2) * seg)
        if b - a < 8:
            continue
        out[a:b] += band(x[a:b], f * 0.6, f * 1.6) * np.hanning(b - a)
    amp = np.sin(np.linspace(0, np.pi, n)) ** (0.6 if rise else 1.4)
    return out * amp


def clatter(seconds, seed, rate, lo=1400, hi=5200, fall=3.0):
    """Small metal bits pattering down: sparse short clinks that thin out."""
    rng = np.random.default_rng(seed)
    out = np.zeros(n_of(seconds))
    t, k = 0.0, 0
    while t < seconds:
        t += rng.exponential(1.0 / rate)
        f = rng.uniform(lo, hi)
        put(out, plate(rng.uniform(0.02, 0.05), f, seed * 100 + k, ratios=(1.0, 2.76, 5.4)), t, np.exp(-fall * t / seconds) * rng.uniform(0.4, 1.0))
        k += 1
    return out


def room(x, seconds=0.35, mix=0.18, seed=99):
    """A short metal-hangar tail: the dry sound convolved with decaying noise (numpy FFT)."""
    ir = noise(seconds, seed) * np.exp(-np.arange(n_of(seconds)) / (SR * seconds * 0.22))
    ir = lowpass(ir, 5000)
    ir /= np.abs(ir).sum() ** 0.5 + 1e-9
    n = len(x) + len(ir)
    wet = np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(ir, n), n)
    out = np.zeros(n)
    out[:len(x)] += x
    out += wet / max(1e-9, np.abs(wet).max()) * np.abs(x).max() * mix
    return out


def tick(semis, seed, length=0.08, chip=0.35):
    """The soft tonal tick hits carry so they read at low volume: a mallet sine with a quiet chip pulse under it."""
    n = n_of(length)
    f = note(semis)
    t = np.arange(n) / SR
    mallet = np.sin(2 * np.pi * f * t) * env(n, 0.0008, length * 0.25)
    pulse = np.tanh(3 * np.sin(2 * np.pi * f * t)) * env(n, 0.0008, length * 0.18)
    return mallet * (1 - chip) + pulse * chip * 0.6


# --- the sounds ----------------------------------------------------------------------------------------------------------

def whoosh_light():   # a fast swing or lunge: the sound two frames ahead of the strike
    return fade(whoosh(0.22, 1, 2400, 700), 0.004, 0.03)


def whoosh_heavy():   # a big limb or body hauling round
    out = whoosh(0.34, 2, 1100, 220)
    put(out, lowpass(noise(0.3, 3), 180) * env(n_of(0.3), 0.04, 0.12), 0.02, 0.6)
    return fade(out, 0.006, 0.05)


def whiff():   # a miss: the swing finds air
    return fade(whoosh(0.2, 4, 1800, 500) * 0.8, 0.004, 0.04)


def hit_metal():   # a blow on armour: contact crack, a clang of plate, the thump of mass
    out = np.zeros(n_of(0.45))
    put(out, click(10), 0.0, 1.0)
    put(out, plate(0.4, 310, 11), 0.001, 0.55)
    put(out, lowpass(noise(0.14, 12), 700) * env(n_of(0.14), 0.001, 0.04), 0.0, 0.9)
    put(out, sub_drop(0.22, 110, 45), 0.0, 0.9)
    put(out, tick(-12, 13), 0.0, 0.18)
    return fade(room(out, 0.3, 0.15), 0.0005, 0.06)


def hit_heavy():   # a crushing blow: deeper plate, a long sub, bits of armour raining down
    out = np.zeros(n_of(0.9))
    put(out, click(20, 0.01, 1800), 0.0, 1.0)
    put(out, plate(0.7, 170, 21), 0.002, 0.6)
    put(out, lowpass(noise(0.3, 22), 500) * env(n_of(0.3), 0.002, 0.09), 0.0, 1.0)
    put(out, sub_drop(0.5, 85, 30), 0.0, 1.0)
    put(out, clatter(0.5, 23, 30), 0.08, 0.3)
    put(out, tick(-17, 24), 0.0, 0.18)
    return fade(room(out, 0.45, 0.2), 0.0005, 0.1)


def hit_slash():   # a blade edge across plate: a hiss, a scrape, a high ring
    out = np.zeros(n_of(0.4))
    put(out, whoosh(0.08, 30, 5200, 2000, rise=False), 0.0, 0.8)
    scrape = band(noise(0.18, 31), 2200, 7000) * env(n_of(0.18), 0.002, 0.06)
    scrape *= 0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 70 * np.arange(len(scrape)) / SR))   # the edge chattering
    put(out, scrape, 0.02, 0.7)
    put(out, plate(0.3, 1300, 32), 0.02, 0.35)
    put(out, sub_drop(0.12, 140, 70), 0.02, 0.5)
    put(out, tick(3, 33), 0.02, 0.15)
    return fade(room(out, 0.25, 0.12), 0.0005, 0.05)


def hit_bite():   # jaws closing on armour: a crunch of short clacks and a squeal of bent plate
    out = np.zeros(n_of(0.42))
    rng = np.random.default_rng(40)
    for k in range(6):
        f = rng.uniform(300, 1300)
        put(out, band(noise(0.03, 41 + k), f * 0.6, f * 1.6) * env(n_of(0.03), 0.0004, 0.008), 0.004 * k + rng.uniform(0, 0.01), 0.8)
    put(out, sub_drop(0.2, 120, 50), 0.0, 0.8)
    squeal = sweep(0.16, 2100, 1500) * env(n_of(0.16), 0.01, 0.05)
    put(out, squeal, 0.03, 0.12)
    put(out, tick(-9, 47), 0.0, 0.15)
    return fade(room(out, 0.25, 0.12), 0.0005, 0.05)


def hit_kinetic():   # the pneumatic glove fires on contact: a pop, the punch of air, a valve's hiss
    out = np.zeros(n_of(0.55))
    put(out, click(50, 0.008, 1500), 0.0, 1.0)
    put(out, sub_drop(0.18, 160, 55), 0.0, 1.0)
    put(out, band(noise(0.06, 51), 300, 2500) * env(n_of(0.06), 0.0005, 0.015), 0.0, 0.9)
    put(out, plate(0.3, 260, 52), 0.003, 0.35)
    hiss = highpass(noise(0.35, 53), 3500) * env(n_of(0.35), 0.01, 0.1)
    put(out, hiss, 0.05, 0.35)
    put(out, tick(-5, 54), 0.0, 0.15)
    return fade(room(out, 0.25, 0.12), 0.0005, 0.06)


def hit_energy():   # a beam hits plate: a sizzle and a falling zap
    out = np.zeros(n_of(0.45))
    put(out, highpass(noise(0.4, 60), 3000) * env(n_of(0.4), 0.002, 0.11), 0.0, 0.6)
    put(out, sweep(0.3, note(10), note(-14), "saw") * env(n_of(0.3), 0.002, 0.08), 0.0, 0.4)
    put(out, sub_drop(0.18, 120, 50), 0.0, 0.6)
    put(out, tick(7, 61), 0.0, 0.15)
    return fade(out, 0.0005, 0.05)


def hit_water():   # a jet or wave hits: the slap, spray, droplets
    out = np.zeros(n_of(0.6))
    slap = band(noise(0.08, 70), 300, 3000) * env(n_of(0.08), 0.0008, 0.02)
    put(out, slap, 0.0, 1.0)
    spray = band(noise(0.45, 71), 1800, 8000) * env(n_of(0.45), 0.01, 0.12)
    put(out, spray, 0.01, 0.45)
    rng = np.random.default_rng(72)
    for k in range(12):
        f = rng.uniform(1600, 3800)
        put(out, sweep(0.03, f, f * 1.4) * env(n_of(0.03), 0.001, 0.008), rng.uniform(0.02, 0.4), 0.2)
    put(out, sub_drop(0.2, 95, 45), 0.0, 0.6)
    return fade(out, 0.0005, 0.06)


def explosion_small():   # a shell or a blast on the hull: a crack, a low burst, crackle, a short tail
    out = np.zeros(n_of(0.9))
    put(out, click(80, 0.01, 1500), 0.0, 1.0)
    put(out, sub_drop(0.5, 90, 28), 0.0, 1.0)
    put(out, lowpass(noise(0.5, 81), 900) * env(n_of(0.5), 0.003, 0.13), 0.0, 1.0)
    rng = np.random.default_rng(82)
    for k in range(14):   # crackle
        put(out, click(83 + k, 0.004, 2500), rng.uniform(0.05, 0.5), rng.uniform(0.15, 0.45))
    return fade(room(out, 0.5, 0.2), 0.0005, 0.12)


def explosion_big():   # a machine going up: two bursts, a long rumble, plate raining down
    out = np.zeros(n_of(2.0))
    put(out, click(100, 0.015, 1200), 0.0, 1.0)
    put(out, sub_drop(1.0, 70, 22), 0.0, 1.0)
    put(out, lowpass(noise(1.2, 101), 700) * env(n_of(1.2), 0.005, 0.35), 0.0, 1.0)
    put(out, lowpass(noise(0.6, 102), 1500) * env(n_of(0.6), 0.003, 0.15), 0.12, 0.7)
    put(out, clatter(1.2, 103, 26, 900, 4200, 2.5), 0.25, 0.35)
    return fade(room(out, 0.8, 0.25), 0.0005, 0.3)


def debris():   # loose plate and rock pattering down
    return fade(clatter(0.7, 110, 34, 900, 4600), 0.0005, 0.08)


def shot_flak():   # one burst from the pouch shotgun: a sharp blast and the slap of the report
    out = np.zeros(n_of(0.35))
    put(out, click(120, 0.006, 2200), 0.0, 1.0)
    put(out, lowpass(noise(0.12, 121), 2800) * env(n_of(0.12), 0.0005, 0.03), 0.0, 1.0)
    put(out, sub_drop(0.14, 150, 60), 0.0, 0.8)
    put(out, plate(0.12, 900, 122), 0.004, 0.15)   # the action cycling
    return fade(room(out, 0.25, 0.15), 0.0003, 0.05)


def shot_cannon():   # a single shell leaving a barrel
    out = np.zeros(n_of(0.45))
    put(out, click(130, 0.008, 1800), 0.0, 1.0)
    put(out, lowpass(noise(0.2, 131), 1600) * env(n_of(0.2), 0.0008, 0.05), 0.0, 1.0)
    put(out, sub_drop(0.25, 120, 40), 0.0, 1.0)
    return fade(room(out, 0.35, 0.18), 0.0003, 0.06)


def throw_heave():   # the gorilla tears a ballast block free and hurls it: servos, a grunt of hydraulics, air
    out = np.zeros(n_of(0.5))
    put(out, sweep(0.25, 140, 260, "saw") * env(n_of(0.25), 0.03, 0.1), 0.0, 0.25)   # hydraulic whine
    put(out, whoosh(0.35, 140, 900, 300), 0.1, 0.9)
    put(out, lowpass(noise(0.2, 141), 300) * env(n_of(0.2), 0.02, 0.07), 0.0, 0.6)
    return fade(out, 0.005, 0.06)


def tear_metal():   # a block wrenched off its rack: a screech and a snap
    out = np.zeros(n_of(0.4))
    screech = band(noise(0.25, 145), 1200, 4500) * env(n_of(0.25), 0.02, 0.1)
    screech *= 0.5 + 0.5 * np.sin(2 * np.pi * 38 * np.arange(len(screech)) / SR)
    put(out, screech, 0.0, 0.6)
    put(out, click(146, 0.01, 1500), 0.22, 1.0)
    put(out, plate(0.15, 700, 147), 0.22, 0.3)
    return fade(out, 0.003, 0.05)


def plates():   # scale plates flicked off in a spread: light clinks, staggered
    out = np.zeros(n_of(0.45))
    for k in range(5):
        put(out, plate(0.12, 1500 + 210 * k, 150 + k, ratios=(1.0, 2.76, 5.4)), 0.035 * k, 0.6)
        put(out, whoosh(0.08, 160 + k, 3500, 1800), 0.035 * k, 0.35)
    return fade(out, 0.001, 0.05)


def missile():   # a pod missile leaving: ignition crack and a rising rush
    out = np.zeros(n_of(0.6))
    put(out, click(170, 0.01, 1500), 0.0, 0.8)
    put(out, whoosh(0.55, 171, 400, 2600), 0.0, 1.0)
    rng = np.random.default_rng(172)
    for k in range(10):
        put(out, click(173 + k, 0.003, 3000), rng.uniform(0.05, 0.5), 0.25)
    return fade(out, 0.002, 0.08)


def beam():   # the lance: a whine rising to the shot, then a buzzing beam with a sizzle on top
    out = np.zeros(n_of(0.75))
    rise = sweep(0.18, note(-12), note(7)) * env(n_of(0.18), 0.12, 1.0)
    put(out, rise, 0.0, 0.35)
    n = n_of(0.5)
    t = np.arange(n) / SR
    f = note(-24)
    buzz = sum(np.sin(2 * np.pi * f * k * (1 + 0.003 * (k % 2)) * t) / k for k in range(1, 12))
    buzz *= (0.75 + 0.25 * np.sin(2 * np.pi * 28 * t)) * np.minimum(1, t / 0.01) * np.exp(-t / 0.4)
    put(out, buzz * 0.35, 0.16, 1.0)
    put(out, highpass(noise(0.5, 180), 4000) * env(n, 0.01, 0.25), 0.16, 0.25)
    return fade(out, 0.002, 0.1)


def jets():   # twin pressure jets: a hard hiss fluttering, and the gurgle under it
    n = n_of(0.6)
    t = np.arange(n) / SR
    hiss = band(noise(0.6, 190), 1000, 7000) * (0.7 + 0.3 * np.sin(2 * np.pi * 31 * t))
    gurgle = lowpass(noise(0.6, 191), 400) * (0.5 + 0.5 * np.sin(2 * np.pi * 9 * t))
    out = (hiss * 0.8 + gurgle * 0.5) * np.minimum(1, t / 0.03) * np.exp(-t / 0.45)
    return fade(out, 0.003, 0.08)


def howl():   # the throat emitter: a rough falling cry through a vowel-like band, a concussive rumble under it
    n = n_of(0.7)
    t = np.arange(n) / SR
    voice = sweep(0.7, note(-5), note(-19), "saw") * (1 + 0.15 * np.sin(2 * np.pi * 6 * t))
    voice = band(voice, 450, 1400) * 1.6 + band(voice, 1800, 2900) * 0.6
    voice = np.tanh(voice * 2.5) * np.minimum(1, t / 0.03) * np.exp(-t / 0.4)
    out = np.zeros(n_of(0.8))
    put(out, voice, 0.0, 0.8)
    put(out, lowpass(noise(0.6, 200), 160) * env(n_of(0.6), 0.02, 0.2), 0.05, 0.7)
    return fade(room(out, 0.4, 0.2), 0.003, 0.1)


def quake():   # the slam's shockwave running along the ground
    n = n_of(0.8)
    t = np.arange(n) / SR
    rumble = lowpass(noise(0.8, 210), 140) * (0.6 + 0.4 * np.sin(2 * np.pi * 7 * t)) * np.minimum(1, t / 0.02) * np.exp(-t / 0.35)
    out = rumble * 1.0
    put(out, sub_drop(0.6, 60, 25), 0.0, 1.0)
    put(out, clatter(0.6, 211, 30, 700, 2600), 0.05, 0.3)
    return fade(out, 0.001, 0.12)


def stomp():   # a heavy foot or a landing
    out = np.zeros(n_of(0.35))
    put(out, sub_drop(0.25, 95, 38), 0.0, 1.0)
    put(out, lowpass(noise(0.12, 220), 400) * env(n_of(0.12), 0.002, 0.04), 0.0, 0.8)
    put(out, plate(0.15, 420, 221), 0.004, 0.18)
    return fade(out, 0.0005, 0.05)


def boost():   # hip boosters lighting: a roar rising with crackle
    out = np.zeros(n_of(0.5))
    put(out, whoosh(0.45, 230, 300, 2400), 0.0, 1.0)
    put(out, lowpass(noise(0.45, 231), 600) * env(n_of(0.45), 0.03, 0.2), 0.0, 0.6)
    rng = np.random.default_rng(232)
    for k in range(8):
        put(out, click(233 + k, 0.003, 3000), rng.uniform(0.05, 0.35), 0.3)
    return fade(out, 0.003, 0.08)


def roll():   # an armoured ball rolling in fast
    n = n_of(0.45)
    t = np.arange(n) / SR
    out = lowpass(noise(0.45, 240), 300) * (0.55 + 0.45 * np.sign(np.sin(2 * np.pi * 14 * t))) * np.minimum(1, t / 0.25)
    put(out, clatter(0.45, 241, 22, 600, 2000), 0.0, 0.3)
    return fade(out, 0.01, 0.05)


def gust():   # one huge wingbeat
    out = whoosh(0.4, 250, 650, 140)
    put(out, lowpass(noise(0.3, 251), 220) * env(n_of(0.3), 0.06, 0.12), 0.04, 0.8)
    return fade(out, 0.006, 0.06)


def charge_up():   # energy drawn in: a rising glide with a shimmer, ending on E5
    n = n_of(0.7)
    out = np.zeros(n)
    t = np.arange(n_of(0.6)) / SR
    glide = sweep(0.6, note(-12), note(7)) * np.minimum(1, t / 0.05)
    put(out, glide * 0.5, 0.0, 1.0)
    put(out, sweep(0.6, note(-12), note(7), "pulse") * np.minimum(1, t / 0.05) * 0.12, 0.0, 1.0)
    shimmer = sum(np.sin(2 * np.pi * note(19 + s) * t) for s in (0, 3, 7)) * np.linspace(0, 1, len(t)) ** 2
    put(out, shimmer * 0.08, 0.0, 1.0)
    put(out, tick(19, 260, 0.12), 0.58, 0.5)
    return fade(out, 0.005, 0.08)


def repair():   # a repair or an item: two soft notes rising (D5 then A5)
    out = np.zeros(n_of(0.55))
    put(out, tick(5, 270, 0.3, 0.3), 0.0, 1.0)
    put(out, tick(12, 271, 0.35, 0.3), 0.12, 1.0)
    put(out, highpass(noise(0.3, 272), 5000) * env(n_of(0.3), 0.02, 0.1), 0.1, 0.06)
    return fade(out, 0.001, 0.08)


def shield():   # an energy shell closing round the machine: a swelling two-note hum with a shimmer
    n = n_of(0.8)
    t = np.arange(n) / SR
    hum = (np.sin(2 * np.pi * note(-12) * t) + 0.7 * np.sin(2 * np.pi * note(-5) * t)) * (0.8 + 0.2 * np.sin(2 * np.pi * 9 * t))
    hum *= np.minimum(1, t / 0.15) * np.exp(-t / 0.45)
    out = hum * 0.6
    put(out, highpass(noise(0.6, 280), 5000) * env(n_of(0.6), 0.1, 0.2), 0.0, 0.12)
    put(out, tick(7, 281, 0.2), 0.12, 0.4)
    return fade(out, 0.004, 0.1)


def mines():   # mines dropped under the foe: three clunks, each with an arming beep
    out = np.zeros(n_of(0.7))
    for k in range(3):
        put(out, stomp() * 0.5, 0.12 * k, 1.0)
        put(out, tick(12, 290 + k, 0.06, 0.8), 0.12 * k + 0.25, 0.5)
    return fade(out, 0.001, 0.05)


def lock_on():   # targeting locks on: quick rising beeps, then a held tone
    out = np.zeros(n_of(0.7))
    for k, s in enumerate((7, 10, 12, 14)):
        put(out, tick(s, 300 + k, 0.05, 0.7), 0.07 * k, 0.6)
    n = n_of(0.3)
    t = np.arange(n) / SR
    put(out, np.tanh(2.5 * np.sin(2 * np.pi * note(19) * t)) * env(n, 0.005, 0.12), 0.3, 0.35)
    return fade(out, 0.001, 0.05)


def power_down():   # a machine dying: a whine falling away and sputtering out
    n = n_of(1.1)
    t = np.arange(n) / SR
    whine = sweep(1.1, note(5), note(-36), "saw") * np.exp(-t / 0.5)
    whine *= (np.random.default_rng(310).random(n) > 0.02 * t * 10)   # sputter: drop-outs as it dies
    return fade(band(whine, 80, 3500) * 0.6, 0.005, 0.15)


def drain():   # the health bar running down: a soft quick ticking
    out = np.zeros(n_of(0.42))
    for k in range(6):
        put(out, tick(-2 - k, 320 + k, 0.03, 0.5), 0.065 * k, 0.4)
    return out


def ui_move():   # the menu cursor: a small mechanical tick
    out = click(330, 0.004, 3000) * 0.6
    o = np.zeros(n_of(0.06))
    put(o, out, 0.0, 1.0)
    put(o, tick(12, 331, 0.05, 0.3), 0.0, 0.5)
    return o


def ui_confirm():   # a choice made: a latch closing and a rising pair
    o = np.zeros(n_of(0.2))
    put(o, click(340, 0.006, 2000), 0.0, 0.7)
    put(o, tick(7, 341, 0.08, 0.3), 0.0, 0.6)
    put(o, tick(14, 342, 0.1, 0.3), 0.05, 0.6)
    return o


def ui_back():   # back out: a falling pair
    o = np.zeros(n_of(0.18))
    put(o, tick(10, 350, 0.08, 0.3), 0.0, 0.5)
    put(o, tick(3, 351, 0.1, 0.3), 0.05, 0.5)
    return o


# each sound and its peak level (dBFS): the loud ones near -1, the light ones lower, so they sit together untouched
SOUNDS = {
    "whoosh_light": (whoosh_light, -6), "whoosh_heavy": (whoosh_heavy, -4), "whiff": (whiff, -8),
    "hit_metal": (hit_metal, -2), "hit_heavy": (hit_heavy, -1), "hit_slash": (hit_slash, -3), "hit_bite": (hit_bite, -3),
    "hit_kinetic": (hit_kinetic, -2), "hit_energy": (hit_energy, -3), "hit_water": (hit_water, -3),
    "explosion_small": (explosion_small, -2), "explosion_big": (explosion_big, -1), "debris": (debris, -9),
    "shot_flak": (shot_flak, -3), "shot_cannon": (shot_cannon, -3), "throw_heave": (throw_heave, -5), "tear_metal": (tear_metal, -6),
    "plates": (plates, -6), "missile": (missile, -4), "beam": (beam, -4), "jets": (jets, -5), "howl": (howl, -3),
    "quake": (quake, -2), "stomp": (stomp, -6), "boost": (boost, -4), "roll": (roll, -5), "gust": (gust, -4),
    "charge_up": (charge_up, -7), "repair": (repair, -8), "shield": (shield, -7), "mines": (mines, -7),
    "lock_on": (lock_on, -9), "power_down": (power_down, -6), "drain": (drain, -14),
    "ui_move": (ui_move, -14), "ui_confirm": (ui_confirm, -10), "ui_back": (ui_back, -11),
}


def save(path, x, peak_db):
    x = np.asarray(x, dtype=np.float64)
    x = x - x.mean() * 0  # keep as is
    x = x / max(1e-9, np.abs(x).max()) * 10 ** (peak_db / 20)
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
    return len(x) / SR


def build(a4, folder):
    global A4
    A4 = a4
    out = ROOT / "audio" / "sfx" / folder
    for name, (fn, peak) in SOUNDS.items():
        secs = save(out / f"{name}.wav", fn(), peak)
        if folder == "battle":
            print(f"{name:16s} {secs:.2f} s  peak {peak} dBFS")


if __name__ == "__main__":
    build(440.0, "battle")
    build(432.0, "battle_432")
    print("built %d sounds at A4 440 (audio/sfx/battle) and 432 (audio/sfx/battle_432)" % len(SOUNDS))
