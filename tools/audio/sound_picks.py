#!/usr/bin/env python3
"""Listen page for two open sound picks (2026-11-05): the rhino ground pound and wall muffling.

Everything is synthesised here or built from the game's own sound files: free, no samples, no downloads.
Writes docs/listen/sound-picks-2026-11-05.html, one page with the audio inside it, so it plays offline and
on a phone. Seeds are fixed, so a picked option comes out the same when it is installed.
Run: python tools/audio/sound_picks.py
"""
import base64
import html
import re
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000
ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "docs" / "listen" / "sound-picks-2026-11-05.html"
REAR_LUFS, SLAM_LUFS = -18.2, -19.1  # what the stand-ins in the game measure now, so no option wins on volume


# ---------- helpers ----------
def axis(sec):
    return np.arange(int(SR * sec)) / SR


def _sos(kind, f, order=2):
    return butter(order, f, kind, fs=SR, output="sos")


def lp(x, f):
    return sosfilt(_sos("lowpass", f), x)


def hp(x, f):
    return sosfilt(_sos("highpass", f), x)


def bp(x, lo, hi):
    return sosfilt(_sos("bandpass", [lo, hi]), x)


def norm(x):
    return x / (np.max(np.abs(x)) + 1e-9)


def noise(sec, rng):
    return rng.standard_normal(int(SR * sec))


def brown(sec, rng):
    return norm(hp(np.cumsum(noise(sec, rng)), 20))


def env(sec, attack, tau):
    t = axis(sec)
    return np.minimum(1.0, t / max(attack, 1e-4)) * np.exp(-t / tau)


def drop(f0, f1, tau, sec):  # a tone whose pitch falls from f0 to f1: the weight of a heavy hit
    f = f1 + (f0 - f1) * np.exp(-axis(sec) / tau)
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def glide(f0, f1, sec, harmonics=(1.0, 0.5, 0.25)):  # a servo climbing in pitch
    t = axis(sec)
    ph = 2 * np.pi * np.cumsum(f0 * (f1 / f0) ** (t / sec)) / SR
    return sum(a * np.sin((k + 1) * ph) for k, a in enumerate(harmonics))


STEEL = [(173, 0.5, 0.9), (412, 0.45, 0.7), (731, 0.35, 0.55), (1187, 0.3, 0.45), (1730, 0.2, 0.35),
         (2410, 0.15, 0.25), (3290, 0.1, 0.18)]  # (Hz, level, decay s): a struck steel plate, not a tuned bell


def ring(partials, sec, rng):  # each partial doubled a hair sharp, so the ring beats like real metal
    t = axis(sec)
    x = np.zeros_like(t)
    for f, a, tau in partials:
        for det, amp in ((1.0, 1.0), (1.0035, 0.5)):
            x += a * amp * np.sin(2 * np.pi * f * det * t + rng.uniform(0, 2 * np.pi)) * np.exp(-t / tau)
    return x


def place(buf, x, at):
    i = int(at * SR)
    j = min(len(buf), i + len(x))
    if j > i:
        buf[i:j] += x[: j - i]
    return buf


def grains(sec, count, lo, hi, rng, start=0.05, spread=0.4):  # falling debris: short ticks, thinning out
    buf = np.zeros(int(SR * sec))
    for at in start + rng.exponential(spread, count):
        if at > sec - 0.05:
            continue
        n = int(SR * rng.uniform(0.003, 0.02))
        tick = rng.standard_normal(n) * np.exp(-np.arange(n) / (n / 4))
        place(buf, tick * rng.uniform(0.3, 1.0) * np.exp(-(at - start) / (spread * 1.5)), at)
    return bp(buf, lo, hi)


def _wav(path, x):
    wavfile.write(path, SR, (np.clip(x, -1, 1) * 32767).astype(np.int16))


def lufs(x):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "x.wav"
        _wav(p, x)
        err = subprocess.run(["ffmpeg", "-nostats", "-hide_banner", "-i", str(p), "-af", "ebur128", "-f", "null", "-"],
                             capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1])


def level(x, target, ceiling=0.89):
    x = norm(x) * 0.3
    for _ in range(4):
        x = x * 10 ** ((target - lufs(x)) / 20)
        if np.max(np.abs(x)) <= ceiling:
            break
        x = ceiling * np.tanh(x / ceiling)
    k = int(0.005 * SR)
    x[-k:] *= np.linspace(1, 0, k)
    return x


def load(path):  # any sound file -> mono float at SR
    raw = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(path), "-f", "f32le", "-ac", "1",
                          "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(float)


# ---------- ground pound: B "Steel" (machine first) ----------
def steel_rear(rng):
    sec = 0.6
    t = axis(sec)
    shape = np.minimum(1, t / 0.05) * np.minimum(1, (sec - t) / 0.08)
    whine = norm(glide(220, 520, sec)) * shape
    hiss = norm(bp(noise(sec, rng), 2500, 7000)) * (t / sec) ** 1.5
    teeth = (np.sin(2 * np.pi * np.cumsum(18 + 14 * t / sec) / SR) > 0.97).astype(float)  # a ratchet speeding up
    ratchet = norm(bp(teeth, 400, 1600))
    motor = norm(lp(noise(sec, rng), 180)) * shape
    return 0.5 * whine + 0.35 * hiss + 0.3 * ratchet + 0.6 * motor


def steel_slam(rng):
    sec = 1.7
    out = np.zeros(int(SR * sec))
    place(out, 0.7 * norm(hp(noise(0.004, rng), 2000)), 0)                          # contact click
    place(out, 1.0 * drop(95, 38, 0.09, 1.0) * env(1.0, 0.002, 0.28), 0)           # deep thump
    place(out, 0.7 * norm(lp(noise(1.2, rng), 400)) * env(1.2, 0.002, 0.12), 0)    # body
    place(out, 0.4 * norm(ring(STEEL, 1.6, rng)), 0.003)                            # the hull rings
    place(out, 0.22 * norm(bp(noise(0.6, rng), 3000, 9000)) * env(0.6, 0.03, 0.25), 0.18)  # hydraulics vent
    place(out, 0.45 * norm(lp(brown(sec, rng), 120)) * env(sec, 0.01, 0.6), 0)     # rumble tail
    place(out, 0.2 * norm(grains(sec, 25, 800, 4000, rng, 0.05, 0.25)), 0)          # a little debris
    return np.tanh(1.5 * out)


# ---------- ground pound: C "Quake" (ground first) ----------
def quake_rear(rng):
    sec = 0.6
    t = axis(sec)
    swell = (t / sec) ** 2
    rumble = norm(lp(brown(sec, rng), 150)) * swell
    rise = norm(glide(35, 60, sec, (1.0,))) * swell
    grind = norm(bp(noise(sec, rng), 300, 1500)) * (0.3 + 0.7 * np.abs(norm(lp(noise(sec, rng), 30)))) * swell
    servo = norm(glide(260, 420, sec))
    suck = norm(hp(noise(sec, rng), 1500)) * (t / sec) ** 3 * np.minimum(1, (sec - t) / 0.03)
    return 0.9 * rumble + 0.5 * rise + 0.45 * grind + 0.2 * servo + 0.2 * suck


def quake_slam(rng):
    sec = 1.7
    out = np.zeros(int(SR * sec))
    m = int(0.012 * SR)
    for at, a in ((0, 1.0), (0.035, 0.5), (0.07, 0.35), (0.12, 0.25)):             # the ground cracks
        place(out, a * norm(bp(rng.standard_normal(m), 1200, 7000)) * np.exp(-np.arange(m) / (0.003 * SR)), at)
    boom = drop(70, 30, 0.12, 1.4) * env(1.4, 0.003, 0.45) + norm(lp(noise(1.4, rng), 250)) * env(1.4, 0.004, 0.35)
    place(out, 0.9 * norm(np.tanh(2.0 * boom)), 0)                                  # heavy boom
    place(out, 0.4 * norm(grains(sec, 120, 900, 5000, rng, 0.06, 0.45)), 0)         # gravel
    place(out, 0.35 * norm(grains(sec, 18, 150, 900, rng, 0.08, 0.5)), 0)           # rocks
    place(out, 0.12 * norm(ring(STEEL, 1.2, rng)), 0.004)                           # a little metal: still a machine
    place(out, 0.5 * norm(lp(brown(sec, rng), 90)) * env(sec, 0.02, 0.8), 0)       # rumble tail
    place(out, 0.15 * norm(bp(noise(1.0, rng), 400, 3000)) * env(1.0, 0.08, 0.4), 0.05)  # dust
    return np.tanh(1.3 * out)


def pair(rear, slam):  # one clip per option: rear up, a beat, slam
    return np.concatenate([rear, np.zeros(int(0.35 * SR)), slam])


# ---------- wall muffling ----------
MUFFLE = {"None": None, "Light": (2500, 2, -4.0), "Heavy": (800, 4, -9.0)}  # low-pass Hz, filter order, dB


def fight():  # a few seconds of a tower fight, from the game's own foundry event sounds
    m = ROOT / "audio" / "sfx" / "map"
    shot, hit, minion = (load(m / f"{k}.wav") for k in ("tower_shot", "tower_hit", "minion_hit"))

    def pitched(x, r):
        return np.interp(np.arange(0, len(x) - 1, r), np.arange(len(x)), x)

    buf = np.zeros(int(3.4 * SR))
    for at, x in ((0.0, shot), (0.35, hit), (0.9, minion), (1.25, pitched(minion, 1.07)),
                  (1.6, pitched(minion, 0.94)), (1.9, shot), (2.25, hit), (2.6, pitched(minion, 1.03))):
        place(buf, x, at)
    return buf


def muffled(x, cutoff, order, db):
    return sosfilt(_sos("lowpass", cutoff, order), x) * 10 ** (db / 20)


def muffle_demos():  # the lane bed throughout; the fight in the open, then the same fight behind a wall
    f = fight()
    bed = load(ROOT / "audio" / "ambience" / "lane.ogg")[: int(7.4 * SR)]
    k = int(0.3 * SR)
    demos = {}
    for name, opt in MUFFLE.items():
        out = bed.copy()
        place(out, f, 0.2)
        place(out, f if opt is None else muffled(f, *opt), 3.9)
        out[:k] *= np.linspace(0, 1, k)
        out[-k:] *= np.linspace(1, 0, k)
        demos[name] = out
    peak = max(np.max(np.abs(d)) for d in demos.values())
    return {n: d * 0.89 / max(0.89, peak) for n, d in demos.items()}  # one gain for all, so they compare


# ---------- the page ----------
def data_uri(x):
    with tempfile.TemporaryDirectory() as d:
        w, m = Path(d) / "x.wav", Path(d) / "x.m4a"
        _wav(w, x)
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(w), "-c:a", "aac",
                        "-b:a", "160k", str(m)], check=True)
        return "data:audio/mp4;base64," + base64.b64encode(m.read_bytes()).decode()


def row(tag, line, x):
    return (f'<div class="row"><p><b>{html.escape(tag)}</b> {html.escape(line)}</p>'
            f'<audio controls preload="auto" src="{data_uri(x)}"></audio></div>')


CSS = """
:root{--bg:#f6f4ef;--card:#fff;--ink:#1d1d1b;--soft:#5c5a55;--line:#dedad2;--accent:#a4521c}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#171614;--card:#211f1c;--ink:#ecebe7;
--soft:#a7a49d;--line:#36332e;--accent:#e08a4a}}
:root[data-theme="dark"]{--bg:#171614;--card:#211f1c;--ink:#ecebe7;--soft:#a7a49d;--line:#36332e;--accent:#e08a4a}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.45 system-ui,sans-serif}
main{max-width:640px;margin:0 auto;padding:20px 16px 40px}
h1{font-size:1.4rem;margin:0 0 4px}h2{font-size:1.1rem;margin:28px 0 6px}
.note{color:var(--soft);font-size:.9rem;margin:0 0 10px}
.row{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 12px;margin:8px 0}
.row p{margin:0 0 8px}audio{width:100%}
.rec{border-left:3px solid var(--accent);padding:4px 10px;margin:10px 0}
"""


def main():
    rhino = ROOT / "audio" / "sfx" / "rhino"
    a = pair(load(rhino / "pound_rear.wav"), load(rhino / "pound_slam.wav"))
    b_rear, b_slam = level(steel_rear(np.random.default_rng(21)), REAR_LUFS), level(steel_slam(np.random.default_rng(22)), SLAM_LUFS)
    c_rear, c_slam = level(quake_rear(np.random.default_rng(31)), REAR_LUFS), level(quake_slam(np.random.default_rng(32)), SLAM_LUFS)
    for name, x in (("B rear", b_rear), ("B slam", b_slam), ("C rear", c_rear), ("C slam", c_slam)):
        print(f"{name}: {len(x) / SR:.2f} s, {lufs(x):.1f} LUFS, peak {np.max(np.abs(x)):.2f}")
    mu = muffle_demos()

    body = [
        "<h1>Sound picks</h1>",
        '<p class="note">Two picks, about a minute. All free: synthesised from scratch or built from the game\'s own '
        "sounds. Loudness is matched, so no option wins by being louder. I can't hear audio, so my picks come from "
        "the design; your ears decide.</p>",
        "<h2>1. Rhino ground pound</h2>",
        '<p class="note">Each clip: the rear-up, a beat, then the slam (the slam also ends the stampede).</p>',
        row("A. In the game now:", "servo climb, then thump, crunch, hull clang and rumble.", a),
        row("B. Steel:", "machine first. Hydraulics and a climbing servo, then a deep thump and a big ringing metal clang.",
            pair(b_rear, b_slam)),
        row("C. Quake:", "ground first. Rumble building, then a sharp crack, a heavy boom and gravel raining down, "
            "with a little metal.", pair(c_rear, c_slam)),
        '<p class="rec"><b>My pick: C.</b> The callout is "Ground\'s coming up!", so the earth breaking should lead.</p>',
        "<h2>2. Wall muffling</h2>",
        '<p class="note">Each clip: a tower fight in the open, then the same fight behind a wall, over the lane '
        "ambience.</p>",
        row("None (today):", "a fight behind a wall sounds the same as one in front of you.", mu["None"]),
        row("Light:", "duller and a bit quieter. You still hear it and can place it; it sounds around a corner.",
            mu["Light"]),
        row("Heavy:", "a low thud only. Clearly hidden, but hard to follow a fight you can't see.", mu["Heavy"]),
        '<p class="rec"><b>My pick: Light.</b> A fight behind a wall is still useful to hear; light keeps it readable '
        "and still makes walls matter.</p>",
        "<h2>How to answer</h2>",
        '<p class="note">Something like "pound C, muffle light". If no pound option is good enough, a paid take '
        "(ElevenLabs sound effects) is the next step, priced first. Made by tools/audio/sound_picks.py.</p>",
    ]
    page = ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>Sound Picks</title>"
            f"<style>{CSS}</style></head><body><main>{''.join(body)}</main></body></html>")
    PAGE.parent.mkdir(parents=True, exist_ok=True)
    PAGE.write_text(page, encoding="utf-8")
    print(f"{PAGE}  {PAGE.stat().st_size / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
