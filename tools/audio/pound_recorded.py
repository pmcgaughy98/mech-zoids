#!/usr/bin/env python3
"""Rhino ground pound built from recorded sounds (Sonniss #GameAudioGDC 2026 bundle), layered locally.

Replaces the synthesised stand-ins from synth_rhino_pound.py once Preston picks an option.
  python tools/audio/pound_recorded.py              render options B, C, D + listen page (game files untouched)
  python tools/audio/pound_recorded.py --install C  write option C to audio/sfx/rhino/pound_rear.wav and pound_slam.wav

Sources live outside the project in D:/dev/sound-library/sonniss-gdc-2026/wav (license v2.0: fine in a commercial
game, no attribution; never pass the raw files on, never put them into any AI tool). Only the finished mixes enter
the project. Needs ffmpeg on PATH (decoding and the EBU R128 loudness meter).
"""
import base64
import html
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000
LIB = Path(r"D:\dev\sound-library\sonniss-gdc-2026\wav")
PROJECT = Path(__file__).resolve().parents[2]
GAME = PROJECT / "audio" / "sfx" / "rhino"
SCRATCH = Path(r"D:\dev\_scratch\sound\pound")
PAGE = PROJECT / "docs" / "listen" / "ground-pound-recorded-2026-11-05.html"
REAR_LUFS, SLAM_LUFS = -18.2, -19.1  # the stand-ins' levels, so no option wins on volume
SLAM_AT = 0.40  # rough gap from cast to the slam frame (ground_pound frame 4), for the in-game-order clip

SRC = {
    "boom": "Federico Soler - Effective Trailer Booms Vol. 2/EffectiveTrailer_Booms_Vol2_075.wav",
    "metal": "The Noisery - Moaning Metal/DSGNImpt_Metal Hit Thud Thump Low Ring Geofon 1_The Noisery_Moaning Metal.wav",
    "body": "344 Audio - Cinematic Fight Vol. 1/FGHTImpt_4 x Punch, Body 02_344 Audio_Cinematic Fight Vol 1.wav",
    "crunch": "InMotionAudio - Sinister Textures 5/GOREMisc_Concrete_MetalPipe02_InMotionAudio_SinisterTextures5.wav",
    "debris": "Cinematic Sound Design - Colossal Impacts/Woosh Debris.wav",
    "ring": "David Dumais Audio - Melee Weapons Sound Effects Pack 2/METLImpt_METAL SWING HIT Weapon Swing To Metallic Body Impact And Resonant Tail 01_DDUMAIS_MWP2.wav",
    "drop": "344 Audio - Bass Drops & Downers Vol. 1/DSGNBass_Bass Drop & Downer Fast 16_344 Audio_Bass Drops & Downers.wav",
    "servo": "Epic Stock Media - Tower Defense Game/ROBTMvmt_Tower Deploy Hitech Robot Motor Dark Thump Servo Whine 04_ESM_TDG.wav",
    "latch": "Epic Stock Media - HD Lock And Mechanism Sound Design Kit/MECHLtch_Click Deep Mechanism Latch Button Nearfield Thunk 02_ESM_HDLM.wav",
}


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def sos(kind, f, order=2):
    return butter(order, f, kind, fs=SR, output="sos")


def lp(x, f, order=2):
    return sosfilt(sos("lowpass", f, order), x)


def hp(x, f, order=2):
    return sosfilt(sos("highpass", f, order), x)


def env(x, ms=5):
    n = int(ms / 1000 * SR)
    return np.sqrt(np.convolve(x ** 2, np.ones(n) / n, "same"))


def onset(x, lo, hi, back=0.3, floor_db=-20):
    """Start of the strongest hit between lo and hi seconds: walk back from its peak to -20 dB."""
    e = env(x)
    a, b = int(lo * SR), min(int(hi * SR), len(x))
    p = a + int(np.argmax(e[a:b]))
    thr = e[p] * 10 ** (floor_db / 20)
    i, stop = p, max(0, p - int(back * SR))
    while i > stop and e[i] > thr:
        i -= 1
    return i


def take(name, lo=0.0, hi=1.0, dur=1.5, fade_out=0.15, back=0.3):
    """One hit from a source file, starting on its transient, peak-normalised."""
    x = load(LIB / SRC[name])
    s = max(0, onset(x, lo, hi, back) - int(0.002 * SR))
    y = x[s:s + int(dur * SR)].copy()
    fi, fo = int(0.002 * SR), int(min(fade_out, dur / 2) * SR)
    y[:fi] *= np.linspace(0, 1, fi)
    y[-fo:] *= np.linspace(1, 0, fo) ** 2
    return y / np.max(np.abs(y))


def mix(dur, *layers):
    out = np.zeros(int(dur * SR))
    for y, at, gain in layers:
        i = int(at * SR)
        n = min(len(y), len(out) - i)
        out[i:i + n] += gain * y[:n]
    return out


def glue(x, drive=1.4, fade=0.12):
    x = x / np.max(np.abs(x))
    x = np.tanh(drive * x) / np.tanh(drive)  # gentle saturation so the layers read as one hit
    n = int(fade * SR)
    x[-n:] *= np.linspace(1, 0, n) ** 2
    return x


def lufs(x):
    with tempfile.TemporaryDirectory(dir=SCRATCH) as d:
        f = Path(d) / "m.wav"
        wavfile.write(f, SR, x.astype(np.float32))
        err = subprocess.run(["ffmpeg", "-nostats", "-i", str(f), "-af", "ebur128", "-f", "null", "-"],
                             capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1])


def level(x, target, ceiling=10 ** (-1 / 20)):
    for _ in range(3):
        x = x * 10 ** ((target - lufs(x)) / 20)
        if np.max(np.abs(x)) > ceiling:  # soft-limit the transient, then re-measure
            x = np.tanh(x / ceiling) * ceiling
    return x


# ---- the options -------------------------------------------------------------------------------------------
def parts():
    return {
        "boom": take("boom", 0.0, 1.2, dur=1.9, fade_out=0.6),
        "metal": take("metal", 0.0, 0.4, dur=1.8, fade_out=0.6),
        "body": take("body", 0.0, 0.7, dur=0.35, fade_out=0.12),
        "crunch": take("crunch", 0.0, 0.44, dur=0.42, fade_out=0.15),
        "debris": take("debris", 0.2, 1.4, dur=1.3, fade_out=0.5),
        "ring": take("ring", 0.25, 0.9, dur=1.6, fade_out=0.6, back=0.08),
        "drop": take("drop", 0.0, 0.6, dur=1.2, fade_out=0.4),
        "servo": take("servo", 0.0, 0.5, dur=0.62, fade_out=0.12, back=0.25),
        "latch": take("latch", 0.0, 0.2, dur=0.3, fade_out=0.1),
    }


def rear(p, servo_lp=9000):
    # the body lifting: robot servo motor; a deep latch releases at the start and locks at the top
    return glue(mix(0.62, (lp(p["servo"], servo_lp), 0.0, 1.0), (p["latch"], 0.0, 0.45),
                    (hp(p["latch"], 300), 0.47, 0.35)), drive=1.2, fade=0.08)


def slam_foundry(p):
    # machine first: the hull rings, a body thud and the concrete crunch on contact, a modest boom under it
    return glue(mix(1.8, (hp(p["metal"], 45), 0.0, 1.0), (hp(p["ring"], 150), 0.0, 0.45), (p["body"], 0.0, 0.6),
                    (hp(p["crunch"], 180), 0.003, 0.55), (lp(p["boom"], 160, 4), 0.0, 0.6),
                    (hp(p["debris"], 500), 0.05, 0.3)))


def slam_quake(p):
    # ground first: the boom and the ground breaking up carry it, the metal sits underneath
    return glue(mix(1.9, (lp(p["boom"], 420), 0.0, 1.0), (hp(p["crunch"], 120), 0.0, 0.75),
                    (hp(p["debris"], 250), 0.04, 0.65), (hp(p["metal"], 80), 0.0, 0.45), (p["body"], 0.0, 0.5)))


def slam_titan(p):
    # both at full size, plus a sub drop under the boom: the heaviest and longest of the three
    return glue(mix(1.9, (lp(p["boom"], 300), 0.0, 1.0), (hp(p["metal"], 50), 0.0, 0.85),
                    (hp(p["ring"], 150), 0.0, 0.35), (p["body"], 0.0, 0.6), (hp(p["crunch"], 150), 0.002, 0.65),
                    (hp(p["debris"], 300), 0.05, 0.5), (lp(p["drop"], 120, 4), 0.0, 0.5)), drive=1.7)


OPTIONS = {
    "B": ("Foundry", "machine first: hull ring, body thud, concrete crunch, light boom", rear, slam_foundry),
    "C": ("Quake", "ground first: trailer boom, crunch and falling debris, metal underneath", rear, slam_quake),
    "D": ("Titan", "both at full size plus a sub drop; heaviest and longest", rear, slam_titan),
}


def to_int16(x):
    return (np.clip(x, -1, 1) * 32767).astype(np.int16)


def wav_b64(x):
    with tempfile.TemporaryDirectory(dir=SCRATCH) as d:
        f = Path(d) / "a.wav"
        wavfile.write(f, SR, to_int16(x))
        return base64.b64encode(f.read_bytes()).decode()


def stats(x):
    spec = np.abs(np.fft.rfft(x))
    low = spec[np.fft.rfftfreq(len(x), 1 / SR) < 150].sum() / spec.sum()
    return f"{len(x) / SR:.2f} s, {lufs(x):.1f} LUFS, peak {20 * np.log10(np.max(np.abs(x))):.1f} dBFS, {low:.0%} under 150 Hz"


def page(rows):
    cards = []
    for key, name, note, pair, r, s in rows:
        cards.append(f"""<section><h2>{key} &middot; {html.escape(name)}</h2><p>{html.escape(note)}</p>
<p class="lbl">In game order (rear, then slam about {SLAM_AT:.2f} s later)</p><audio controls preload="none" src="data:audio/wav;base64,{wav_b64(pair)}"></audio>
<div class="two"><div><p class="lbl">pound_rear &middot; {stats(r)}</p><audio controls preload="none" src="data:audio/wav;base64,{wav_b64(r)}"></audio></div>
<div><p class="lbl">pound_slam &middot; {stats(s)}</p><audio controls preload="none" src="data:audio/wav;base64,{wav_b64(s)}"></audio></div></div></section>""")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Rhino Ground Pound</title><style>
:root{{--bg:#f6f5f2;--card:#fff;--ink:#1d1d1b;--mute:#66645e;--line:#e2dfd8}}
@media (prefers-color-scheme:dark){{:root{{--bg:#161614;--card:#21211e;--ink:#ecebe6;--mute:#a19f97;--line:#34332e}}}}
body{{background:var(--bg);color:var(--ink);font:16px/1.45 system-ui,sans-serif;margin:0;padding:24px 16px}}
main{{max-width:760px;margin:0 auto}} h1{{font-size:1.5rem;margin:0 0 4px}} .sub{{color:var(--mute);margin:0 0 20px}}
section{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px;margin:0 0 14px}}
h2{{font-size:1.1rem;margin:0 0 4px}} p{{margin:0 0 8px}} .lbl{{color:var(--mute);font-size:.85rem;margin:8px 0 4px}}
audio{{width:100%}} .two{{display:grid;grid-template-columns:1fr 1fr;gap:12px}} @media (max-width:560px){{.two{{grid-template-columns:1fr}}}}
</style></head><body><main><h1>Rhino ground pound</h1>
<p class="sub">A is the synthesised stand-in in the game now. B, C and D are layered from recorded sounds (Sonniss GDC 2026 bundle).
All are matched in loudness (rear {REAR_LUFS} LUFS, slam {SLAM_LUFS} LUFS), so none wins by being louder. Pick one letter.</p>
{''.join(cards)}</main></body></html>"""


def main():
    SCRATCH.mkdir(parents=True, exist_ok=True)
    if len(sys.argv) == 3 and sys.argv[1] == "--install":
        key = sys.argv[2].upper()
        p = parts()
        _, _, rf, sf = OPTIONS[key]
        for name, x, target in (("pound_rear.wav", rf(p), REAR_LUFS), ("pound_slam.wav", sf(p), SLAM_LUFS)):
            x = level(x, target)
            wavfile.write(GAME / name, SR, to_int16(x))
            print(f"audio/sfx/rhino/{name}  {stats(x)}")
        return
    p = parts()
    rows = []
    a_rear, a_slam = load(GAME / "pound_rear.wav"), load(GAME / "pound_slam.wav")
    rows.append(("A", "Stand-in (now)", "synthesised, from synth_rhino_pound.py", a_rear, a_slam))
    for key, (name, note, rf, sf) in OPTIONS.items():
        rows.append((key, name, note, level(rf(p), REAR_LUFS), level(sf(p), SLAM_LUFS)))
    out = []
    for key, name, note, r, s in rows:
        pair = mix(SLAM_AT + len(s) / SR, (r, 0.0, 1.0), (s, SLAM_AT, 1.0))
        pair = pair / max(1.0, np.max(np.abs(pair)) / 0.89)
        for tag, x in (("rear", r), ("slam", s)):
            wavfile.write(SCRATCH / f"{key}_{tag}.wav", SR, to_int16(x))
        out.append((key, name, note, pair, r, s))
        print(f"{key} {name}: rear {stats(r)} | slam {stats(s)}")
    PAGE.parent.mkdir(parents=True, exist_ok=True)
    PAGE.write_text(page(out), encoding="utf-8")
    print(f"page: {PAGE} ({PAGE.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
