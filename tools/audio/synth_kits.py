#!/usr/bin/env python3
"""Ability sounds for the gorilla (folder ape) and the fennec, synthesised (free, local, no samples).

SMITE 2's first rule for ability sound is a sound the instant you press (docs/reference/
moba-audio-synthesis-2026-11-04.md), so every ability gets a cast sound. Where the kit sends an impact on
a later frame (the throw, the landing, the blast), a second sound lands on that frame. KitAudio
(scripts/audio/kit_audio.gd) maps them to the kits' own used(slot) and impact(strength) signals.

  gorilla (size L, heavy):  1 hex shield   shield_wind (cast), shield_up (the throw frame)
                            2 chest beat   chest_hit (every beat's impact)
                            3 bound        bound_leap (cast), bound_land (the landing)
                            4 hex dome     dome_rise (cast), dome_slam (both fists down, the dome up)
  fennec (size S, light):   1 sand kick    kick_wind (cast), kick_sand (the kick frame)
                            2 ear burst    burst_charge (cast), burst_blast (the burst)
                            3 tunnel       dig_in (cast), pop_out (coming up)
                            4 sonic boom   boom_charge (cast, under the ear-fold charge), boom_blast (the blast)

Stand-ins: a better take replaces a file under the same name. Run from the project folder:
python tools/audio/synth_kits.py
"""
from pathlib import Path

import numpy as np

from synth_map import (SR, axis, white, lp, hp, bp, osc, place, ping, burst, finish, thump, servo, hiss,
                       sparks, level, lufs, write_wav)

SFX = Path(__file__).resolve().parents[2] / "audio" / "sfx"


def shimmer(freqs, sec, tau, trem=11.0):
    """The green hex panels: glassy partials with a fast tremble."""
    t = axis(sec)
    x = sum(osc(f, len(t)) / (i + 1) for i, f in enumerate(freqs))
    return x * (0.75 + 0.25 * np.sin(2 * np.pi * trem * t)) * np.minimum(1, t / 0.03) * np.exp(-t / tau)


def hum_up(f0, f1, sec, bright=1200):
    """An energy field powering up: a rising, slightly detuned saw pair."""
    t = axis(sec)
    f = np.linspace(f0, f1, len(t))
    x = osc(f, len(t), "saw") + osc(f * 1.007, len(t), "saw")
    return lp(x, bright) * np.minimum(1, t / (sec * 0.7)) * np.minimum(1, (sec - t) / 0.08)


def whoosh(sec, lo, hi, peak=0.6):
    t = axis(sec)
    env = np.sin(np.pi * np.minimum(1, t / sec / peak * 0.5)) ** 2
    return bp(white(len(t)), lo, hi) * env * np.minimum(1, (sec - t) / 0.1)


# ---------- gorilla ----------
def shield_wind():
    x = np.zeros(int(0.4 * SR))
    place(x, 0.7 * servo(90, 240, 0.35, 1800), 0)
    place(x, 0.4 * ping([700, 1100], [0.06, 0.04], 0.1), 0.3)
    return finish(x, -1.0, 1.5)


def shield_up():
    x = np.zeros(int(1.1 * SR))
    place(x, 0.5 * shimmer([1320, 1980, 2640, 3520], 1.0, 0.45), 0)
    place(x, 0.5 * hum_up(110, 165, 0.6), 0)
    place(x, 0.3 * whoosh(0.4, 600, 4000), 0)
    return finish(x, -1.0, 1.3, fade=0.1)


def chest_hit():
    x = np.zeros(int(0.55 * SR))
    place(x, 0.9 * thump(58, 0.45), 0)
    place(x, 0.45 * ping([170, 265, 390, 610], [0.35, 0.25, 0.15, 0.1], 0.5), 0)
    place(x, 0.3 * burst(0.06, 400, 3000, 0.012), 0)
    return finish(x, -1.0, 1.8)


def bound_leap():
    x = np.zeros(int(0.7 * SR))
    place(x, 0.6 * servo(80, 220, 0.4, 1500), 0)
    place(x, 0.6 * thump(70, 0.3), 0.02)
    place(x, 0.4 * whoosh(0.6, 300, 2500), 0.05)
    return finish(x, -1.0, 1.5)


def bound_land():
    x = np.zeros(int(1.4 * SR))
    place(x, 1.0 * thump(42, 1.0), 0)
    place(x, 0.6 * burst(0.4, 150, 3500, 0.08), 0)
    place(x, 0.3 * ping([210, 340, 520], [0.6, 0.4, 0.25], 1.0), 0)
    place(x, 0.25 * burst(1.0, 900, 5000, 0.3), 0.05)  # debris
    return finish(x, -1.0, 2.0, fade=0.15)


def dome_rise():
    x = np.zeros(int(0.9 * SR))
    place(x, 0.6 * hum_up(70, 140, 0.85, 900), 0)
    place(x, 0.25 * shimmer([880, 1320, 1760], 0.85, 0.6, 7.0), 0.15)
    return finish(x, -1.0, 1.3, fade=0.05)


def dome_slam():
    x = np.zeros(int(2.0 * SR))
    place(x, 1.0 * thump(40, 1.2), 0)
    place(x, 0.5 * burst(0.3, 150, 3000, 0.07), 0)
    place(x, 0.55 * shimmer([660, 990, 1320, 1980, 2640], 1.8, 0.8, 9.0), 0.04)
    t = axis(1.8)
    place(x, 0.25 * osc(55, len(t)) * np.exp(-t / 0.9), 0.04)  # the dome's low hum
    return finish(x, -1.0, 1.6, fade=0.2)


# ---------- fennec ----------
def kick_wind():
    x = np.zeros(int(0.3 * SR))
    place(x, 0.5 * servo(300, 700, 0.18, 3000), 0)
    place(x, 0.4 * bp(white(int(0.2 * SR)), 1500, 6000) * np.exp(-axis(0.2) / 0.06), 0.05)  # paw scrape
    return finish(x, -1.0, 1.4)


def kick_sand():
    n = int(0.6 * SR)
    t = axis(0.6)
    grains = lp((np.abs(white(n)) > 1.6).astype(float), 3000)  # a spray of grains, not a smooth hiss
    x = bp(white(n), 1500, 9000) * (0.4 + grains) * np.minimum(1, t / 0.01) * np.exp(-t / 0.18)
    place(x, 0.4 * thump(120, 0.15), 0)
    return finish(x, -1.0, 1.6)


def burst_charge():
    t = axis(0.4)
    f = np.linspace(800, 2400, len(t))
    x = (osc(f, len(t)) + 0.3 * osc(f * 1.5, len(t))) * np.minimum(1, t / 0.3) * np.minimum(1, (0.4 - t) / 0.04)
    return finish(x, -1.0, 1.2)


def burst_blast():
    t = axis(0.7)
    n = len(t)
    wub = osc(95, n) * (0.5 + 0.5 * np.sin(2 * np.pi * 18 * t)) * np.exp(-t / 0.2)  # the pressure wave
    x = 0.7 * wub + 0.4 * (osc(1000, n) + 0.6 * osc(1500, n)) * np.exp(-t / 0.08)
    place(x, 0.6 * thump(110, 0.4), 0)
    place(x, 0.4 * burst(0.3, 600, 6000, 0.05), 0)
    return finish(x, -1.0, 1.7)


def dig_in():
    x = np.zeros(int(0.75 * SR))
    for k in range(8):  # claws scraping in, fast
        place(x, 0.5 * bp(white(int(0.05 * SR)), 900, 5000) * np.exp(-axis(0.05) / 0.015), k * 0.075)
    place(x, 0.4 * servo(500, 220, 0.6, 1800), 0.05)
    place(x, 0.4 * lp(burst(0.5, 60, 600, 0.15), 500), 0.15)  # sinking into the ground
    return finish(x, -1.0, 1.5, fade=0.08)


def pop_out():
    x = np.zeros(int(0.6 * SR))
    place(x, 0.8 * thump(130, 0.3), 0)
    place(x, 0.5 * burst(0.4, 700, 7000, 0.09), 0)  # dirt thrown up
    place(x, 0.3 * servo(260, 600, 0.2, 2500), 0.05)
    return finish(x, -1.0, 1.6)


def boom_charge():
    t = axis(1.0)
    n = len(t)
    f = np.linspace(400, 1800, n)
    x = (osc(f, n) + 0.4 * osc(f * 0.5, n, "saw")) * (0.7 + 0.3 * np.sin(2 * np.pi * np.linspace(6, 22, n) * t))
    x *= np.minimum(1, t / 0.6) ** 2 * np.minimum(1, (1.0 - t) / 0.05)
    return finish(lp(x, 4000), -1.0, 1.3)


def boom_blast():
    t = axis(1.6)
    n = len(t)
    sweep = osc(1800 * np.exp(-t / 0.25) + 280, n) * np.exp(-t / 0.5)  # the sonic ring falling away
    x = 0.4 * sweep
    place(x, 1.0 * thump(55, 1.0), 0)
    place(x, 0.7 * lp(burst(1.2, 100, 8000, 0.25), 5000), 0)
    place(x, 0.3 * sparks(0.6, 0.2, 2500), 0.02)
    return finish(x, -1.0, 2.0, fade=0.15)


## name -> (folder, function, target LUFS). Casts sit under the landings, which carry the hit.
SOUNDS = {
    "shield_wind": ("ape", shield_wind, -19), "shield_up": ("ape", shield_up, -16),
    "chest_hit": ("ape", chest_hit, -15), "bound_leap": ("ape", bound_leap, -18),
    "bound_land": ("ape", bound_land, -13), "dome_rise": ("ape", dome_rise, -18),
    "dome_slam": ("ape", dome_slam, -13),
    "kick_wind": ("fennec", kick_wind, -20), "kick_sand": ("fennec", kick_sand, -16),
    "burst_charge": ("fennec", burst_charge, -20), "burst_blast": ("fennec", burst_blast, -15),
    "dig_in": ("fennec", dig_in, -18), "pop_out": ("fennec", pop_out, -16),
    "boom_charge": ("fennec", boom_charge, -18), "boom_blast": ("fennec", boom_blast, -13),
}

if __name__ == "__main__":
    for name, (folder, make, target) in SOUNDS.items():
        x = level(make(), target)
        write_wav(SFX / folder / f"{name}.wav", x)
        print(f"audio/sfx/{folder}/{name}.wav  {len(x) / SR:.2f} s  {lufs(x):.1f} LUFS")
