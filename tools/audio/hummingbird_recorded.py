"""Hummingbird sounds (2026-11-06): the link needle, the kindred link and the beak shot. Preston: "Yes, hummingbird".

hummingbird_kit.gd (class_name HummingbirdKit) fires cue(name):
  needle_cast  the needle leaves the beak (20 m/s, up to 10 m): a thin glint
  needle_heal  it reaches an ally (heals 10%, links them): the warm, rewarding one
  needle_hit   it reaches an enemy: a light prick, no shake
  needle_miss  nothing or a wall: small and quiet
  link_on      the ruby beam locks onto an ally; link_hum then holds until link_break
  link_break   the beam snaps (range, wall, ally gone, or replaced by a new link)
  beak_shot    the basic attack, a short steel dart, up to once per 0.9 s: light, it repeats all fight
  beak_hit     the dart lands (24 m/s, within about 6.5 m)
  beak_miss    the target was gone when it arrived
link_hum.wav is a seamless 2 s loop with its loop points in a WAV smpl chunk, which Godot's importer reads by default.
Built from the Sonniss GDC 2026 bundle (D:\\dev\\sound-library, never into an AI tool).

  python -I tools/audio/hummingbird_recorded.py             renders two options per sound and the listen page
  python -I tools/audio/hummingbird_recorded.py --install A writes audio/sfx/hummingbird/ with every A
  python -I tools/audio/hummingbird_recorded.py --install A,B,A,A,A,A,B,A,A,A   one letter per sound, in SOUNDS order
"""
import struct
import sys
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import basic_attacks_recorded as ba  # noqa: E402  (brings the wolf, gorilla and fennec sources and helpers)
import gorilla_recorded as g  # noqa: E402
import fennec_portal_recorded as fp  # noqa: E402
from pound_recorded import SR, hp, lp, mix, glue, level, stats, to_int16  # noqa: E402

g.F.update({
    "coil": "344 Audio - East Coast America Vol. 1/AMBSubn_Electricity Hum, Lightbulb,  Coil Pickup 01_344 Audio_East Coast America.wav",
    "reactor": "Epic Stock Media - Strange Game Ambient Loops 3/DSGNSynth_Scifi Loop Ship Reactor Synth Layer Layered Saw Buzz_ESM_SGA3.wav",
})
take, pitch, cut = g.take, fp.pitch, ba.cut
PROJECT = Path(__file__).resolve().parents[2]
GAME = PROJECT / "audio" / "sfx" / "hummingbird"
PAGE = PROJECT / "docs" / "listen" / "hummingbird-2026-11-06.html"
LOOP, XFADE = 2.0, 0.3  # link hum length and its wrap crossfade, seconds


# ---- needle -------------------------------------------------------------------------------------------------------
def cast_a():  # Glint: a glassy snap flicked high, a thin fast swish behind it
    return cut(glue(mix(0.3, (hp(pitch(take("snap", 0, 0.2, 0.2, 0.08), 1.5), 2000), 0.0, 0.8),
                        (hp(pitch(take("swish", 0, 1.0, 0.3, 0.12), 1.8), 3000), 0.01, 0.6)), drive=1.2, fade=0.08), 0.28)


def cast_b():  # Flick: a spring wire flicked off, a little electric tick
    return cut(glue(mix(0.3, (hp(pitch(take("spring", 0, 0.4, 0.25, 0.1), 1.4), 1500), 0.0, 0.8),
                        (hp(take("arc", 0, 0.4, 0.15, 0.06), 2000), 0.0, 0.35)), drive=1.2, fade=0.08), 0.28)


def heal_a():  # Ruby chime: a bright tonal spell note, a high ping on top
    return glue(mix(0.75, (hp(take("bright", 0, 0.5, 0.7, 0.35), 400), 0.0, 1.0),
                    (hp(pitch(take("ping", 0, 0.3, 0.3, 0.12), 1.5), 1500), 0.0, 0.35)), drive=1.1, fade=0.25)


def heal_b():  # Sparkle: a short bright shimmer with a glassy snap at the start
    return glue(mix(0.65, (hp(take("shimmer", 0, 0.5, 0.6, 0.3), 1200), 0.0, 0.9),
                    (hp(pitch(take("snap", 0, 0.2, 0.2, 0.08), 1.2), 1500), 0.0, 0.4)), drive=1.1, fade=0.22)


def hit_a():  # Pierce: a glass snap and a wire tap, a little electric bite
    return glue(mix(0.3, (hp(pitch(take("snap", 0, 0.2, 0.2, 0.08), 1.1), 1200), 0.0, 0.7),
                    (hp(take("spring", 0, 0.4, 0.2, 0.08), 800), 0.0, 0.6),
                    (hp(take("elec", 0, 0.4, 0.2, 0.1), 1000), 0.0, 0.3)), drive=1.3, fade=0.1)


def hit_b():  # Sting: an arc tick and a dry percussive snap, a light smack under it
    return glue(mix(0.3, (hp(take("arc", 0, 0.4, 0.2, 0.08), 800), 0.0, 0.7),
                    (pitch(take("percsnap", 0, 0.4, 0.2, 0.08), 1.3), 0.0, 0.6),
                    (hp(take("punch", 0, 0.4, 0.15, 0.06), 1500), 0.0, 0.3)), drive=1.3, fade=0.1)


def miss_a():  # Ricochet: a high wire tap and a falling ping, as if it glanced off
    return glue(mix(0.4, (hp(pitch(take("spring", 0, 0.4, 0.3, 0.15), 1.6), 2000), 0.0, 0.7),
                    (hp(pitch(take("ping", 0, 0.3, 0.35, 0.15), 1.8), 2500), 0.02, 0.4)), drive=1.1, fade=0.15)


def miss_b():  # Fizzle: the electric tick dies out with a thin sweep
    return glue(mix(0.4, (fp.ramp(hp(take("arc", 0, 0.4, 0.35, 0.2), 1500), 1, 0, 2), 0.0, 0.6),
                    (hp(pitch(take("sweep", 0, 0.5, 0.3, 0.15), 1.4), 2500), 0.0, 0.4)), drive=1.1, fade=0.15)


# ---- link ---------------------------------------------------------------------------------------------------------
def on_a():  # Lock on: an electric power-up rises, a glassy snap locks it
    return glue(mix(0.6, (hp(take("powerup", 0, 1.0, 0.5, 0.2), 200), 0.0, 1.0),
                    (hp(pitch(take("snap", 0, 0.2, 0.2, 0.08), 1.2), 1500), 0.25, 0.5)), drive=1.2, fade=0.15)


def on_b():  # Swell: a reversed shimmer swells into the snap
    return glue(mix(0.65, (hp(take("shimmer", 0, 0.5, 0.45, 0.1, reverse=True), 800), 0.0, 0.7),
                    (hp(pitch(take("snap", 0, 0.2, 0.2, 0.08), 1.2), 1500), 0.42, 0.6)), drive=1.2, fade=0.12)


def break_a():  # Snap: a whip crack and an arc zap, the beam's tone falling away
    return glue(mix(0.45, (hp(take("whip", 0, 0.5, 0.25, 0.1), 600), 0.0, 0.7),
                    (hp(take("arc", 0, 0.4, 0.25, 0.12), 800), 0.0, 0.6),
                    (hp(pitch(take("ping", 0, 0.3, 0.4, 0.2), 0.9), 800), 0.03, 0.4)), drive=1.3, fade=0.15)


def break_b():  # Drop: an electric tick and a fast bass downer, the power going out of it
    return glue(mix(0.55, (hp(take("drop", 0, 0.5, 0.5, 0.25), 150), 0.0, 0.8),
                    (hp(take("arc", 0, 0.4, 0.2, 0.1), 1000), 0.0, 0.5)), drive=1.3, fade=0.18)


def seamless(y, sec=LOOP, x=XFADE):
    """sec seconds of y that loop cleanly: the head is an equal-power crossfade with what follows the cut."""
    n, m = int(sec * SR), int(x * SR)
    t = np.linspace(0, np.pi / 2, m)
    out = y[:n].copy()
    out[:m] = y[:m] * np.sin(t) + y[n:n + m] * np.cos(t)
    return out


def hum_a():  # Coil: a lightbulb coil hum, thinned, with a faint high whine an octave up
    n = LOOP + XFADE + 0.1
    base = hp(lp(fp.seg("coil", 1.0, n, 0.02), 5000), 120)
    whine = hp(pitch(fp.seg("hum", 1.0, 2 * n + 0.2, 0.02), 2.0), 400)[:len(base)]
    return seamless(base + 0.3 * whine)


def hum_b():  # Reactor: a soft sci-fi saw buzz with a slow pulse (12 even pulses per loop, so it wraps cleanly)
    y = seamless(hp(lp(fp.seg("reactor", 1.0, LOOP + XFADE + 0.1, 0.02), 3000), 150))
    t = np.arange(len(y)) / SR
    return y * (0.85 + 0.15 * np.cos(2 * np.pi * 6.0 * t))


# ---- beak shot ----------------------------------------------------------------------------------------------------
def shot_a():  # Steel flick: a dry snap and a very fast high swish
    return cut(glue(mix(0.2, (pitch(take("percsnap", 0, 0.4, 0.15, 0.06), 1.4), 0.0, 0.7),
                        (hp(pitch(take("swish", 0, 1.0, 0.2, 0.08), 2.0), 3000), 0.0, 0.6)), drive=1.2, fade=0.06), 0.16)


def shot_b():  # Air dart: a high swish led by a small latch tick
    return cut(glue(mix(0.2, (hp(pitch(take("swish", 0, 1.0, 0.25, 0.1), 1.6), 2000), 0.0, 0.9),
                        (hp(pitch(take("latch", 0, 0.5, 0.15, 0.06), 1.6), 1500), 0.0, 0.35)), drive=1.2, fade=0.06), 0.18)


def bhit_a():  # Tink: a wire tap on a small metal hit, a glassy edge
    return glue(mix(0.28, (hp(take("spring", 0, 0.4, 0.25, 0.1), 1000), 0.0, 0.8),
                    (hp(take("metal", 0, 0.4, 0.2, 0.1), 600), 0.0, 0.4),
                    (hp(pitch(take("snap", 0, 0.2, 0.15, 0.06), 1.3), 2000), 0.0, 0.3)), drive=1.3, fade=0.1)


def bhit_b():  # Tack: a light smack and a high latch click
    return glue(mix(0.25, (hp(take("punch", 0, 0.4, 0.2, 0.08), 600), 0.0, 0.7),
                    (pitch(take("latch", 0, 0.5, 0.2, 0.08), 1.5), 0.0, 0.6)), drive=1.3, fade=0.1)


def bmiss_a():  # Whiff: the dart's swish trails off
    return cut(fp.ramp(hp(pitch(take("swish", 0, 1.0, 0.3, 0.12), 1.8), 2500), 1, 0, 1.5), 0.25)


def bmiss_b():  # Ping off: a tiny high ping and wire tap, gone
    return glue(mix(0.28, (hp(pitch(take("ping", 0, 0.3, 0.25, 0.12), 2.0), 2500), 0.0, 0.6),
                    (hp(pitch(take("spring", 0, 0.4, 0.2, 0.1), 1.8), 2500), 0.0, 0.4)), drive=1.1, fade=0.1)


SOUNDS = {  # name: (target LUFS, {letter: (title, builder)}, what triggers it)
    "needle_cast": (-21.0, {"A": ("Glint", cast_a), "B": ("Flick", cast_b)}, "the needle leaves the beak"),
    "needle_heal": (-18.0, {"A": ("Ruby chime", heal_a), "B": ("Sparkle", heal_b)}, "it reaches an ally: heals and links"),
    "needle_hit": (-18.0, {"A": ("Pierce", hit_a), "B": ("Sting", hit_b)}, "it reaches an enemy"),
    "needle_miss": (-23.0, {"A": ("Ricochet", miss_a), "B": ("Fizzle", miss_b)}, "nothing, or a wall"),
    "link_on": (-19.0, {"A": ("Lock on", on_a), "B": ("Swell", on_b)}, "the ruby beam locks onto an ally"),
    "link_break": (-18.0, {"A": ("Snap", break_a), "B": ("Drop", break_b)}, "the beam snaps"),
    "link_hum": (-30.0, {"A": ("Coil", hum_a), "B": ("Reactor", hum_b)}, "held while linked: a seamless 2 s loop, quiet"),
    "beak_shot": (-22.0, {"A": ("Steel flick", shot_a), "B": ("Air dart", shot_b)}, "the basic attack, up to once per 0.9 s"),
    "beak_hit": (-19.0, {"A": ("Tink", bhit_a), "B": ("Tack", bhit_b)}, "the dart lands, 0.1 to 0.3 s later"),
    "beak_miss": (-24.0, {"A": ("Whiff", bmiss_a), "B": ("Ping off", bmiss_b)}, "the target was gone"),
}


def lvl(x, target):
    """level() for short sounds: ebur128 needs a 400 ms block, so pad to 0.5 s to measure, then trim back."""
    n = len(x)
    return level(np.concatenate([x, np.zeros(max(0, int(0.5 * SR) - n))]), target)[:n]


def build():
    return {n: {k: lvl(f(), t) for k, (_, f) in opts.items()} for n, (t, opts, _) in SOUNDS.items()}


def norm(x):
    return x / max(1.0, np.max(np.abs(x)) / 0.89)


def needle_fight(b, k):
    """Cast, heal; cast, hit; cast, miss, each with a small pitch nudge as KitAudio plays them."""
    return norm(mix(3.4, (b["needle_cast"][k], 0.0, 1.0), (b["needle_heal"][k], 0.35, 1.0),
                    (pitch(b["needle_cast"][k], 1.02), 1.3, 1.0), (pitch(b["needle_hit"][k], 1.02), 1.55, 1.0),
                    (pitch(b["needle_cast"][k], 0.98), 2.5, 1.0), (b["needle_miss"][k], 3.0, 1.0)))


def link_life(b, k):
    """Lock on, hum for 3 s (the loop wraps once), snap."""
    hum = np.tile(b["link_hum"][k], 2)[:int(3.0 * SR)]
    return norm(mix(4.0, (b["link_on"][k], 0.0, 1.0), (hum, 0.3, 1.0), (b["link_break"][k], 3.3, 1.0)))


def beak_fight(b, k):
    """Three shots 0.9 s apart: hit, hit, miss."""
    return norm(mix(2.6, (b["beak_shot"][k], 0.0, 1.0), (b["beak_hit"][k], 0.2, 1.0),
                    (pitch(b["beak_shot"][k], 1.02), 0.9, 1.0), (pitch(b["beak_hit"][k], 1.02), 1.15, 1.0),
                    (pitch(b["beak_shot"][k], 0.98), 1.8, 1.0), (b["beak_miss"][k], 2.05, 1.0)))


def write_wav(path, x, loop=False):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(to_int16(x).tobytes())
    if loop:  # smpl chunk: one forward loop over the whole file
        smpl = struct.pack("<9I", 0, 0, int(1e9 / SR), 60, 0, 0, 0, 1, 0) + struct.pack("<6I", 0, 0, 0, len(x) - 1, 0, 0)
        with open(path, "r+b") as f:
            f.seek(0, 2)
            f.write(b"smpl" + struct.pack("<I", len(smpl)) + smpl)
            size = f.tell() - 8
            f.seek(4)
            f.write(struct.pack("<I", size))


def page(b):
    parts = ["<h3>In a fight</h3>"]
    for k in "AB":
        parts += [ba.card(f"Needle, all {k}", "cast and heal, cast and hit, cast and miss", needle_fight(b, k)),
                  ba.card(f"Link, all {k}", "lock on, hum 3 s, snap", link_life(b, k)),
                  ba.card(f"Beak shot, all {k}", "three shots 0.9 s apart: hit, hit, miss", beak_fight(b, k))]
    parts.append("<h3>One by one</h3>")
    for n, (_, opts, note) in SOUNDS.items():
        parts += [ba.card(f"{n} {k}: {title}", note, b[n][k]) for k, (title, _) in opts.items()]
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Hummingbird Sounds</title><style>
:root{{--bg:#f6f5f2;--card:#fff;--ink:#1d1d1b;--mute:#66645e;--line:#e2dfd8}}
@media (prefers-color-scheme:dark){{:root{{--bg:#161614;--card:#21211e;--ink:#ecebe6;--mute:#a19f97;--line:#34332e}}}}
body{{background:var(--bg);color:var(--ink);font:16px/1.45 system-ui,sans-serif;margin:0;padding:24px 16px}}
main{{max-width:760px;margin:0 auto}} h1{{font-size:1.5rem;margin:0 0 4px}} h3{{margin:22px 0 8px;font-size:1rem;color:var(--mute)}}
.sub{{color:var(--mute);margin:0 0 20px}} section{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:0 0 12px}}
h2{{font-size:1.05rem;margin:0 0 2px}} p{{margin:0 0 6px}} .lbl{{color:var(--mute);font-size:.85rem}} audio{{width:100%}}
</style></head><body><main><h1>Hummingbird: needle, link, beak shot</h1>
<p class="sub">Small and bright, to read apart from the heavy machines. The heal is the warm one; the beak shot stays tiny
because it repeats all fight. The link hum is a quiet loop that holds while the ruby beam is up. Every A is in the game now
as a placeholder. Pick a letter per sound, or "all A" / "all B".</p>
{''.join(parts)}</main></body></html>"""


def main():
    b = build()
    if "--install" in sys.argv:
        picks = sys.argv[sys.argv.index("--install") + 1].upper().split(",")
        picks = picks if len(picks) == len(SOUNDS) else picks * len(SOUNDS)
        GAME.mkdir(parents=True, exist_ok=True)
        for n, k in zip(SOUNDS, picks):
            write_wav(GAME / f"{n}.wav", b[n][k], loop=(n == "link_hum"))
            print(f"{n} <- {k}  {len(b[n][k]) / SR * 1000:.0f} ms  {stats(b[n][k])}")
        return
    for n, opts in b.items():
        for k, x in opts.items():
            print(n, k, f"{len(x) / SR * 1000:.0f} ms", stats(x))
    PAGE.write_text(page(b), encoding="utf-8")
    print("page", PAGE)


if __name__ == "__main__":
    main()
